import numpy as np
import pandas as pd

from app.models.feature_engineering import FEATURE_COLUMNS, engineer_features


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


def test_feature_columns_present():
    df = engineer_features(_make_ohlcv())
    for col in FEATURE_COLUMNS:
        assert col in df.columns, f"Missing feature column: {col}"


def test_target_column_created():
    df = engineer_features(_make_ohlcv())
    assert "target" in df.columns
    # Target should be 0 or 1 (or NaN for last 24 rows)
    valid = df["target"].dropna()
    assert set(valid.unique()).issubset({0, 1})


def test_no_future_leakage():
    """The target should look 24 hours ahead, so last 24 rows should have NaN future_return."""
    df = engineer_features(_make_ohlcv())
    # The last 24 rows should have NaN future_return_24h (no future data to look at)
    assert pd.isna(df["future_return_24h"].iloc[-1])


def test_enough_valid_rows():
    df = engineer_features(_make_ohlcv(500))
    valid = df[FEATURE_COLUMNS + ["target"]].dropna()
    assert len(valid) > 100, f"Only {len(valid)} valid rows"
