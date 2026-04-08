import numpy as np
import pandas as pd
import pytest

from app.models.feature_engineering import engineer_features
from app.models.xgboost_model import XGBoostPredictor


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


def test_xgboost_train_and_predict():
    df = engineer_features(_make_ohlcv(500))
    xgb = XGBoostPredictor()
    metrics = xgb.train(df)

    assert "accuracy" in metrics
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert metrics["train_size"] > 0
    assert metrics["test_size"] > 0

    # Predict
    direction, confidence = xgb.predict(df)
    assert direction in [0, 1]
    assert 0.0 <= confidence <= 1.0


def test_xgboost_predict_without_train():
    xgb = XGBoostPredictor()
    with pytest.raises(RuntimeError, match="not loaded"):
        xgb.predict(pd.DataFrame())


def test_xgboost_save_load(tmp_path, monkeypatch):
    """Test model save and load round-trip."""
    df = engineer_features(_make_ohlcv(500))
    xgb = XGBoostPredictor()
    xgb.train(df)

    # Monkeypatch the artifacts dir
    monkeypatch.setattr("app.models.xgboost_model.ARTIFACTS_DIR", tmp_path)
    xgb.save("TEST")

    xgb2 = XGBoostPredictor()
    monkeypatch.setattr("app.models.xgboost_model.ARTIFACTS_DIR", tmp_path)
    assert xgb2.load("TEST")

    d1, c1 = xgb.predict(df)
    d2, c2 = xgb2.predict(df)
    assert d1 == d2
    assert abs(c1 - c2) < 0.001
