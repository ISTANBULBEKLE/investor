import logging

import httpx

from app.config.symbols import SYMBOL_CONFIG
from app.services.cache import cache

logger = logging.getLogger(__name__)

# Multiple free news sources
COINGECKO_NEWS_URL = "https://api.coingecko.com/api/v3/news"
COINPAPRIKA_NEWS_URL = "https://api.coinpaprika.com/v1/coins/{coin_id}/events"
CRYPTOPANIC_URL = "https://cryptopanic.com/api/free/v1/posts/"


class NewsFetcher:
    """Fetches crypto news headlines for sentiment analysis."""

    async def get_headlines(self, symbol: str, limit: int = 20) -> list[str]:
        """Fetch latest headlines for a symbol. Tries multiple sources."""
        cache_key = f"news:headlines:{symbol}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        headlines: list[str] = []

        # Try CoinGecko news
        headlines = await self._fetch_coingecko_news(symbol, limit)

        # Fallback: CryptoPanic free API
        if not headlines:
            headlines = await self._fetch_cryptopanic(symbol, limit)

        # Last resort: use general crypto market headlines
        if not headlines:
            headlines = await self._fetch_general_crypto_news(limit)

        if headlines:
            await cache.set(cache_key, headlines, ttl=900)  # 15 min cache

        return headlines

    async def _fetch_coingecko_news(self, symbol: str, limit: int) -> list[str]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(COINGECKO_NEWS_URL)
                if resp.status_code != 200:
                    return []
                data = resp.json()

            name = str(SYMBOL_CONFIG.get(symbol, {}).get("name", symbol)).lower()
            sym_lower = symbol.lower()

            headlines = []
            for item in data.get("data", []):
                title = item.get("title", "")
                if sym_lower in title.lower() or name in title.lower():
                    headlines.append(title)
                if len(headlines) >= limit:
                    break
            return headlines
        except Exception as e:
            logger.debug(f"CoinGecko news failed: {e}")
            return []

    async def _fetch_cryptopanic(self, symbol: str, limit: int) -> list[str]:
        """CryptoPanic free API (no auth, limited)."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    CRYPTOPANIC_URL,
                    params={"currencies": symbol, "public": "true"},
                )
                if resp.status_code != 200:
                    return []
                data = resp.json()

            headlines = []
            for item in data.get("results", [])[:limit]:
                title = item.get("title", "")
                if title:
                    headlines.append(title)
            return headlines
        except Exception as e:
            logger.debug(f"CryptoPanic news failed: {e}")
            return []

    async def _fetch_general_crypto_news(self, limit: int) -> list[str]:
        """Fallback: return general crypto market headlines."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(COINGECKO_NEWS_URL)
                if resp.status_code != 200:
                    return []
                data = resp.json()

            headlines = []
            for item in data.get("data", [])[:limit]:
                title = item.get("title", "")
                if title:
                    headlines.append(title)
            return headlines
        except Exception as e:
            logger.debug(f"General news failed: {e}")
            return []


news_fetcher = NewsFetcher()
