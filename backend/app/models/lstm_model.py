import logging
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from app.models.feature_engineering import FEATURE_COLUMNS

logger = logging.getLogger(__name__)

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"
SEQUENCE_LENGTH = 48  # 48 hours of hourly data


class LSTMNetwork(nn.Module):
    def __init__(self, input_size: int, hidden_size: int = 64, num_layers: int = 2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers, batch_first=True, dropout=0.2
        )
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])  # Last timestep
        return torch.sigmoid(out)


class LSTMPredictor:
    def __init__(self) -> None:
        self.model: LSTMNetwork | None = None
        self.feature_means: np.ndarray | None = None
        self.feature_stds: np.ndarray | None = None

    def _prepare_sequences(
        self, X: np.ndarray, y: np.ndarray | None = None
    ) -> tuple[np.ndarray, np.ndarray | None]:
        """Create sequences of SEQUENCE_LENGTH for LSTM input."""
        sequences = []
        targets = []
        for i in range(SEQUENCE_LENGTH, len(X)):
            sequences.append(X[i - SEQUENCE_LENGTH : i])
            if y is not None:
                targets.append(y[i])
        return np.array(sequences), np.array(targets) if y is not None else None

    def _normalize(self, X: np.ndarray, fit: bool = False) -> np.ndarray:
        if fit:
            self.feature_means = np.nanmean(X, axis=0)
            self.feature_stds = np.nanstd(X, axis=0)
            self.feature_stds[self.feature_stds == 0] = 1.0
        X_norm = (X - self.feature_means) / self.feature_stds
        return np.nan_to_num(X_norm, nan=0.0)

    def train(self, df: pd.DataFrame, epochs: int = 30) -> dict:
        """Train LSTM on featured DataFrame."""
        X_all = df[FEATURE_COLUMNS].values.astype(np.float32)
        y_all = df["target"].values.astype(np.float32)

        # Remove rows where target is NaN
        valid = ~np.isnan(y_all) & ~np.isnan(X_all).any(axis=1)
        X_all = X_all[valid]
        y_all = y_all[valid]

        if len(X_all) < SEQUENCE_LENGTH + 100:
            raise ValueError(f"Not enough data: {len(X_all)} rows")

        # Temporal split
        split_idx = int(len(X_all) * 0.8)
        X_train_raw, X_test_raw = X_all[:split_idx], X_all[split_idx:]
        y_train_raw, y_test_raw = y_all[:split_idx], y_all[split_idx:]

        # Normalize using training data
        X_train_norm = self._normalize(X_train_raw, fit=True)
        X_test_norm = self._normalize(X_test_raw)

        # Create sequences
        X_train_seq, y_train_seq = self._prepare_sequences(X_train_norm, y_train_raw)
        X_test_seq, y_test_seq = self._prepare_sequences(X_test_norm, y_test_raw)

        if len(X_train_seq) == 0:
            raise ValueError("Not enough data for sequences")

        # Convert to tensors
        X_train_t = torch.FloatTensor(X_train_seq)
        y_train_t = torch.FloatTensor(y_train_seq).unsqueeze(1)
        X_test_t = torch.FloatTensor(X_test_seq)
        y_test_t = torch.FloatTensor(y_test_seq)

        # Build model
        self.model = LSTMNetwork(input_size=len(FEATURE_COLUMNS))
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        criterion = nn.BCELoss()

        # Training loop
        self.model.train()
        best_loss = float("inf")
        patience_counter = 0

        for epoch in range(epochs):
            optimizer.zero_grad()
            output = self.model(X_train_t)
            loss = criterion(output, y_train_t)
            loss.backward()
            optimizer.step()

            # Early stopping on validation
            if epoch % 5 == 0:
                self.model.eval()
                with torch.no_grad():
                    val_out = self.model(X_test_t).squeeze()
                    val_loss = criterion(val_out, y_test_t).item()
                self.model.train()

                if val_loss < best_loss:
                    best_loss = val_loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                    if patience_counter >= 3:
                        logger.info(f"Early stopping at epoch {epoch}")
                        break

        # Evaluate
        self.model.eval()
        with torch.no_grad():
            preds = self.model(X_test_t).squeeze()
            predicted = (preds > 0.5).float()
            accuracy = (predicted == y_test_t).float().mean().item()

        metrics = {
            "accuracy": round(accuracy, 4),
            "train_size": len(X_train_seq),
            "test_size": len(X_test_seq),
            "epochs_trained": epoch + 1,
        }
        logger.info(f"LSTM trained: accuracy={accuracy:.4f}")
        return metrics

    def predict(self, df: pd.DataFrame) -> tuple[int, float]:
        """Predict direction and confidence using last SEQUENCE_LENGTH rows."""
        if self.model is None or self.feature_means is None:
            raise RuntimeError("Model not loaded")

        X = df[FEATURE_COLUMNS].iloc[-SEQUENCE_LENGTH:].values.astype(np.float32)
        if len(X) < SEQUENCE_LENGTH:
            raise ValueError(f"Need {SEQUENCE_LENGTH} rows, got {len(X)}")

        X_norm = self._normalize(X)
        X_t = torch.FloatTensor(X_norm).unsqueeze(0)

        self.model.eval()
        with torch.no_grad():
            prob_up = self.model(X_t).item()

        direction = 1 if prob_up > 0.5 else 0
        confidence = prob_up if direction == 1 else 1 - prob_up
        return direction, confidence

    def save(self, symbol: str) -> Path:
        if self.model is None:
            raise RuntimeError("No model to save")
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        path = ARTIFACTS_DIR / f"lstm_{symbol.lower()}.pt"
        torch.save(
            {
                "model_state_dict": self.model.state_dict(),
                "feature_means": self.feature_means.tolist(),
                "feature_stds": self.feature_stds.tolist(),
                "input_size": len(FEATURE_COLUMNS),
            },
            path,
        )
        logger.info(f"LSTM model saved to {path}")
        return path

    def load(self, symbol: str) -> bool:
        path = ARTIFACTS_DIR / f"lstm_{symbol.lower()}.pt"
        if not path.exists():
            logger.warning(f"No LSTM model found at {path}")
            return False
        checkpoint = torch.load(path, weights_only=True)
        self.model = LSTMNetwork(input_size=checkpoint["input_size"])
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.feature_means = np.array(checkpoint["feature_means"])
        self.feature_stds = np.array(checkpoint["feature_stds"])
        self.model.eval()
        logger.info(f"LSTM model loaded from {path}")
        return True
