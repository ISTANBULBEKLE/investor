from pydantic import BaseModel

from app.schemas.common import SignalEnum


class TAIndicators(BaseModel):
    rsi_14: float | None = None
    macd_line: float | None = None
    macd_signal: float | None = None
    macd_histogram: float | None = None
    bb_upper: float | None = None
    bb_middle: float | None = None
    bb_lower: float | None = None
    sma_50: float | None = None
    sma_200: float | None = None
    ema_12: float | None = None
    ema_26: float | None = None
    atr_14: float | None = None
    obv: float | None = None
    stoch_rsi_k: float | None = None
    stoch_rsi_d: float | None = None


class TASignal(BaseModel):
    symbol: str
    signal: SignalEnum
    score: float  # -1.0 to +1.0
    indicators: TAIndicators
    reasoning: list[str]
