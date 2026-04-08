import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from app.config.symbols import SYMBOL_CONFIG
from app.schemas.market import OHLCVItem, OHLCVResponse, TickerResponse
from app.services.data_fetcher import binance_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/market", tags=["market"])


def _validate_symbol(symbol: str) -> str:
    symbol = symbol.upper()
    if symbol not in SYMBOL_CONFIG:
        raise HTTPException(status_code=400, detail=f"Unsupported symbol: {symbol}")
    return symbol


@router.get("/{symbol}/price", response_model=TickerResponse)
async def get_price(symbol: str) -> TickerResponse:
    symbol = _validate_symbol(symbol)
    try:
        data = await binance_client.get_current_price(symbol)
        return TickerResponse(
            symbol=data["symbol"],
            price=data["price"],
            price_change_24h=data["price_change_24h"],
            price_change_pct_24h=data["price_change_pct_24h"],
            high_24h=data["high_24h"],
            low_24h=data["low_24h"],
            volume_24h=data["volume_24h"],
            timestamp=datetime.now(timezone.utc),
        )
    except Exception as e:
        logger.error(f"Failed to fetch price for {symbol}: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to fetch price: {e}")


@router.get("/{symbol}/ohlcv", response_model=OHLCVResponse)
async def get_ohlcv(
    symbol: str,
    timeframe: str = Query(default="1h", pattern="^(1h|4h|1d|1w)$"),
    limit: int = Query(default=100, ge=1, le=1000),
) -> OHLCVResponse:
    symbol = _validate_symbol(symbol)
    try:
        raw = await binance_client.get_ohlcv(symbol, interval=timeframe, limit=limit)
        items = [
            OHLCVItem(
                timestamp=datetime.fromisoformat(k["timestamp"]),
                open=k["open"],
                high=k["high"],
                low=k["low"],
                close=k["close"],
                volume=k["volume"],
            )
            for k in raw
        ]
        return OHLCVResponse(symbol=symbol, timeframe=timeframe, data=items)
    except Exception as e:
        logger.error(f"Failed to fetch OHLCV for {symbol}: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to fetch OHLCV: {e}")
