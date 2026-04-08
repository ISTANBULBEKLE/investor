import logging
import time
from datetime import UTC, datetime

from app.config.settings import settings
from app.schemas.signal import AlertTrigger, EnsembleSignal
from app.services.email_templates import SIGNAL_CHANGE_TEMPLATE, SIGNAL_COLORS

logger = logging.getLogger(__name__)

# Rate limiting: track last email sent per symbol
_last_email_sent: dict[str, float] = {}
EMAIL_COOLDOWN_SECONDS = 3600  # 1 hour per symbol


class EmailNotifier:
    """Sends email alerts via Resend."""

    async def send_alert(self, trigger: AlertTrigger, signal: EnsembleSignal) -> bool:
        """Send an alert email. Returns True if sent, False if skipped."""
        if not settings.resend_api_key or not settings.alert_email_to:
            logger.debug("Resend not configured, skipping email")
            return False

        # Rate limit: max 1 email per symbol per hour
        last_sent = _last_email_sent.get(trigger.symbol, 0)
        if time.time() - last_sent < EMAIL_COOLDOWN_SECONDS:
            logger.debug(f"Email rate limited for {trigger.symbol}")
            return False

        try:
            import resend

            resend.api_key = settings.resend_api_key

            # Build email content
            signal_color = SIGNAL_COLORS.get(signal.signal.value, "#f0b90b")
            ta_score = next((f"{c.score:.2f}" for c in signal.components if c.source == "technical" and c.available), "N/A")
            ml_score = next((f"{c.score:.2f}" for c in signal.components if c.source == "ml" and c.available), "N/A")
            sentiment_score = next((f"{c.score:.2f}" for c in signal.components if c.source == "sentiment" and c.available), "N/A")

            html = SIGNAL_CHANGE_TEMPLATE.format(
                symbol=trigger.symbol,
                signal=signal.signal.value,
                signal_color=signal_color,
                confidence=signal.confidence,
                message=trigger.message,
                ta_score=ta_score,
                ml_score=ml_score,
                sentiment_score=sentiment_score,
            )

            resend.Emails.send({
                "from": settings.alert_email_from,
                "to": [settings.alert_email_to],
                "subject": f"INVESTOR: {trigger.symbol} {signal.signal.value} ({trigger.alert_type})",
                "html": html,
            })

            _last_email_sent[trigger.symbol] = time.time()
            logger.info(f"Alert email sent for {trigger.symbol}: {trigger.alert_type}")

            # Log to database
            await self._log_alert(trigger)

            return True

        except Exception as e:
            logger.error(f"Failed to send email for {trigger.symbol}: {e}")
            return False

    async def _log_alert(self, trigger: AlertTrigger) -> None:
        """Store alert in database."""
        try:
            from app.database import async_session
            from app.models.db_models import AlertLog

            async with async_session() as db:
                db.add(AlertLog(
                    symbol=trigger.symbol,
                    alert_type=trigger.alert_type,
                    message=trigger.message,
                    sent_at=datetime.now(UTC),
                    email_sent=True,
                ))
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")


email_notifier = EmailNotifier()
