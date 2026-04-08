from app.schemas.common import SignalEnum
from app.schemas.signal import AlertTrigger, ComponentSignal, EnsembleSignal
from app.services.signal_monitor import SignalMonitor, _last_signals


class TestSignalMonitor:
    def _make_signal(self, symbol: str, signal: SignalEnum, confidence: float = 0.5) -> EnsembleSignal:
        from datetime import datetime, timezone

        return EnsembleSignal(
            symbol=symbol,
            signal=signal,
            confidence=confidence,
            composite_score=0.3 if signal == SignalEnum.BUY else -0.3,
            components=[
                ComponentSignal(source="technical", signal=signal, score=0.3, weight=0.35, available=True),
            ],
            reasoning=["test"],
            timestamp=datetime.now(timezone.utc),
        )

    def test_first_signal_no_change_alert(self):
        _last_signals.clear()
        monitor = SignalMonitor()
        signal = self._make_signal("TEST", SignalEnum.BUY)
        triggers = monitor.check(signal)
        # First signal — no "signal_change" trigger
        assert not any(t.alert_type == "signal_change" for t in triggers)

    def test_signal_change_triggers_alert(self):
        _last_signals.clear()
        monitor = SignalMonitor()
        # First: BUY
        monitor.check(self._make_signal("TEST", SignalEnum.BUY))
        # Second: SELL — should trigger
        triggers = monitor.check(self._make_signal("TEST", SignalEnum.SELL))
        changes = [t for t in triggers if t.alert_type == "signal_change"]
        assert len(changes) == 1
        assert "BUY" in changes[0].message and "SELL" in changes[0].message

    def test_same_signal_no_change(self):
        _last_signals.clear()
        monitor = SignalMonitor()
        monitor.check(self._make_signal("TEST", SignalEnum.BUY))
        triggers = monitor.check(self._make_signal("TEST", SignalEnum.BUY))
        assert not any(t.alert_type == "signal_change" for t in triggers)

    def test_confidence_spike(self):
        _last_signals.clear()
        monitor = SignalMonitor()
        signal = self._make_signal("TEST", SignalEnum.BUY, confidence=0.9)
        triggers = monitor.check(signal)
        spikes = [t for t in triggers if t.alert_type == "confidence_spike"]
        assert len(spikes) == 1

    def test_no_confidence_spike_at_low_confidence(self):
        _last_signals.clear()
        monitor = SignalMonitor()
        signal = self._make_signal("TEST", SignalEnum.HOLD, confidence=0.3)
        triggers = monitor.check(signal)
        assert not any(t.alert_type == "confidence_spike" for t in triggers)


class TestSignalEndpoint:
    def test_signal_endpoint(self, client):
        resp = client.get("/api/signals/BTC")
        assert resp.status_code == 200
        data = resp.json()
        assert data["symbol"] == "BTC"
        assert data["signal"] in ["STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"]
        assert "components" in data
        assert "reasoning" in data
        assert "timestamp" in data

    def test_signal_invalid_symbol(self, client):
        resp = client.get("/api/signals/FAKE")
        assert resp.status_code == 400

    def test_signal_history_empty(self, client):
        resp = client.get("/api/signals/BTC/history")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
