import logging

from app.schemas.sentiment import NewsSentiment, SentimentScore

logger = logging.getLogger(__name__)

_pipeline = None


def _get_pipeline():
    """Lazy-load FinBERT model. ~400MB download on first use, cached after."""
    global _pipeline
    if _pipeline is None:
        logger.info("Loading FinBERT model (first load may download ~400MB)...")
        from transformers import pipeline

        _pipeline = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
            top_k=None,
            device=-1,  # CPU
        )
        logger.info("FinBERT model loaded.")
    return _pipeline


class SentimentAnalyzer:
    def analyze_text(self, text: str) -> SentimentScore:
        """Analyze a single text and return sentiment scores."""
        pipe = _get_pipeline()
        results = pipe(text[:512])[0]  # FinBERT max 512 tokens

        scores = {r["label"]: r["score"] for r in results}
        label = max(scores, key=scores.get)
        return SentimentScore(
            positive=round(scores.get("positive", 0.0), 4),
            negative=round(scores.get("negative", 0.0), 4),
            neutral=round(scores.get("neutral", 0.0), 4),
            label=label,
        )

    def analyze_batch(self, texts: list[str]) -> list[SentimentScore]:
        """Analyze multiple texts efficiently."""
        if not texts:
            return []
        pipe = _get_pipeline()
        truncated = [t[:512] for t in texts]
        results = pipe(truncated)

        scores_list = []
        for result in results:
            scores = {r["label"]: r["score"] for r in result}
            label = max(scores, key=scores.get)
            scores_list.append(
                SentimentScore(
                    positive=round(scores.get("positive", 0.0), 4),
                    negative=round(scores.get("negative", 0.0), 4),
                    neutral=round(scores.get("neutral", 0.0), 4),
                    label=label,
                )
            )
        return scores_list

    def analyze_headlines(self, headlines: list[str]) -> list[NewsSentiment]:
        """Analyze headlines and return paired results."""
        scores = self.analyze_batch(headlines)
        return [
            NewsSentiment(headline=h, score=s) for h, s in zip(headlines, scores)
        ]

    def aggregate_score(self, scores: list[SentimentScore]) -> float:
        """Compute aggregate sentiment score from -1.0 (bearish) to +1.0 (bullish)."""
        if not scores:
            return 0.0
        total = sum(s.positive - s.negative for s in scores)
        return max(-1.0, min(1.0, total / len(scores)))


sentiment_analyzer = SentimentAnalyzer()
