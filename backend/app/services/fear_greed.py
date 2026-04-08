import logging

import httpx

from app.schemas.sentiment import FearGreedData
from app.services.cache import cache

logger = logging.getLogger(__name__)

FEAR_GREED_URL = "https://api.alternative.me/fng/"


class FearGreedService:
    """Fetches the Crypto Fear & Greed Index from alternative.me."""

    async def get_current(self) -> FearGreedData | None:
        cache_key = "fear_greed:current"
        cached = await cache.get(cache_key)
        if cached:
            return FearGreedData(**cached)

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(FEAR_GREED_URL, params={"limit": 1})
                resp.raise_for_status()
                data = resp.json()

            entry = data["data"][0]
            value = int(entry["value"])
            classification = entry["value_classification"]

            # Contrarian signal: extreme fear = bullish, extreme greed = bearish
            if value <= 20:
                signal = 0.8  # Extreme fear → strong buy signal
            elif value <= 35:
                signal = 0.4  # Fear → moderate buy signal
            elif value >= 80:
                signal = -0.8  # Extreme greed → strong sell signal
            elif value >= 65:
                signal = -0.4  # Greed → moderate sell signal
            else:
                signal = 0.0  # Neutral

            result = FearGreedData(
                value=value,
                classification=classification,
                signal_contribution=round(signal, 2),
            )

            await cache.set(cache_key, result.model_dump(), ttl=1800)  # 30 min cache
            return result

        except Exception as e:
            logger.warning(f"Fear & Greed fetch failed: {e}")
            return None


fear_greed_service = FearGreedService()
