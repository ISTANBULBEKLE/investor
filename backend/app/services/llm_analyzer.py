import json
import logging

import httpx

from app.config.settings import settings
from app.schemas.sentiment import LLMAnalysis
from app.services.llm_prompts import SIGNAL_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """Generates narrative analysis using Ollama (local LLM)."""

    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

    async def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def analyze_signals(
        self,
        symbol: str,
        ta_data: dict | None = None,
        ml_data: dict | None = None,
        sentiment_data: dict | None = None,
    ) -> LLMAnalysis | None:
        """Generate narrative analysis from combined signals."""
        if not await self.is_available():
            logger.debug("Ollama not available, skipping LLM analysis")
            return None

        # Build prompt
        prompt = SIGNAL_ANALYSIS_PROMPT.format(
            symbol=symbol,
            ta_signal=_get(ta_data, "signal", "N/A"),
            ta_score=_get(ta_data, "score", "N/A"),
            rsi=_get(ta_data, "indicators.rsi_14", "N/A"),
            macd_hist=_get(ta_data, "indicators.macd_histogram", "N/A"),
            price_vs_sma200=_get(ta_data, "indicators.sma_200", "N/A"),
            ml_signal=_get(ml_data, "signal", "N/A"),
            ml_confidence=_get(ml_data, "confidence", "N/A"),
            xgb_direction=_safe_prediction(ml_data, "xgboost"),
            lstm_direction=_safe_prediction(ml_data, "lstm"),
            sentiment_signal=_get(sentiment_data, "signal", "N/A"),
            sentiment_score=_get(sentiment_data, "score", "N/A"),
            fear_greed=_get(sentiment_data, "fear_greed.value", "N/A"),
            news_score=_get(sentiment_data, "news_score", "N/A"),
        )

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.3, "num_predict": 500},
                    },
                )
                resp.raise_for_status()
                response_text = resp.json().get("response", "")

            return self._parse_response(symbol, response_text)

        except Exception as e:
            logger.warning(f"LLM analysis failed for {symbol}: {e}")
            return None

    def _parse_response(self, symbol: str, text: str) -> LLMAnalysis:
        """Parse JSON response from LLM."""
        # Try to extract JSON from response
        try:
            # Find JSON in response
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(text[start:end])
                return LLMAnalysis(
                    symbol=symbol,
                    summary=data.get("summary", "Analysis unavailable"),
                    action=data.get("action", "HOLD"),
                    confidence=data.get("confidence", "LOW"),
                    key_factors=data.get("key_factors", []),
                )
        except (json.JSONDecodeError, KeyError):
            pass

        # Fallback: use raw text as summary
        return LLMAnalysis(
            symbol=symbol,
            summary=text[:500] if text else "LLM analysis could not be parsed",
            action="HOLD",
            confidence="LOW",
            key_factors=[],
        )


def _get(data: dict | None, path: str, default: str = "N/A") -> str:
    """Safely get a nested value from a dict using dot notation."""
    if data is None:
        return default
    try:
        for key in path.split("."):
            data = data[key]
        return str(data) if data is not None else default
    except (KeyError, TypeError, IndexError):
        return default


def _safe_prediction(ml_data: dict | None, model_name: str) -> str:
    if ml_data is None:
        return "N/A"
    for p in ml_data.get("predictions", []):
        if p.get("model") == model_name:
            return f"{p['direction']} ({p['confidence']:.2f})"
    return "N/A"


llm_analyzer = LLMAnalyzer()
