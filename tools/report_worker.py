"""Scheduled job runner for loot reports and notifications."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from apscheduler.schedulers.blocking import BlockingScheduler  # type: ignore[import-not-found]
except (
    ImportError
):  # pragma: no cover - APScheduler optional until Phase 5 implementation
    BlockingScheduler = None  # type: ignore[assignment]

from tools.generate_loot_report import gather_summary, render_report, write_report
from core.storage import SQLAlchemyStorage, create_session


def run_once(
    period: str, *, user_id: str | None = None, database_url: str | None = None
) -> None:
    """Generate a single report immediately."""

    session = create_session(database_url)
    storage = SQLAlchemyStorage(session)
    summary = gather_summary(storage, period=period, user_id=user_id)
    content = render_report(summary)
    write_report(content, summary, Path("reports"))


def schedule_reports(
    period: str,
    cron: str,
    *,
    user_id: str | None = None,
    database_url: str | None = None,
) -> None:
    """Schedule recurring report generation.

    cron expression parsing requires APScheduler. Until Phase 5, this remains a stub
    demonstrating the intended flow.
    """

    if BlockingScheduler is None:
        raise RuntimeError(
            "APScheduler is not installed. Install it to enable scheduling."
        )

    scheduler = BlockingScheduler()

    def job() -> None:
        run_once(period, user_id=user_id, database_url=database_url)

    scheduler.add_job(job, trigger="cron", **{"cron": cron})  # TODO: parse cron string
    scheduler.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Schedule loot report generation.")
    parser.add_argument("--period", choices=["monthly", "quarterly"], default="monthly")
    parser.add_argument("--user-id", default=None)
    parser.add_argument("--database-url", default=None)
    parser.add_argument(
        "--cron",
        default=None,
        help="Cron expression for scheduling (requires APScheduler)",
    )
    args = parser.parse_args()

    if args.cron:
        schedule_reports(
            args.period, args.cron, user_id=args.user_id, database_url=args.database_url
        )
    else:
        run_once(args.period, user_id=args.user_id, database_url=args.database_url)
