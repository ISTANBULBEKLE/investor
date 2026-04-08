import time
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from app.schemas.common import SignalEnum
from app.schemas.signal import AlertTrigger, ComponentSignal, EnsembleSignal
from app.services.email_notifier import EmailNotifier, _last_email_sent


def _make_trigger(symbol: str = "BTC") -> AlertTrigger:
    return AlertTrigger(
        symbol=symbol,
        alert_type="signal_change",
        message=f"{symbol} signal changed from HOLD to BUY",
        severity="high",
        current_signal=SignalEnum.BUY,
    )


def _make_signal(symbol: str = "BTC") -> EnsembleSignal:
    return EnsembleSignal(
        symbol=symbol,
        signal=SignalEnum.BUY,
        confidence=0.7,
        composite_score=0.35,
        components=[
            ComponentSignal(source="technical", signal=SignalEnum.BUY, score=0.4, weight=0.35, available=True),
            ComponentSignal(source="ml", signal=SignalEnum.BUY, score=0.3, weight=0.30, available=True),
            ComponentSignal(source="sentiment", signal=SignalEnum.STRONG_BUY, score=0.8, weight=0.20, available=True),
        ],
        reasoning=["test"],
        timestamp=datetime.now(timezone.utc),
    )


class TestEmailNotifier:
    @pytest.mark.asyncio
    async def test_skips_when_no_api_key(self):
        notifier = EmailNotifier()
        with patch("app.services.email_notifier.settings") as mock_settings:
            mock_settings.resend_api_key = ""
            mock_settings.alert_email_to = ""
            result = await notifier.send_alert(_make_trigger(), _make_signal())
            assert result is False

    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        _last_email_sent.clear()
        _last_email_sent["BTC"] = time.time()  # Just sent
        notifier = EmailNotifier()
        with patch("app.services.email_notifier.settings") as mock_settings:
            mock_settings.resend_api_key = "test"
            mock_settings.alert_email_to = "test@test.com"
            result = await notifier.send_alert(_make_trigger(), _make_signal())
            assert result is False  # Rate limited

    @pytest.mark.asyncio
    async def test_different_symbol_not_rate_limited(self):
        _last_email_sent.clear()
        _last_email_sent["BTC"] = time.time()
        notifier = EmailNotifier()
        with patch("app.services.email_notifier.settings") as mock_settings:
            mock_settings.resend_api_key = ""  # Will skip due to no API key
            mock_settings.alert_email_to = "test@test.com"
            result = await notifier.send_alert(_make_trigger("ETH"), _make_signal("ETH"))
            assert result is False
