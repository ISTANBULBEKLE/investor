import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config.settings import settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def run_analysis_cycle() -> None:
    """Run a full analysis cycle for all configured symbols."""
    import asyncio

    from app.services.signal_generator import signal_generator
    from app.services.signal_monitor import signal_monitor
    from app.services.email_notifier import email_notifier
    from app.database import async_session
    from app.models.db_models import AnalysisResult

    symbols = settings.default_symbols
    logger.info(f"Starting analysis cycle for {symbols}")

    for symbol in symbols:
        # Small delay between symbols to avoid overwhelming APIs
        await asyncio.sleep(2)
        try:
            # Generate ensemble signal
            result = await signal_generator.generate(symbol)
            logger.info(f"{symbol}: {result.signal.value} (score={result.composite_score:.2f})")

            # Store in DB
            async with async_session() as db:
                db.add(AnalysisResult(
                    symbol=symbol,
                    timestamp=result.timestamp,
                    signal=result.signal.value,
                    confidence=result.confidence,
                    technical_score=next((c.score for c in result.components if c.source == "technical"), None),
                    ml_score=next((c.score for c in result.components if c.source == "ml"), None),
                    sentiment_score=next((c.score for c in result.components if c.source == "sentiment"), None),
                    raw_data={"reasoning": result.reasoning, "composite_score": result.composite_score},
                ))
                await db.commit()

            # Check for alert triggers
            triggers = signal_monitor.check(result)
            if triggers:
                logger.info(f"{symbol}: {len(triggers)} alert(s) triggered")
                for trigger in triggers:
                    await email_notifier.send_alert(trigger, result)

        except Exception as e:
            logger.error(f"Analysis cycle failed for {symbol}: {e}")

    logger.info("Analysis cycle complete")


async def update_prices() -> None:
    """Fetch and cache latest prices for all symbols."""
    from app.services.data_fetcher import binance_client

    for symbol in settings.default_symbols:
        try:
            await binance_client.get_current_price(symbol)
        except Exception as e:
            logger.debug(f"Price update failed for {symbol}: {e}")


def start_scheduler() -> None:
    """Register jobs and start the scheduler."""
    from datetime import datetime, timedelta, timezone

    interval = settings.analysis_interval_minutes

    # Delay first analysis run by 2 minutes to let server warm up
    first_run = datetime.now(timezone.utc) + timedelta(minutes=2)

    scheduler.add_job(
        run_analysis_cycle,
        "interval",
        minutes=interval,
        id="analysis_cycle",
        replace_existing=True,
        next_run_time=first_run,
    )
    scheduler.add_job(
        update_prices,
        "interval",
        minutes=5,
        id="price_update",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(f"Scheduler started: analysis every {interval}min (first run in 2min), prices every 5min")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
