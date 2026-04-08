import asyncio
import logging
from datetime import datetime, timedelta, timezone

import httpx

from app.config.settings import settings
from app.config.symbols import SYMBOL_CONFIG
from app.services.cache import cache

logger = logging.getLogger(__name__)


class BinanceClient:
    """Fetches real-time data from Binance public API (no auth required)."""

    def __init__(self) -> None:
        self.base_url = settings.binance_base_url

    async def get_current_price(self, symbol: str) -> dict:
        cache_key = f"binance:price:{symbol}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        pair = SYMBOL_CONFIG[symbol]["binance"]
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/ticker/24hr", params={"symbol": pair}
            )
            resp.raise_for_status()
            data = resp.json()

        result = {
            "symbol": symbol,
            "price": float(data["lastPrice"]),
            "price_change_24h": float(data["priceChange"]),
            "price_change_pct_24h": float(data["priceChangePercent"]),
            "high_24h": float(data["highPrice"]),
            "low_24h": float(data["lowPrice"]),
            "volume_24h": float(data["volume"]),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await cache.set(cache_key, result, ttl=30)
        return result

    async def get_ohlcv(
        self, symbol: str, interval: str = "1h", limit: int = 100
    ) -> list[dict]:
        cache_key = f"binance:ohlcv:{symbol}:{interval}:{limit}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        pair = SYMBOL_CONFIG[symbol]["binance"]
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/klines",
                params={"symbol": pair, "interval": interval, "limit": limit},
            )
            resp.raise_for_status()
            raw = resp.json()

        result = [
            {
                "timestamp": datetime.fromtimestamp(
                    k[0] / 1000, tz=timezone.utc
                ).isoformat(),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
            }
            for k in raw
        ]
        await cache.set(cache_key, result, ttl=60)
        return result


    async def backfill_ohlcv(
        self, symbol: str, days: int = 365, interval: str = "1h"
    ) -> list[dict]:
        """Fetch historical OHLCV in batches of 1000 candles."""
        pair = SYMBOL_CONFIG[symbol]["binance"]
        all_candles: list[dict] = []
        end_time = int(datetime.now(timezone.utc).timestamp() * 1000)
        start_time = int(
            (datetime.now(timezone.utc) - timedelta(days=days)).timestamp() * 1000
        )

        logger.info(f"Backfilling {symbol} {interval} data for {days} days...")

        async with httpx.AsyncClient(timeout=30.0) as client:
            current_start = start_time
            while current_start < end_time:
                resp = await client.get(
                    f"{self.base_url}/klines",
                    params={
                        "symbol": pair,
                        "interval": interval,
                        "startTime": current_start,
                        "limit": 1000,
                    },
                )
                resp.raise_for_status()
                raw = resp.json()

                if not raw:
                    break

                for k in raw:
                    all_candles.append(
                        {
                            "timestamp": datetime.fromtimestamp(
                                k[0] / 1000, tz=timezone.utc
                            ).isoformat(),
                            "open": float(k[1]),
                            "high": float(k[2]),
                            "low": float(k[3]),
                            "close": float(k[4]),
                            "volume": float(k[5]),
                        }
                    )

                # Move start to after last candle
                current_start = raw[-1][0] + 1
                # Rate limit: stay under Binance limits
                await asyncio.sleep(0.2)

        logger.info(f"Backfilled {len(all_candles)} candles for {symbol}")
        return all_candles


class CoinGeckoClient:
    """Fetches historical data from CoinGecko API."""

    def __init__(self) -> None:
        self.base_url = settings.coingecko_base_url
        self.api_key = settings.coingecko_api_key

    def _headers(self) -> dict:
        headers: dict[str, str] = {}
        if self.api_key:
            headers["x-cg-demo-api-key"] = self.api_key
        return headers

    async def get_market_data(self, symbol: str) -> dict:
        cache_key = f"coingecko:market:{symbol}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        coin_id = SYMBOL_CONFIG[symbol]["coingecko"]
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/coins/{coin_id}",
                params={"localization": "false", "tickers": "false"},
                headers=self._headers(),
            )
            resp.raise_for_status()
            data = resp.json()

        result = {
            "symbol": symbol,
            "name": data.get("name", ""),
            "current_price": data["market_data"]["current_price"]["usd"],
            "market_cap": data["market_data"]["market_cap"]["usd"],
            "total_volume": data["market_data"]["total_volume"]["usd"],
            "price_change_24h": data["market_data"]["price_change_percentage_24h"],
        }
        await cache.set(cache_key, result, ttl=120)
        return result

    async def get_historical_data(
        self, symbol: str, days: int = 365
    ) -> list[dict]:
        cache_key = f"coingecko:history:{symbol}:{days}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        coin_id = SYMBOL_CONFIG[symbol]["coingecko"]
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/coins/{coin_id}/ohlc",
                params={"vs_currency": "usd", "days": days},
                headers=self._headers(),
            )
            resp.raise_for_status()
            raw = resp.json()

        result = [
            {
                "timestamp": datetime.fromtimestamp(
                    k[0] / 1000, tz=timezone.utc
                ).isoformat(),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": 0.0,
            }
            for k in raw
        ]
        await cache.set(cache_key, result, ttl=300)
        return result


# Singleton instances
binance_client = BinanceClient()
coingecko_client = CoinGeckoClient()
