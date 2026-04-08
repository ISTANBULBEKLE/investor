import time
from typing import Any


class InMemoryCache:
    """Simple in-memory cache with TTL. Will be replaced by Upstash Redis in Phase 4."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float]] = {}

    async def get(self, key: str) -> Any | None:
        if key in self._store:
            value, expires_at = self._store[key]
            if time.time() < expires_at:
                return value
            del self._store[key]
        return None

    async def set(self, key: str, value: Any, ttl: int = 60) -> None:
        self._store[key] = (value, time.time() + ttl)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)


cache = InMemoryCache()
