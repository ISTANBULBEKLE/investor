from pydantic import BaseModel

from app.schemas.common import SignalEnum


class MLPrediction(BaseModel):
    model: str
    direction: str  # "UP" or "DOWN"
    confidence: float


class MLSignal(BaseModel):
    symbol: str
    signal: SignalEnum
    score: float
    confidence: float
    predictions: list[MLPrediction]
