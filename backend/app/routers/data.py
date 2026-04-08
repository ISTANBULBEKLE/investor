import logging
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.symbols import SYMBOL_CONFIG
from app.database import get_db
from app.models.db_models import OHLCVData
from app.services.data_fetcher import binance_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/data", tags=["data"])


async def _store_candles(
    symbol: str, candles: list[dict], timeframe: str, source: str
) -> int:
    """Store candles in the database, skipping duplicates."""
    from app.database import async_session

    stored = 0
    async with async_session() as db:
        for c in candles:
            ts = datetime.fromisoformat(c["timestamp"])
            # Check for duplicate
            existing = await db.execute(
                select(OHLCVData.id).where(
                    OHLCVData.symbol == symbol,
                    OHLCVData.timestamp == ts,
                    OHLCVData.timeframe == timeframe,
                )
            )
            if existing.scalar_one_or_none():
                continue

            db.add(
                OHLCVData(
                    symbol=symbol,
                    timestamp=ts,
                    open=c["open"],
                    high=c["high"],
                    low=c["low"],
                    close=c["close"],
                    volume=c["volume"],
                    timeframe=timeframe,
                    source=source,
                )
            )
            stored += 1

            # Batch commit every 500 rows
            if stored % 500 == 0:
                await db.commit()

        await db.commit()
    return stored


async def _run_backfill(symbol: str, days: int, timeframe: str) -> None:
    """Background task to fetch and store historical data."""
    try:
        candles = await binance_client.backfill_ohlcv(symbol, days=days, interval=timeframe)
        stored = await _store_candles(symbol, candles, timeframe, "binance")
        logger.info(f"Backfill complete: {symbol} — {stored} new candles stored")
    except Exception as e:
        logger.error(f"Backfill failed for {symbol}: {e}")


@router.post("/{symbol}/backfill")
async def backfill_data(
    symbol: str,
    background_tasks: BackgroundTasks,
    days: int = Query(default=365, ge=1, le=365),
    timeframe: str = Query(default="1h", pattern="^(1h|4h|1d)$"),
) -> dict:
    symbol = symbol.upper()
    if symbol not in SYMBOL_CONFIG:
        raise HTTPException(status_code=400, detail=f"Unsupported symbol: {symbol}")

    background_tasks.add_task(_run_backfill, symbol, days, timeframe)
    return {"status": "backfill_started", "symbol": symbol, "days": days, "timeframe": timeframe}


@router.get("/{symbol}/ohlcv")
async def get_stored_ohlcv(
    symbol: str,
    db: AsyncSession = Depends(get_db),
    timeframe: str = Query(default="1h", pattern="^(1h|4h|1d)$"),
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=1000, ge=1, le=10000),
) -> dict:
    symbol = symbol.upper()
    if symbol not in SYMBOL_CONFIG:
        raise HTTPException(status_code=400, detail=f"Unsupported symbol: {symbol}")

    from datetime import timedelta

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(OHLCVData)
        .where(
            OHLCVData.symbol == symbol,
            OHLCVData.timeframe == timeframe,
            OHLCVData.timestamp >= cutoff,
        )
        .order_by(OHLCVData.timestamp.asc())
        .limit(limit)
    )
    rows = result.scalars().all()

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "count": len(rows),
        "data": [
            {
                "timestamp": r.timestamp.isoformat(),
                "open": r.open,
                "high": r.high,
                "low": r.low,
                "close": r.close,
                "volume": r.volume,
            }
            for r in rows
        ],
    }


@router.get("/{symbol}/count")
async def get_data_count(
    symbol: str,
    db: AsyncSession = Depends(get_db),
    timeframe: str = Query(default="1h"),
) -> dict:
    symbol = symbol.upper()
    result = await db.execute(
        select(func.count(OHLCVData.id)).where(
            OHLCVData.symbol == symbol,
            OHLCVData.timeframe == timeframe,
        )
    )
    count = result.scalar_one()
    return {"symbol": symbol, "timeframe": timeframe, "count": count}
