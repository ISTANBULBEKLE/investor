import logging
from datetime import datetime, timezone

import pandas as pd

from app.schemas.common import SignalEnum
from app.schemas.signal import ComponentSignal, EnsembleSignal
from app.services.data_fetcher import binance_client
from app.services.llm_analyzer import llm_analyzer
from app.services.ml_predictor import ml_predictor_service
from app.services.sentiment_aggregator import sentiment_aggregator
from app.services.technical_analysis import ta_service

logger = logging.getLogger(__name__)

# Component weights
TA_WEIGHT = 0.35
ML_WEIGHT = 0.30
SENTIMENT_WEIGHT = 0.20
LLM_WEIGHT = 0.15


def _score_to_signal(score: float) -> SignalEnum:
    if score > 0.5:
        return SignalEnum.STRONG_BUY
    elif score > 0.15:
        return SignalEnum.BUY
    elif score < -0.5:
        return SignalEnum.STRONG_SELL
    elif score < -0.15:
        return SignalEnum.SELL
    return SignalEnum.HOLD


class SignalGenerator:
    """Combines all analysis sources into a single ensemble signal."""

    async def generate(self, symbol: str) -> EnsembleSignal:
        components: list[ComponentSignal] = []
        reasoning: list[str] = []
        weighted_score = 0.0
        total_weight = 0.0

        # Fetch OHLCV once for TA and ML
        df = await self._get_ohlcv(symbol)

        # --- Technical Analysis ---
        ta_score, ta_signal = await self._run_ta(symbol, df, components, reasoning)
        if ta_score is not None:
            weighted_score += ta_score * TA_WEIGHT
            total_weight += TA_WEIGHT

        # --- ML Prediction ---
        ml_score, ml_signal = await self._run_ml(symbol, df, components, reasoning)
        if ml_score is not None:
            weighted_score += ml_score * ML_WEIGHT
            total_weight += ML_WEIGHT

        # --- Sentiment ---
        sent_score, _ = await self._run_sentiment(symbol, components, reasoning)
        if sent_score is not None:
            weighted_score += sent_score * SENTIMENT_WEIGHT
            total_weight += SENTIMENT_WEIGHT

        # --- LLM (optional, non-blocking) ---
        llm_score = await self._run_llm(symbol, ta_score, ml_score, sent_score, components, reasoning)
        if llm_score is not None:
            weighted_score += llm_score * LLM_WEIGHT
            total_weight += LLM_WEIGHT

        # --- Compute ensemble ---
        if total_weight > 0:
            composite = weighted_score / total_weight
        else:
            composite = 0.0

        composite = max(-1.0, min(1.0, composite))

        # Safety override: complete TA/ML disagreement → force HOLD
        if ta_signal and ml_signal:
            ta_dir = 1 if ta_signal in (SignalEnum.STRONG_BUY, SignalEnum.BUY) else (-1 if ta_signal in (SignalEnum.STRONG_SELL, SignalEnum.SELL) else 0)
            ml_dir = 1 if ml_signal in (SignalEnum.STRONG_BUY, SignalEnum.BUY) else (-1 if ml_signal in (SignalEnum.STRONG_SELL, SignalEnum.SELL) else 0)
            if ta_dir != 0 and ml_dir != 0 and ta_dir == -ml_dir:
                reasoning.append("SAFETY: TA and ML strongly disagree — forcing HOLD")
                composite = 0.0

        # Confidence boost: all non-LLM sources agree
        non_llm = [c for c in components if c.source != "llm" and c.available]
        if len(non_llm) >= 3:
            directions = set()
            for c in non_llm:
                if c.signal in (SignalEnum.STRONG_BUY, SignalEnum.BUY):
                    directions.add("buy")
                elif c.signal in (SignalEnum.STRONG_SELL, SignalEnum.SELL):
                    directions.add("sell")
            if len(directions) == 1:
                composite *= 1.15
                composite = max(-1.0, min(1.0, composite))
                reasoning.append("BOOST: All analysis sources agree on direction (+15%)")

        signal = _score_to_signal(composite)
        confidence = min(1.0, abs(composite))

        return EnsembleSignal(
            symbol=symbol,
            signal=signal,
            confidence=round(confidence, 4),
            composite_score=round(composite, 4),
            components=components,
            reasoning=reasoning,
            timestamp=datetime.now(timezone.utc),
        )

    async def _get_ohlcv(self, symbol: str) -> pd.DataFrame:
        raw = await binance_client.get_ohlcv(symbol, interval="1h", limit=300)
        df = pd.DataFrame(raw)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)
        return df

    async def _run_ta(self, symbol, df, components, reasoning):
        try:
            result = ta_service.generate_signal(symbol, df)
            components.append(ComponentSignal(
                source="technical", signal=result.signal, score=result.score,
                weight=TA_WEIGHT, available=True,
            ))
            reasoning.append(f"TA: {result.signal.value} (score={result.score:.2f})")
            return result.score, result.signal
        except Exception as e:
            logger.warning(f"TA failed for {symbol}: {e}")
            components.append(ComponentSignal(
                source="technical", signal=SignalEnum.HOLD, score=0.0,
                weight=TA_WEIGHT, available=False,
            ))
            return None, None

    async def _run_ml(self, symbol, df, components, reasoning):
        try:
            if symbol not in ml_predictor_service._xgb_models:
                ml_predictor_service.load_models(symbol)
            if symbol not in ml_predictor_service._xgb_models:
                raise RuntimeError("No trained models")

            result = ml_predictor_service.predict(symbol, df)
            components.append(ComponentSignal(
                source="ml", signal=result.signal, score=result.score,
                weight=ML_WEIGHT, available=True,
            ))
            reasoning.append(f"ML: {result.signal.value} (score={result.score:.2f}, conf={result.confidence:.2f})")
            return result.score, result.signal
        except Exception as e:
            logger.warning(f"ML failed for {symbol}: {e}")
            components.append(ComponentSignal(
                source="ml", signal=SignalEnum.HOLD, score=0.0,
                weight=ML_WEIGHT, available=False,
            ))
            return None, None

    async def _run_sentiment(self, symbol, components, reasoning):
        try:
            result = await sentiment_aggregator.get_sentiment(symbol)
            components.append(ComponentSignal(
                source="sentiment", signal=result.signal, score=result.score,
                weight=SENTIMENT_WEIGHT, available=True,
            ))
            reasoning.append(f"Sentiment: {result.signal.value} (score={result.score:.2f}, sources={result.sources_available})")
            return result.score, None
        except Exception as e:
            logger.warning(f"Sentiment failed for {symbol}: {e}")
            components.append(ComponentSignal(
                source="sentiment", signal=SignalEnum.HOLD, score=0.0,
                weight=SENTIMENT_WEIGHT, available=False,
            ))
            return None, None

    async def _run_llm(self, symbol, ta_score, ml_score, sent_score, components, reasoning):
        try:
            if not await llm_analyzer.is_available():
                components.append(ComponentSignal(
                    source="llm", signal=SignalEnum.HOLD, score=0.0,
                    weight=LLM_WEIGHT, available=False,
                ))
                return None

            result = await llm_analyzer.analyze_signals(symbol)
            if result is None:
                components.append(ComponentSignal(
                    source="llm", signal=SignalEnum.HOLD, score=0.0,
                    weight=LLM_WEIGHT, available=False,
                ))
                return None

            action_map = {"BUY": 0.5, "SELL": -0.5, "HOLD": 0.0}
            score = action_map.get(result.action.upper(), 0.0)
            signal = _score_to_signal(score)

            components.append(ComponentSignal(
                source="llm", signal=signal, score=score,
                weight=LLM_WEIGHT, available=True,
            ))
            reasoning.append(f"LLM: {result.action} — {result.summary[:100]}")
            return score
        except Exception as e:
            logger.warning(f"LLM failed for {symbol}: {e}")
            components.append(ComponentSignal(
                source="llm", signal=SignalEnum.HOLD, score=0.0,
                weight=LLM_WEIGHT, available=False,
            ))
            return None


signal_generator = SignalGenerator()
