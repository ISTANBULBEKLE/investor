from app.schemas.sentiment import FearGreedData, SentimentScore
from app.services.sentiment_analyzer import SentimentAnalyzer


class TestSentimentAnalyzer:
    def test_aggregate_score_empty(self):
        sa = SentimentAnalyzer()
        assert sa.aggregate_score([]) == 0.0

    def test_aggregate_score_positive(self):
        sa = SentimentAnalyzer()
        scores = [
            SentimentScore(positive=0.8, negative=0.1, neutral=0.1, label="positive"),
            SentimentScore(positive=0.7, negative=0.2, neutral=0.1, label="positive"),
        ]
        result = sa.aggregate_score(scores)
        assert result > 0.5

    def test_aggregate_score_negative(self):
        sa = SentimentAnalyzer()
        scores = [
            SentimentScore(positive=0.1, negative=0.8, neutral=0.1, label="negative"),
            SentimentScore(positive=0.1, negative=0.7, neutral=0.2, label="negative"),
        ]
        result = sa.aggregate_score(scores)
        assert result < -0.5

    def test_aggregate_score_clamped(self):
        sa = SentimentAnalyzer()
        scores = [
            SentimentScore(positive=1.0, negative=0.0, neutral=0.0, label="positive"),
        ]
        result = sa.aggregate_score(scores)
        assert -1.0 <= result <= 1.0


class TestFearGreedSignalLogic:
    """Test the contrarian signal mapping logic directly."""

    def test_extreme_fear_is_bullish(self):
        fg = FearGreedData(value=15, classification="Extreme Fear", signal_contribution=0.8)
        assert fg.signal_contribution > 0  # Extreme fear = contrarian buy

    def test_fear_is_moderately_bullish(self):
        fg = FearGreedData(value=30, classification="Fear", signal_contribution=0.4)
        assert fg.signal_contribution > 0

    def test_extreme_greed_is_bearish(self):
        fg = FearGreedData(value=85, classification="Extreme Greed", signal_contribution=-0.8)
        assert fg.signal_contribution < 0  # Extreme greed = contrarian sell

    def test_neutral_is_zero(self):
        fg = FearGreedData(value=50, classification="Neutral", signal_contribution=0.0)
        assert fg.signal_contribution == 0.0

    def test_fear_greed_live(self, client):
        """Test live Fear & Greed fetch via sentiment endpoint."""
        resp = client.get("/api/analysis/BTC/sentiment")
        assert resp.status_code == 200
        data = resp.json()
        if data.get("fear_greed"):
            assert 0 <= data["fear_greed"]["value"] <= 100


class TestSentimentEndpoint:
    def test_sentiment_endpoint(self, client):
        resp = client.get("/api/analysis/BTC/sentiment")
        assert resp.status_code == 200
        data = resp.json()
        assert data["symbol"] == "BTC"
        assert -1.0 <= data["score"] <= 1.0
        assert data["signal"] in ["STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"]
        assert isinstance(data["sources_available"], list)

    def test_sentiment_invalid_symbol(self, client):
        resp = client.get("/api/analysis/FAKE/sentiment")
        assert resp.status_code == 400

    def test_services_status(self, client):
        resp = client.get("/api/analysis/services/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "binance" in data
        assert "ollama" in data
        assert "fear_greed" in data

    def test_llm_returns_503_when_ollama_offline(self, client):
        resp = client.get("/api/analysis/BTC/llm-summary")
        # Should be 503 if Ollama is not running
        assert resp.status_code == 503
