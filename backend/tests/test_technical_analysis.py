import numpy as np
import pandas as pd

from app.services.technical_analysis import TechnicalAnalysisService


def _make_ohlcv(n: int = 300, base_price: float = 50000.0) -> pd.DataFrame:
    """Create synthetic OHLCV data for testing."""
    np.random.seed(42)
    prices = base_price + np.cumsum(np.random.randn(n) * 100)
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=n, freq="h"),
            "open": prices,
            "high": prices + np.abs(np.random.randn(n) * 50),
            "low": prices - np.abs(np.random.randn(n) * 50),
            "close": prices + np.random.randn(n) * 20,
            "volume": np.random.rand(n) * 1000 + 100,
        }
    )


def test_compute_indicators():
    svc = TechnicalAnalysisService()
    df = _make_ohlcv()
    result = svc.compute_indicators(df)

    assert "rsi_14" in result.columns
    assert "macd_line" in result.columns
    assert "bb_upper" in result.columns
    assert "sma_50" in result.columns
    assert "sma_200" in result.columns
    # Last row should have values (enough data)
    assert not np.isnan(result.iloc[-1]["rsi_14"])
    assert not np.isnan(result.iloc[-1]["sma_200"])


def test_generate_signal_returns_valid():
    svc = TechnicalAnalysisService()
    df = _make_ohlcv()
    signal = svc.generate_signal("BTC", df)

    assert signal.symbol == "BTC"
    assert signal.signal in ["STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"]
    assert -1.0 <= signal.score <= 1.0
    assert len(signal.reasoning) > 0
    assert signal.indicators.rsi_14 is not None


def test_signal_with_few_candles():
    svc = TechnicalAnalysisService()
    df = _make_ohlcv(n=50)
    signal = svc.generate_signal("ETH", df)

    # Should still return a signal even with limited data
    assert signal.symbol == "ETH"
    assert signal.signal in ["STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"]
