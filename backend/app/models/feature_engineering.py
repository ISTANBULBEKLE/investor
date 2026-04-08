import numpy as np
import pandas as pd
import pandas_ta as ta


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract ML features from OHLCV data. Returns a new DataFrame with features and target."""
    df = df.copy()
    df = df.sort_values("timestamp").reset_index(drop=True)

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    # --- Price returns ---
    df["return_1h"] = df["close"].pct_change(1)
    df["return_4h"] = df["close"].pct_change(4)
    df["return_24h"] = df["close"].pct_change(24)
    df["return_7d"] = df["close"].pct_change(168)

    # --- Volatility ---
    df["volatility_24h"] = df["return_1h"].rolling(24).std()
    df["volatility_7d"] = df["return_1h"].rolling(168).std()

    # --- Volume features ---
    df["volume_sma_24"] = df["volume"].rolling(24).mean()
    df["volume_ratio"] = df["volume"] / df["volume_sma_24"].replace(0, np.nan)

    # --- Technical indicators ---
    df["rsi_14"] = ta.rsi(df["close"], length=14)

    macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
    if macd is not None:
        df["macd_hist"] = macd.iloc[:, 2]

    bbands = ta.bbands(df["close"], length=20, std=2)
    if bbands is not None:
        df["bb_pct"] = (df["close"] - bbands.iloc[:, 0]) / (
            bbands.iloc[:, 2] - bbands.iloc[:, 0]
        ).replace(0, np.nan)

    df["sma_50"] = ta.sma(df["close"], length=50)
    df["sma_200"] = ta.sma(df["close"], length=200)
    df["price_sma50_ratio"] = df["close"] / df["sma_50"].replace(0, np.nan)
    df["price_sma200_ratio"] = df["close"] / df["sma_200"].replace(0, np.nan)
    df["sma_50_200_ratio"] = df["sma_50"] / df["sma_200"].replace(0, np.nan)

    df["atr_14"] = ta.atr(df["high"], df["low"], df["close"], length=14)
    df["atr_pct"] = df["atr_14"] / df["close"]

    stochrsi = ta.stochrsi(df["close"], length=14)
    if stochrsi is not None:
        df["stoch_rsi_k"] = stochrsi.iloc[:, 0]

    # --- Time features ---
    if pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["hour"] = df["timestamp"].dt.hour
        df["day_of_week"] = df["timestamp"].dt.dayofweek
    else:
        ts = pd.to_datetime(df["timestamp"])
        df["hour"] = ts.dt.hour
        df["day_of_week"] = ts.dt.dayofweek

    # Cyclical encoding
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)

    # --- Target: price direction 24h ahead ---
    df["future_return_24h"] = df["close"].shift(-24) / df["close"] - 1
    df["target"] = (df["future_return_24h"] > 0).astype(int)

    return df


FEATURE_COLUMNS = [
    "return_1h",
    "return_4h",
    "return_24h",
    "return_7d",
    "volatility_24h",
    "volatility_7d",
    "volume_ratio",
    "rsi_14",
    "macd_hist",
    "bb_pct",
    "price_sma50_ratio",
    "price_sma200_ratio",
    "sma_50_200_ratio",
    "atr_pct",
    "stoch_rsi_k",
    "hour_sin",
    "hour_cos",
    "dow_sin",
    "dow_cos",
]
