import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.symbols import SYMBOL_CONFIG
from app.database import get_db
from app.models.db_models import AnalysisResult
from app.schemas.signal import EnsembleSignal
from app.services.signal_generator import signal_generator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/signals", tags=["signals"])


@router.get("/{symbol}", response_model=EnsembleSignal)
async def get_signal(symbol: str, db: AsyncSession = Depends(get_db)) -> EnsembleSignal:
    symbol = symbol.upper()
    if symbol not in SYMBOL_CONFIG:
        raise HTTPException(status_code=400, detail=f"Unsupported symbol: {symbol}")

    try:
        result = await signal_generator.generate(symbol)

        # Store in DB
        db.add(AnalysisResult(
            symbol=symbol,
            timestamp=result.timestamp,
            signal=result.signal.value,
            confidence=result.confidence,
            technical_score=next((c.score for c in result.components if c.source == "technical"), None),
            ml_score=next((c.score for c in result.components if c.source == "ml"), None),
            sentiment_score=next((c.score for c in result.components if c.source == "sentiment"), None),
            raw_data={"reasoning": result.reasoning, "composite_score": result.composite_score},
        ))
        await db.commit()

        return result
    except Exception as e:
        logger.error(f"Signal generation failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Signal generation failed: {e}")


@router.get("/{symbol}/history")
async def get_signal_history(
    symbol: str,
    db: AsyncSession = Depends(get_db),
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=100, ge=1, le=1000),
) -> list[dict]:
    symbol = symbol.upper()
    if symbol not in SYMBOL_CONFIG:
        raise HTTPException(status_code=400, detail=f"Unsupported symbol: {symbol}")

    from datetime import timedelta

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(AnalysisResult)
        .where(AnalysisResult.symbol == symbol, AnalysisResult.timestamp >= cutoff)
        .order_by(AnalysisResult.timestamp.desc())
        .limit(limit)
    )
    rows = result.scalars().all()

    return [
        {
            "symbol": r.symbol,
            "signal": r.signal,
            "confidence": r.confidence,
            "technical_score": r.technical_score,
            "ml_score": r.ml_score,
            "sentiment_score": r.sentiment_score,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
        }
        for r in rows
    ]
