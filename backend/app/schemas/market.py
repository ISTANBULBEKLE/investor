from datetime import datetime

from pydantic import BaseModel


class PriceResponse(BaseModel):
    symbol: str
    price: float
    timestamp: datetime


class TickerResponse(BaseModel):
    symbol: str
    price: float
    price_change_24h: float
    price_change_pct_24h: float
    high_24h: float
    low_24h: float
    volume_24h: float
    timestamp: datetime


class OHLCVItem(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class OHLCVResponse(BaseModel):
    symbol: str
    timeframe: str
    data: list[OHLCVItem]


class MarketOverview(BaseModel):
    symbols: list[TickerResponse]
