from pydantic import BaseModel


class UserSettingsResponse(BaseModel):
    symbols: list[str]
    email: str
    alert_preferences: dict

    model_config = {"from_attributes": True}


class UserSettingsUpdate(BaseModel):
    symbols: list[str] | None = None
    email: str | None = None
    alert_preferences: dict | None = None


class AlertConfig(BaseModel):
    signal_change: bool = True
    rsi_extreme: bool = True
    macd_crossover: bool = True
    price_drop: bool = True
    fear_greed_extreme: bool = True
    confidence_spike: bool = True
    quiet_hours_start: int | None = None
    quiet_hours_end: int | None = None
