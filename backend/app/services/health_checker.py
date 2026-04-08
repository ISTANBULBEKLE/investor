import logging

import httpx

from app.config.settings import settings

logger = logging.getLogger(__name__)


class ServiceHealthChecker:
    """Checks availability of external services."""

    async def check_all(self) -> dict[str, bool]:
        return {
            "binance": await self._check_url(f"{settings.binance_base_url}/ping"),
            "coingecko": await self._check_url(f"{settings.coingecko_base_url}/ping"),
            "ollama": await self._check_url(f"{settings.ollama_base_url}/api/tags"),
            "reddit": bool(settings.reddit_client_id and settings.reddit_client_secret),
            "fear_greed": await self._check_url("https://api.alternative.me/fng/?limit=1"),
        }

    async def _check_url(self, url: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url)
                return resp.status_code == 200
        except Exception:
            return False


health_checker = ServiceHealthChecker()
