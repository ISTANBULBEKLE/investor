import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
from xgboost import XGBClassifier

from app.models.feature_engineering import FEATURE_COLUMNS

logger = logging.getLogger(__name__)

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"


class XGBoostPredictor:
    def __init__(self) -> None:
        self.model: XGBClassifier | None = None

    def train(self, df: pd.DataFrame) -> dict:
        """Train on featured DataFrame. Uses temporal split (no shuffle)."""
        X = df[FEATURE_COLUMNS].copy()
        y = df["target"].copy()

        # Drop rows with NaN in features or target
        mask = X.notna().all(axis=1) & y.notna()
        X = X[mask]
        y = y[mask]

        if len(X) < 100:
            raise ValueError(f"Not enough data to train: {len(X)} rows")

        # Temporal split: 80% train, 20% test (no shuffle!)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        self.model = XGBClassifier(
            max_depth=6,
            n_estimators=200,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            random_state=42,
        )
        self.model.fit(X_train, y_train, verbose=False)

        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, zero_division=0)

        metrics = {
            "accuracy": round(accuracy, 4),
            "f1_score": round(f1, 4),
            "train_size": len(X_train),
            "test_size": len(X_test),
        }
        logger.info(f"XGBoost trained: accuracy={accuracy:.4f}, f1={f1:.4f}")
        return metrics

    def predict(self, df: pd.DataFrame) -> tuple[int, float]:
        """Predict direction and confidence for the latest row."""
        if self.model is None:
            raise RuntimeError("Model not loaded")

        X = df[FEATURE_COLUMNS].iloc[[-1]].copy()
        if X.isna().any(axis=1).iloc[0]:
            # Fill NaN with 0 for prediction (graceful degradation)
            X = X.fillna(0)

        proba = self.model.predict_proba(X)[0]
        direction = int(np.argmax(proba))
        confidence = float(proba[direction])
        return direction, confidence

    def save(self, symbol: str) -> Path:
        if self.model is None:
            raise RuntimeError("No model to save")
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        path = ARTIFACTS_DIR / f"xgboost_{symbol.lower()}.joblib"
        joblib.dump(self.model, path)
        logger.info(f"XGBoost model saved to {path}")
        return path

    def load(self, symbol: str) -> bool:
        path = ARTIFACTS_DIR / f"xgboost_{symbol.lower()}.joblib"
        if not path.exists():
            logger.warning(f"No XGBoost model found at {path}")
            return False
        self.model = joblib.load(path)
        logger.info(f"XGBoost model loaded from {path}")
        return True
