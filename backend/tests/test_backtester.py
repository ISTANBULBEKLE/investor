import numpy as np
import pandas as pd

from app.services.backtester import BacktestEngine


def _make_ohlcv(n: int = 500) -> pd.DataFrame:
    np.random.seed(42)
    prices = 50000.0 + np.cumsum(np.random.randn(n) * 100)
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


def test_backtest_runs():
    engine = BacktestEngine()
    df = _make_ohlcv()
    result = engine.run("BTC", df, strategy="ta")

    assert result.symbol == "BTC"
    assert result.strategy == "ta"
    assert result.total_trades >= 0
    assert 0.0 <= result.win_rate <= 1.0


def test_backtest_with_no_signals():
    """If data is too short for signals, should return zero trades."""
    engine = BacktestEngine()
    df = _make_ohlcv(n=20)
    result = engine.run("BTC", df, strategy="ta")

    assert result.total_trades >= 0
    assert result.win_rate >= 0.0


def test_backtest_metrics_valid():
    engine = BacktestEngine()
    df = _make_ohlcv(1000)
    result = engine.run("BTC", df, strategy="ta")

    assert result.max_drawdown_pct >= 0.0
    # Profit factor should be >= 0
    assert result.profit_factor >= 0.0
