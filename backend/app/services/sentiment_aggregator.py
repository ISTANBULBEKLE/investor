import logging

from app.schemas.common import SignalEnum
from app.schemas.sentiment import CryptoSentiment
from app.services.fear_greed import fear_greed_service
from app.services.news_fetcher import news_fetcher
from app.services.reddit_scraper import reddit_scraper
from app.services.sentiment_analyzer import sentiment_analyzer

logger = logging.getLogger(__name__)

# Weights for combining sentiment sources
NEWS_WEIGHT = 0.4
REDDIT_WEIGHT = 0.3
FEAR_GREED_WEIGHT = 0.3


class SentimentAggregator:
    """Combines multiple sentiment sources into a single score."""

    async def get_sentiment(self, symbol: str) -> CryptoSentiment:
        sources: list[str] = []
        weighted_score = 0.0
        total_weight = 0.0
        news_score_val = None
        reddit_score_val = None
        fg_data = None
        news_sentiments = None

        # --- News sentiment (FinBERT) ---
        try:
            headlines = await news_fetcher.get_headlines(symbol, limit=20)
            if headlines:
                analyzed = sentiment_analyzer.analyze_headlines(headlines)
                scores = [a.score for a in analyzed]
                news_score_val = sentiment_analyzer.aggregate_score(scores)
                weighted_score += news_score_val * NEWS_WEIGHT
                total_weight += NEWS_WEIGHT
                sources.append("news")
                news_sentiments = analyzed[:10]  # Return top 10
                logger.info(f"{symbol} news sentiment: {news_score_val:.4f} ({len(headlines)} headlines)")
        except Exception as e:
            logger.warning(f"News sentiment failed for {symbol}: {e}")

        # --- Reddit sentiment ---
        try:
            posts = await reddit_scraper.get_posts(symbol, limit=25)
            if posts:
                scores = sentiment_analyzer.analyze_batch(posts)
                reddit_score_val = sentiment_analyzer.aggregate_score(scores)
                weighted_score += reddit_score_val * REDDIT_WEIGHT
                total_weight += REDDIT_WEIGHT
                sources.append("reddit")
                logger.info(f"{symbol} reddit sentiment: {reddit_score_val:.4f} ({len(posts)} posts)")
        except Exception as e:
            logger.warning(f"Reddit sentiment failed for {symbol}: {e}")

        # --- Fear & Greed Index ---
        try:
            fg_data = await fear_greed_service.get_current()
            if fg_data:
                weighted_score += fg_data.signal_contribution * FEAR_GREED_WEIGHT
                total_weight += FEAR_GREED_WEIGHT
                sources.append("fear_greed")
                logger.info(f"Fear & Greed: {fg_data.value} ({fg_data.classification})")
        except Exception as e:
            logger.warning(f"Fear & Greed failed: {e}")

        # --- Compute final score ---
        if total_weight > 0:
            final_score = weighted_score / total_weight
        else:
            final_score = 0.0

        final_score = max(-1.0, min(1.0, final_score))

        # Map to signal
        if final_score > 0.4:
            signal = SignalEnum.STRONG_BUY
        elif final_score > 0.15:
            signal = SignalEnum.BUY
        elif final_score < -0.4:
            signal = SignalEnum.STRONG_SELL
        elif final_score < -0.15:
            signal = SignalEnum.SELL
        else:
            signal = SignalEnum.HOLD

        return CryptoSentiment(
            symbol=symbol,
            signal=signal,
            score=round(final_score, 4),
            news_score=round(news_score_val, 4) if news_score_val is not None else None,
            reddit_score=round(reddit_score_val, 4) if reddit_score_val is not None else None,
            fear_greed=fg_data,
            news_headlines=news_sentiments,
            sources_available=sources,
        )


sentiment_aggregator = SentimentAggregator()
