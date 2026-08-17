"""APScheduler skeleton. Jobs call package no-ops and collect no live data."""

from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ripple.config.settings import Settings, get_settings
from ripple.connectors import run_ingest
from ripple.detect import run_backtest, run_detect, run_mature


def register_jobs(scheduler: BackgroundScheduler) -> None:
    """Register scaffold jobs on ``scheduler``.

    Intervals are placeholders. Callbacks are no-ops until later PRs.
    """
    scheduler.add_job(
        run_ingest,
        IntervalTrigger(hours=1),
        id="ingest",
        replace_existing=True,
    )
    scheduler.add_job(
        run_detect,
        IntervalTrigger(minutes=15),
        id="detect",
        replace_existing=True,
    )
    scheduler.add_job(
        run_mature,
        IntervalTrigger(hours=1),
        id="mature",
        replace_existing=True,
    )
    scheduler.add_job(
        run_backtest,
        IntervalTrigger(weeks=1),
        id="backtest",
        replace_existing=True,
    )


def create_scheduler(settings: Settings | None = None) -> BackgroundScheduler:
    """Build a timezone-aware scheduler with scaffold jobs registered.

    The scheduler is not started here so CLI import stays side-effect free.
    """
    cfg = settings or get_settings()
    scheduler = BackgroundScheduler(timezone=cfg.scheduler_timezone)
    register_jobs(scheduler)
    return scheduler
