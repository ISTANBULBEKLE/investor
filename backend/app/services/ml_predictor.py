import logging

import pandas as pd

from app.models.feature_engineering import engineer_features
from app.models.lstm_model import LSTMPredictor
from app.models.xgboost_model import XGBoostPredictor
from app.schemas.common import SignalEnum
from app.schemas.prediction import MLPrediction, MLSignal

logger = logging.getLogger(__name__)

# Weights: XGBoost 0.6, LSTM 0.4
XGBOOST_WEIGHT = 0.6
LSTM_WEIGHT = 0.4


class MLPredictorService:
    def __init__(self) -> None:
        self._xgb_models: dict[str, XGBoostPredictor] = {}
        self._lstm_models: dict[str, LSTMPredictor] = {}

    def load_models(self, symbol: str) -> bool:
        """Load trained models for a symbol. Returns True if at least one loaded."""
        loaded = False

        xgb = XGBoostPredictor()
        if xgb.load(symbol):
            self._xgb_models[symbol] = xgb
            loaded = True

        lstm = LSTMPredictor()
        if lstm.load(symbol):
            self._lstm_models[symbol] = lstm
            loaded = True

        return loaded

    def predict(self, symbol: str, df: pd.DataFrame) -> MLSignal:
        """Run ensemble prediction on featured DataFrame."""
        df = engineer_features(df)
        predictions: list[MLPrediction] = []
        weighted_score = 0.0
        total_weight = 0.0

        # XGBoost prediction
        xgb = self._xgb_models.get(symbol)
        if xgb is not None:
            try:
                direction, confidence = xgb.predict(df)
                dir_str = "UP" if direction == 1 else "DOWN"
                predictions.append(
                    MLPrediction(model="xgboost", direction=dir_str, confidence=round(confidence, 4))
                )
                # Score: +1 for UP, -1 for DOWN, scaled by confidence
                score = (1 if direction == 1 else -1) * confidence
                weighted_score += score * XGBOOST_WEIGHT
                total_weight += XGBOOST_WEIGHT
            except Exception as e:
                logger.error(f"XGBoost prediction failed for {symbol}: {e}")

        # LSTM prediction
        lstm = self._lstm_models.get(symbol)
        if lstm is not None:
            try:
                direction, confidence = lstm.predict(df)
                dir_str = "UP" if direction == 1 else "DOWN"
                predictions.append(
                    MLPrediction(model="lstm", direction=dir_str, confidence=round(confidence, 4))
                )
                score = (1 if direction == 1 else -1) * confidence
                weighted_score += score * LSTM_WEIGHT
                total_weight += LSTM_WEIGHT
            except Exception as e:
                logger.error(f"LSTM prediction failed for {symbol}: {e}")

        # Ensemble score
        if total_weight > 0:
            ensemble_score = weighted_score / total_weight
        else:
            ensemble_score = 0.0

        # Map to signal
        if ensemble_score > 0.3:
            signal = SignalEnum.STRONG_BUY
        elif ensemble_score > 0.1:
            signal = SignalEnum.BUY
        elif ensemble_score < -0.3:
            signal = SignalEnum.STRONG_SELL
        elif ensemble_score < -0.1:
            signal = SignalEnum.SELL
        else:
            signal = SignalEnum.HOLD

        avg_confidence = (
            sum(p.confidence for p in predictions) / len(predictions)
            if predictions
            else 0.0
        )

        return MLSignal(
            symbol=symbol,
            signal=signal,
            score=round(ensemble_score, 4),
            confidence=round(avg_confidence, 4),
            predictions=predictions,
        )


ml_predictor_service = MLPredictorService()
