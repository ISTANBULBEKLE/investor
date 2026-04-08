from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbols: Mapped[dict] = mapped_column(JSON, default=["BTC", "ETH", "HBAR", "IOTA"])
    email: Mapped[str] = mapped_column(String(255), default="")
    alert_preferences: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow
    )


class OHLCVData(Base):
    __tablename__ = "ohlcv_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[float] = mapped_column(Float)
    timeframe: Mapped[str] = mapped_column(String(10), default="1h")
    source: Mapped[str] = mapped_column(String(50), default="binance")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    signal: Mapped[str] = mapped_column(
        Enum("STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL", name="signal_enum")
    )
    confidence: Mapped[float] = mapped_column(Float)
    technical_score: Mapped[float] = mapped_column(Float, nullable=True)
    ml_score: Mapped[float] = mapped_column(Float, nullable=True)
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=True)
    llm_summary: Mapped[str] = mapped_column(Text, nullable=True)
    raw_data: Mapped[dict] = mapped_column(JSON, nullable=True)


class AlertLog(Base):
    __tablename__ = "alert_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    alert_type: Mapped[str] = mapped_column(String(50))
    message: Mapped[str] = mapped_column(Text)
    sent_at: Mapped[datetime] = mapped_column(DateTime)
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False)


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    predicted_signal: Mapped[str] = mapped_column(String(20))
    predicted_at: Mapped[datetime] = mapped_column(DateTime)
    actual_outcome: Mapped[str] = mapped_column(String(10), nullable=True)
    accuracy_score: Mapped[float] = mapped_column(Float, nullable=True)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class Holdings(Base):
    __tablename__ = "holdings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    avg_buy_price: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow
    )
