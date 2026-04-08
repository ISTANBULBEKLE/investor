from pydantic import BaseModel

from app.schemas.common import SignalEnum


class SentimentScore(BaseModel):
    positive: float
    negative: float
    neutral: float
    label: str  # "positive", "negative", "neutral"


class NewsSentiment(BaseModel):
    headline: str
    score: SentimentScore


class FearGreedData(BaseModel):
    value: int  # 0-100
    classification: str  # "Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"
    signal_contribution: float  # -1 to +1


class CryptoSentiment(BaseModel):
    symbol: str
    signal: SignalEnum
    score: float  # -1.0 to +1.0
    news_score: float | None = None
    reddit_score: float | None = None
    fear_greed: FearGreedData | None = None
    news_headlines: list[NewsSentiment] | None = None
    sources_available: list[str]


class LLMAnalysis(BaseModel):
    symbol: str
    summary: str
    action: str
    confidence: str
    key_factors: list[str]
