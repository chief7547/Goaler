"""Scheduled job runner for loot reports and notifications."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from contextlib import suppress
from pathlib import Path
from urllib import error as urllib_error
from urllib import request as urllib_request

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from apscheduler.schedulers.blocking import BlockingScheduler  # type: ignore[import-not-found,import-untyped]
    from apscheduler.triggers.cron import CronTrigger  # type: ignore[import-not-found,import-untyped]
except ImportError:  # pragma: no cover - APScheduler optional until Phase 5 implementation
    BlockingScheduler = None  # type: ignore[assignment]
    CronTrigger = None  # type: ignore[assignment]

from tools.generate_loot_report import (
    compose_growth_story,
    gather_summary,
    render_report,
    write_report,
)
from core.storage import SQLAlchemyStorage, create_session


LOG_PATH = Path("logs/report_worker.log")


def _configure_logging(verbose: bool = False) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    handlers: list[logging.Handler] = [logging.FileHandler(LOG_PATH, encoding="utf-8")]
    if verbose:
        handlers.append(logging.StreamHandler())
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=handlers,
    )


def run_once(
    period: str,
    *,
    user_id: str | None = None,
    database_url: str | None = None,
    output_dir: Path | None = None,
) -> Path | None:
    """Generate a single report immediately and return its path."""

    logging.info(
        "Starting loot report generation | period=%s user_id=%s", period, user_id or "all-users"
    )
    session = create_session(database_url)
    try:
        storage = SQLAlchemyStorage(session)
        summary = gather_summary(storage, period=period, user_id=user_id)
        narrative = compose_growth_story(summary)
        content = render_report(summary)
        report_path = write_report(content, summary, output_dir or Path("reports"))
        logging.info("Report generated at %s", report_path)
        _notify_slack(summary, narrative, report_path)
        return report_path
    except Exception:
        logging.exception("Report generation failed")
        raise
    finally:
        with suppress(Exception):
            session.close()


def schedule_reports(
    period: str,
    cron: str,
    *,
    user_id: str | None = None,
    database_url: str | None = None,
    output_dir: Path | None = None,
) -> None:
    """Schedule recurring report generation using APScheduler."""

    if BlockingScheduler is None or CronTrigger is None:
        raise RuntimeError(
            "APScheduler is not installed. Install it to enable scheduling."
        )

    scheduler = BlockingScheduler()
    trigger = CronTrigger.from_crontab(cron)

    def job() -> None:
        try:
            run_once(
                period,
                user_id=user_id,
                database_url=database_url,
                output_dir=output_dir,
            )
        except Exception:  # pragma: no cover - logged in run_once
            # run_once already logs; leave failure recorded for monitoring
            pass

    scheduler.add_job(
        job,
        trigger=trigger,
        id=f"loot-report-{period}",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
    )
    logging.info(
        "Scheduled %s loot report with cron='%s' (user=%s)", period, cron, user_id or "all-users"
    )
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped by signal")


def _default_database_url() -> str | None:
    return os.getenv("GOALER_DATABASE_URL")


def _notify_slack(summary: dict, narrative: str, report_path: Path) -> None:
    token = os.getenv("SLACK_BOT_TOKEN")
    channel = os.getenv("SLACK_CHANNEL")
    if not token or not channel:
        logging.info("Slack configuration missing; skipping notification")
        return

    loot_counts = summary.get("loot_counts", {})
    if hasattr(loot_counts, "values"):
        total_loot = sum(loot_counts.values())  # type: ignore[arg-type]
    else:
        total_loot = 0
    period_label = summary.get("period", "monthly")

    text = (
        f"[Goaler] {summary.get('user_label', '사용자')}님의 {period_label.title()} 전리품 기록이 업데이트되었습니다.\n"
        f"전리품 횟수: {total_loot}\n"
        f"성장 서사: {narrative}\n"
        f"리포트 경로: {report_path}"
    )

    response_data = _slack_call(
        token,
        "https://slack.com/api/chat.postMessage",
        {"channel": channel, "text": text},
    )

    if response_data and response_data.get("ok"):
        logging.info("Slack notification delivered to %s", channel)
    elif response_data and response_data.get("error") == "not_in_channel":
        logging.error(
            "Slack bot is not a member of %s. Invite the bot or provide a channel ID.",
            channel,
        )


def _slack_call(
    token: str,
    url: str,
    payload: dict,
    *,
    log_errors: bool = True,
) -> dict | None:
    request = urllib_request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {token}",
        },
    )

    try:
        with urllib_request.urlopen(request) as response:  # type: ignore[assignment]
            response_data = json.load(response)
    except urllib_error.URLError as exc:  # pragma: no cover - network edge
        logging.error("Slack request failed: %s", exc)
        return None

    if not response_data.get("ok") and log_errors:
        logging.error("Slack API returned error (%s): %s", url, response_data)
    return response_data


if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Schedule loot report generation.")
    parser.add_argument("--period", choices=["monthly", "quarterly"], default="monthly")
    parser.add_argument("--user-id", default=None)
    parser.add_argument("--database-url", default=None)
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Directory where generated reports are stored",
    )
    parser.add_argument(
        "--cron",
        default=None,
        help="Cron expression for scheduling (requires APScheduler)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Also echo logs to stdout",
    )
    args = parser.parse_args()

    _configure_logging(verbose=args.verbose)

    db_url = args.database_url or _default_database_url()
    output_dir = Path(args.output_dir)

    if args.cron:
        schedule_reports(
            args.period,
            args.cron,
            user_id=args.user_id,
            database_url=db_url,
            output_dir=output_dir,
        )
    else:
        run_once(
            args.period,
            user_id=args.user_id,
            database_url=db_url,
            output_dir=output_dir,
        )
