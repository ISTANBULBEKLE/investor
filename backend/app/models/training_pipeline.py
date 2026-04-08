import asyncio
import logging

import pandas as pd

from app.models.feature_engineering import engineer_features
from app.models.lstm_model import LSTMPredictor
from app.models.xgboost_model import XGBoostPredictor
from app.services.data_fetcher import binance_client

logger = logging.getLogger(__name__)


async def fetch_training_data(symbol: str, days: int = 365) -> pd.DataFrame:
    """Fetch historical data and prepare features."""
    logger.info(f"Fetching {days} days of data for {symbol}...")
    raw = await binance_client.backfill_ohlcv(symbol, days=days, interval="1h")
    df = pd.DataFrame(raw)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    logger.info(f"Engineering features for {len(df)} candles...")
    df = engineer_features(df)
    return df


async def train_models_for_symbol(symbol: str, days: int = 365) -> dict:
    """Train both XGBoost and LSTM models for a symbol."""
    df = await fetch_training_data(symbol, days=days)

    results = {"symbol": symbol}

    # Train XGBoost
    logger.info(f"Training XGBoost for {symbol}...")
    xgb = XGBoostPredictor()
    try:
        xgb_metrics = xgb.train(df)
        xgb.save(symbol)
        results["xgboost"] = xgb_metrics
    except Exception as e:
        logger.error(f"XGBoost training failed: {e}")
        results["xgboost"] = {"error": str(e)}

    # Train LSTM
    logger.info(f"Training LSTM for {symbol}...")
    lstm = LSTMPredictor()
    try:
        lstm_metrics = lstm.train(df)
        lstm.save(symbol)
        results["lstm"] = lstm_metrics
    except Exception as e:
        logger.error(f"LSTM training failed: {e}")
        results["lstm"] = {"error": str(e)}

    return results


async def train_all(symbols: list[str] | None = None, days: int = 365) -> list[dict]:
    """Train models for all configured symbols."""
    if symbols is None:
        from app.config.settings import settings

        symbols = settings.default_symbols

    results = []
    for symbol in symbols:
        result = await train_models_for_symbol(symbol, days=days)
        results.append(result)
    return results
