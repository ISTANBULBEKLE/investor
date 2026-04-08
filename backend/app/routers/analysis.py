import logging

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from app.config.symbols import SYMBOL_CONFIG
from app.schemas.backtest import BacktestConfig, BacktestResult
from app.schemas.prediction import MLSignal
from app.schemas.sentiment import CryptoSentiment, LLMAnalysis
from app.schemas.technical import TASignal
from app.services.backtester import backtest_engine
from app.services.data_fetcher import binance_client
from app.services.health_checker import health_checker
from app.services.llm_analyzer import llm_analyzer
from app.services.ml_predictor import ml_predictor_service
from app.services.sentiment_aggregator import sentiment_aggregator
from app.services.technical_analysis import ta_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


async def _get_ohlcv_df(symbol: str, limit: int = 300) -> pd.DataFrame:
    """Fetch OHLCV data from Binance and return as DataFrame."""
    raw = await binance_client.get_ohlcv(symbol, interval="1h", limit=limit)
    if not raw:
        raise HTTPException(status_code=502, detail="No OHLCV data available")
    df = pd.DataFrame(raw)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    return df


def _validate_symbol(symbol: str) -> str:
    symbol = symbol.upper()
    if symbol not in SYMBOL_CONFIG:
        raise HTTPException(status_code=400, detail=f"Unsupported symbol: {symbol}")
    return symbol


@router.get("/{symbol}/technical", response_model=TASignal)
async def get_technical_analysis(symbol: str) -> TASignal:
    symbol = _validate_symbol(symbol)
    try:
        df = await _get_ohlcv_df(symbol, limit=300)
        return ta_service.generate_signal(symbol, df)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TA failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


@router.get("/{symbol}/ml", response_model=MLSignal)
async def get_ml_prediction(symbol: str) -> MLSignal:
    symbol = _validate_symbol(symbol)

    # Ensure models are loaded
    if symbol not in ml_predictor_service._xgb_models:
        loaded = ml_predictor_service.load_models(symbol)
        if not loaded:
            raise HTTPException(
                status_code=404,
                detail=f"No trained models for {symbol}. Run 'make train-models' first.",
            )

    try:
        df = await _get_ohlcv_df(symbol, limit=300)
        return ml_predictor_service.predict(symbol, df)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ML prediction failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"ML prediction failed: {e}")


@router.post("/backtest", response_model=BacktestResult)
async def run_backtest(config: BacktestConfig) -> BacktestResult:
    symbol = _validate_symbol(config.symbol)
    try:
        raw = await binance_client.backfill_ohlcv(symbol, days=config.days, interval="1h")
        df = pd.DataFrame(raw)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)

        return backtest_engine.run(
            symbol, df, strategy=config.strategy, position_size_pct=config.position_size_pct
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Backtest failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Backtest failed: {e}")


@router.get("/{symbol}/sentiment", response_model=CryptoSentiment)
async def get_sentiment(symbol: str) -> CryptoSentiment:
    symbol = _validate_symbol(symbol)
    try:
        return await sentiment_aggregator.get_sentiment(symbol)
    except Exception as e:
        logger.error(f"Sentiment analysis failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {e}")


@router.get("/{symbol}/llm-summary", response_model=LLMAnalysis)
async def get_llm_summary(symbol: str) -> LLMAnalysis:
    symbol = _validate_symbol(symbol)

    if not await llm_analyzer.is_available():
        raise HTTPException(
            status_code=503,
            detail="Ollama is not running. Start it with: ollama serve",
        )

    # Gather data from other analysis services
    ta_data = None
    ml_data = None
    sentiment_data = None

    try:
        df = await _get_ohlcv_df(symbol, limit=300)
        ta_result = ta_service.generate_signal(symbol, df)
        ta_data = ta_result.model_dump()
    except Exception as e:
        logger.debug(f"TA data unavailable for LLM: {e}")

    try:
        if symbol not in ml_predictor_service._xgb_models:
            ml_predictor_service.load_models(symbol)
        df = await _get_ohlcv_df(symbol, limit=300)
        ml_result = ml_predictor_service.predict(symbol, df)
        ml_data = ml_result.model_dump()
    except Exception as e:
        logger.debug(f"ML data unavailable for LLM: {e}")

    try:
        sent_result = await sentiment_aggregator.get_sentiment(symbol)
        sentiment_data = sent_result.model_dump()
    except Exception as e:
        logger.debug(f"Sentiment data unavailable for LLM: {e}")

    result = await llm_analyzer.analyze_signals(
        symbol, ta_data=ta_data, ml_data=ml_data, sentiment_data=sentiment_data
    )

    if result is None:
        raise HTTPException(status_code=500, detail="LLM analysis failed")

    return result


@router.get("/services/status")
async def get_services_status() -> dict:
    """Check availability of all external analysis services."""
    return await health_checker.check_all()
