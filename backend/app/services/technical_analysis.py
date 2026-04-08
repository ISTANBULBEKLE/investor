import logging

import numpy as np
import pandas as pd
import pandas_ta as ta

from app.schemas.common import SignalEnum
from app.schemas.technical import TAIndicators, TASignal

logger = logging.getLogger(__name__)


class TechnicalAnalysisService:
    """Computes technical indicators and generates buy/sell signals."""

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add all technical indicators to a DataFrame with OHLCV columns."""
        if len(df) < 200:
            logger.warning(f"Only {len(df)} candles — some indicators may be NaN")

        # RSI
        df["rsi_14"] = ta.rsi(df["close"], length=14)

        # MACD
        macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
        if macd is not None:
            df["macd_line"] = macd.iloc[:, 0]
            df["macd_signal"] = macd.iloc[:, 1]
            df["macd_histogram"] = macd.iloc[:, 2]

        # Bollinger Bands
        bbands = ta.bbands(df["close"], length=20, std=2)
        if bbands is not None:
            df["bb_lower"] = bbands.iloc[:, 0]
            df["bb_middle"] = bbands.iloc[:, 1]
            df["bb_upper"] = bbands.iloc[:, 2]

        # Moving Averages
        df["sma_50"] = ta.sma(df["close"], length=50)
        df["sma_200"] = ta.sma(df["close"], length=200)
        df["ema_12"] = ta.ema(df["close"], length=12)
        df["ema_26"] = ta.ema(df["close"], length=26)

        # ATR
        df["atr_14"] = ta.atr(df["high"], df["low"], df["close"], length=14)

        # OBV
        df["obv"] = ta.obv(df["close"], df["volume"])

        # Stochastic RSI
        stochrsi = ta.stochrsi(df["close"], length=14)
        if stochrsi is not None:
            df["stoch_rsi_k"] = stochrsi.iloc[:, 0]
            df["stoch_rsi_d"] = stochrsi.iloc[:, 1]

        return df

    def generate_signal(self, symbol: str, df: pd.DataFrame) -> TASignal:
        """Generate a TA signal from the latest indicators."""
        df = self.compute_indicators(df.copy())
        latest = df.iloc[-1]
        reasoning: list[str] = []
        score = 0.0
        signals_count = 0

        # --- RSI ---
        rsi = latest.get("rsi_14")
        if rsi is not None and not np.isnan(rsi):
            if rsi < 30:
                score += 1.0
                reasoning.append(f"RSI={rsi:.1f} — oversold (bullish)")
            elif rsi < 40:
                score += 0.5
                reasoning.append(f"RSI={rsi:.1f} — approaching oversold")
            elif rsi > 70:
                score -= 1.0
                reasoning.append(f"RSI={rsi:.1f} — overbought (bearish)")
            elif rsi > 60:
                score -= 0.5
                reasoning.append(f"RSI={rsi:.1f} — approaching overbought")
            else:
                reasoning.append(f"RSI={rsi:.1f} — neutral")
            signals_count += 1

        # --- MACD ---
        macd_hist = latest.get("macd_histogram")
        if macd_hist is not None and not np.isnan(macd_hist):
            prev_hist = df.iloc[-2].get("macd_histogram") if len(df) > 1 else None
            if prev_hist is not None and not np.isnan(prev_hist):
                if prev_hist < 0 and macd_hist > 0:
                    score += 1.0
                    reasoning.append("MACD bullish crossover")
                elif prev_hist > 0 and macd_hist < 0:
                    score -= 1.0
                    reasoning.append("MACD bearish crossover")
                elif macd_hist > 0:
                    score += 0.3
                    reasoning.append("MACD histogram positive")
                else:
                    score -= 0.3
                    reasoning.append("MACD histogram negative")
                signals_count += 1

        # --- Bollinger Bands ---
        bb_lower = latest.get("bb_lower")
        bb_upper = latest.get("bb_upper")
        price = latest["close"]
        if bb_lower is not None and not np.isnan(bb_lower):
            if price <= bb_lower:
                score += 0.8
                reasoning.append("Price at/below lower Bollinger Band (bullish)")
            elif price >= bb_upper:
                score -= 0.8
                reasoning.append("Price at/above upper Bollinger Band (bearish)")
            else:
                reasoning.append("Price within Bollinger Bands")
            signals_count += 1

        # --- SMA crossover ---
        sma_50 = latest.get("sma_50")
        sma_200 = latest.get("sma_200")
        if (
            sma_50 is not None
            and sma_200 is not None
            and not np.isnan(sma_50)
            and not np.isnan(sma_200)
        ):
            if sma_50 > sma_200:
                score += 0.5
                reasoning.append("SMA50 > SMA200 (golden cross territory)")
            else:
                score -= 0.5
                reasoning.append("SMA50 < SMA200 (death cross territory)")
            signals_count += 1

        # --- Price vs SMA200 ---
        if sma_200 is not None and not np.isnan(sma_200):
            if price > sma_200:
                score += 0.3
                reasoning.append("Price above SMA200 (uptrend)")
            else:
                score -= 0.3
                reasoning.append("Price below SMA200 (downtrend)")
            signals_count += 1

        # Normalize score to -1.0 to 1.0
        if signals_count > 0:
            normalized_score = max(-1.0, min(1.0, score / signals_count))
        else:
            normalized_score = 0.0

        # Map score to signal
        if normalized_score > 0.5:
            signal = SignalEnum.STRONG_BUY
        elif normalized_score > 0.15:
            signal = SignalEnum.BUY
        elif normalized_score < -0.5:
            signal = SignalEnum.STRONG_SELL
        elif normalized_score < -0.15:
            signal = SignalEnum.SELL
        else:
            signal = SignalEnum.HOLD

        indicators = TAIndicators(
            rsi_14=_safe_float(latest.get("rsi_14")),
            macd_line=_safe_float(latest.get("macd_line")),
            macd_signal=_safe_float(latest.get("macd_signal")),
            macd_histogram=_safe_float(latest.get("macd_histogram")),
            bb_upper=_safe_float(latest.get("bb_upper")),
            bb_middle=_safe_float(latest.get("bb_middle")),
            bb_lower=_safe_float(latest.get("bb_lower")),
            sma_50=_safe_float(latest.get("sma_50")),
            sma_200=_safe_float(latest.get("sma_200")),
            ema_12=_safe_float(latest.get("ema_12")),
            ema_26=_safe_float(latest.get("ema_26")),
            atr_14=_safe_float(latest.get("atr_14")),
            obv=_safe_float(latest.get("obv")),
            stoch_rsi_k=_safe_float(latest.get("stoch_rsi_k")),
            stoch_rsi_d=_safe_float(latest.get("stoch_rsi_d")),
        )

        return TASignal(
            symbol=symbol,
            signal=signal,
            score=round(normalized_score, 4),
            indicators=indicators,
            reasoning=reasoning,
        )


def _safe_float(val: object) -> float | None:
    if val is None:
        return None
    try:
        f = float(val)
        return None if np.isnan(f) else round(f, 6)
    except (ValueError, TypeError):
        return None


ta_service = TechnicalAnalysisService()
