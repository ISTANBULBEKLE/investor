from enum import Enum

from pydantic import BaseModel


class SignalEnum(str, Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


class TimeframeEnum(str, Enum):
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"


class HealthResponse(BaseModel):
    status: str
    database: str
    uptime_seconds: float
