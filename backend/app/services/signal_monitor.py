import logging

from app.schemas.common import SignalEnum
from app.schemas.signal import AlertTrigger, EnsembleSignal

logger = logging.getLogger(__name__)

# Track last known signals per symbol
_last_signals: dict[str, SignalEnum] = {}


class SignalMonitor:
    """Detects alert-worthy changes between signal cycles."""

    def check(self, signal: EnsembleSignal) -> list[AlertTrigger]:
        triggers: list[AlertTrigger] = []
        symbol = signal.symbol

        # --- Signal direction change ---
        prev = _last_signals.get(symbol)
        if prev is not None and prev != signal.signal:
            if signal.signal != SignalEnum.HOLD and prev != SignalEnum.HOLD:
                severity = "high"
            else:
                severity = "medium"
            triggers.append(AlertTrigger(
                symbol=symbol,
                alert_type="signal_change",
                message=f"{symbol} signal changed from {prev.value} to {signal.signal.value}",
                severity=severity,
                current_signal=signal.signal,
            ))

        _last_signals[symbol] = signal.signal

        # --- Confidence spike ---
        if signal.confidence > 0.8:
            triggers.append(AlertTrigger(
                symbol=symbol,
                alert_type="confidence_spike",
                message=f"{symbol} confidence spike: {signal.confidence:.0%}",
                severity="medium",
                current_signal=signal.signal,
            ))

        # --- Check component-level alerts ---
        for comp in signal.components:
            if not comp.available:
                continue

            # RSI extreme (from TA reasoning)
            if comp.source == "technical":
                for reason in signal.reasoning:
                    if "RSI=" in reason and "oversold" in reason:
                        triggers.append(AlertTrigger(
                            symbol=symbol,
                            alert_type="rsi_extreme",
                            message=f"{symbol}: {reason}",
                            severity="medium",
                            current_signal=signal.signal,
                        ))
                        break
                    elif "RSI=" in reason and "overbought" in reason:
                        triggers.append(AlertTrigger(
                            symbol=symbol,
                            alert_type="rsi_extreme",
                            message=f"{symbol}: {reason}",
                            severity="medium",
                            current_signal=signal.signal,
                        ))
                        break

                for reason in signal.reasoning:
                    if "MACD bullish crossover" in reason:
                        triggers.append(AlertTrigger(
                            symbol=symbol,
                            alert_type="macd_crossover",
                            message=f"{symbol}: MACD bullish crossover detected",
                            severity="medium",
                            current_signal=signal.signal,
                        ))
                        break
                    elif "MACD bearish crossover" in reason:
                        triggers.append(AlertTrigger(
                            symbol=symbol,
                            alert_type="macd_crossover",
                            message=f"{symbol}: MACD bearish crossover detected",
                            severity="medium",
                            current_signal=signal.signal,
                        ))
                        break

            # Fear & Greed extreme
            if comp.source == "sentiment":
                for reason in signal.reasoning:
                    if "Extreme Fear" in reason or "Extreme Greed" in reason:
                        triggers.append(AlertTrigger(
                            symbol=symbol,
                            alert_type="fear_greed_extreme",
                            message=f"{symbol}: {reason}",
                            severity="low",
                            current_signal=signal.signal,
                        ))
                        break

        return triggers


signal_monitor = SignalMonitor()
