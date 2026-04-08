import logging

from app.config.settings import settings
from app.config.symbols import SYMBOL_CONFIG
from app.services.cache import cache

logger = logging.getLogger(__name__)


class RedditSentimentScraper:
    """Fetches crypto sentiment from Reddit via PRAW."""

    def __init__(self) -> None:
        self._reddit = None

    def _get_reddit(self):
        if self._reddit is None:
            if not settings.reddit_client_id or not settings.reddit_client_secret:
                return None
            import praw

            self._reddit = praw.Reddit(
                client_id=settings.reddit_client_id,
                client_secret=settings.reddit_client_secret,
                user_agent=settings.reddit_user_agent,
            )
        return self._reddit

    async def get_posts(self, symbol: str, limit: int = 25) -> list[str]:
        """Fetch post titles from relevant subreddits."""
        cache_key = f"reddit:posts:{symbol}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        reddit = self._get_reddit()
        if reddit is None:
            logger.debug("Reddit credentials not configured, skipping")
            return []

        config = SYMBOL_CONFIG.get(symbol, {})
        subreddits = config.get("subreddits", ["cryptocurrency"])
        name = str(config.get("name", symbol)).lower()
        sym_lower = symbol.lower()

        posts: list[str] = []
        try:
            for sub_name in subreddits:
                subreddit = reddit.subreddit(sub_name)
                for post in subreddit.hot(limit=50):
                    title = post.title
                    text = f"{title} {(post.selftext or '')[:200]}"
                    # Filter for symbol relevance
                    if sym_lower in title.lower() or name in title.lower():
                        posts.append(text.strip())
                    if len(posts) >= limit:
                        break
                if len(posts) >= limit:
                    break

            await cache.set(cache_key, posts, ttl=900)  # 15 min cache
        except Exception as e:
            logger.warning(f"Reddit scrape failed for {symbol}: {e}")

        return posts


reddit_scraper = RedditSentimentScraper()
