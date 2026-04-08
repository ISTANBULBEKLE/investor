from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import SignalEnum


class ComponentSignal(BaseModel):
    source: str  # "technical", "ml", "sentiment", "llm"
    signal: SignalEnum
    score: float
    weight: float
    available: bool


class EnsembleSignal(BaseModel):
    symbol: str
    signal: SignalEnum
    confidence: float
    composite_score: float
    components: list[ComponentSignal]
    reasoning: list[str]
    timestamp: datetime


class AlertTrigger(BaseModel):
    symbol: str
    alert_type: str  # "signal_change", "rsi_extreme", "macd_crossover", "price_drop", "fear_greed_extreme", "confidence_spike"
    message: str
    severity: str  # "high", "medium", "low"
    current_signal: SignalEnum
