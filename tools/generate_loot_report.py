#!/usr/bin/env python3
"""Generate monthly/quarterly loot reports based on stored quest logs."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

from sqlalchemy import select

from core.storage import SQLAlchemyStorage, create_session
from core.models import BossStage, Goal, QuestLog

DEFAULT_OUTPUT_DIR = Path("reports")
DEFAULT_USAGE_LOG = Path("logs/llm_usage.log")


def compute_window(
    period: str, *, now: datetime | None = None
) -> tuple[datetime, datetime]:
    now = now or datetime.now(timezone.utc)
    if period == "monthly":
        start = now - timedelta(days=30)
    elif period == "quarterly":
        start = now - timedelta(days=90)
    else:
        raise ValueError(f"Unsupported period: {period}")
    return start, now


def summarize_usage(log_path: Path, start: datetime) -> dict[str, Any]:
    if not log_path.exists():
        return {}
    total_prompt = 0
    total_completion = 0
    total_requests = 0
    with log_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            timestamp = record.get("timestamp")
            try:
                logged_at = datetime.fromisoformat(timestamp)
            except Exception:  # pragma: no cover - defensive
                continue
            if logged_at.tzinfo is None:
                logged_at = logged_at.replace(tzinfo=timezone.utc)
            if logged_at < start:
                continue
            total_prompt += record.get("prompt_tokens", 0) or 0
            total_completion += record.get("completion_tokens", 0) or 0
            total_requests += 1
    if total_requests == 0:
        return {}
    return {
        "total_requests": total_requests,
        "prompt_tokens": total_prompt,
        "completion_tokens": total_completion,
    }


def gather_summary(
    storage: SQLAlchemyStorage,
    *,
    period: str,
    user_id: str | None = None,
    now: datetime | None = None,
    usage_log: Path | None = None,
) -> dict[str, Any]:
    start, end = compute_window(period, now=now)

    logs_stmt = select(QuestLog, Goal).join(Goal, Goal.goal_id == QuestLog.goal_id)
    if user_id:
        logs_stmt = logs_stmt.where(Goal.user_id == user_id)
    logs_stmt = logs_stmt.where(QuestLog.occurred_at >= start).where(
        QuestLog.occurred_at <= end
    )
    quest_logs = storage.session.execute(logs_stmt).all()

    loot_counts: Counter[str] = Counter()
    energy_counts: Counter[str] = Counter()
    loot_samples: dict[str, list[str]] = {}
    recent_quotes: list[str] = []

    for log, goal in quest_logs:
        loot_type = log.loot_type or "UNSPECIFIED"
        loot_counts[loot_type] += 1
        energy_counts[log.energy_status or "UNKNOWN"] += 1
        if log.mood_note:
            loot_samples.setdefault(loot_type, []).append(log.mood_note)
            recent_quotes.append(log.mood_note)

    recent_quotes = recent_quotes[-3:]

    goal_ids = {goal.goal_id for _, goal in quest_logs}
    boss_stmt = select(BossStage).where(BossStage.goal_id.in_(goal_ids))
    boss_rows: Iterable[BossStage] = storage.session.scalars(boss_stmt)

    boss_completed = []
    boss_in_progress = []
    boss_next = []
    for stage in boss_rows:
        if stage.status == "COMPLETED":
            boss_completed.append(stage.title)
        elif stage.status in {"READY", "IN_PROGRESS"}:
            boss_in_progress.append(stage.title)
        else:
            boss_next.append(stage.title)

    usage_summary = summarize_usage(usage_log or DEFAULT_USAGE_LOG, start)

    return {
        "period": period,
        "start": start,
        "end": end,
        "generated_at": (now or datetime.utcnow()).isoformat(),
        "user_label": user_id or "all-users",
        "loot_counts": loot_counts,
        "loot_samples": loot_samples,
        "recent_quotes": recent_quotes,
        "energy_counts": energy_counts,
        "boss_completed": boss_completed,
        "boss_in_progress": boss_in_progress,
        "boss_next": boss_next,
        "usage_summary": usage_summary,
    }


def _build_table(header: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(header) + " |"]
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def render_report(summary: dict[str, Any]) -> str:
    period_label = summary["period"].title()
    loot_counts: Counter = summary["loot_counts"]
    energy_counts: Counter = summary["energy_counts"]
    loot_samples: dict[str, list[str]] = summary["loot_samples"]

    loot_rows = []
    for loot_type in ["ACHIEVEMENT", "INSIGHT", "EMOTION"]:
        count = loot_counts.get(loot_type, 0)
        sample_list = loot_samples.get(loot_type, [])
        sample = sample_list[-1] if sample_list else "-"
        loot_rows.append([loot_type, str(count), sample])
    loot_table = _build_table(["유형", "획득 횟수", "대표 문장"], loot_rows)

    energy_rows = []
    for key in ["READY_FOR_BOSS", "KEEPING_PACE", "NEEDS_POTION"]:
        energy_rows.append([key or "UNKNOWN", str(energy_counts.get(key, 0))])
    energy_table = _build_table(["경고 레벨", "발생 횟수"], energy_rows)

    recent_quotes = summary["recent_quotes"] or [
        "이번 기간에는 전리품 기록이 아직 없어요."
    ]
    quote_block = "\n> ".join([""] + recent_quotes)

    boss_completed = ", ".join(summary["boss_completed"]) or "없음"
    boss_in_progress = ", ".join(summary["boss_in_progress"]) or "없음"
    boss_next = ", ".join(summary["boss_next"]) or "없음"

    usage_summary = summary["usage_summary"]
    if usage_summary:
        usage_text = (
            f"모델 호출 {usage_summary['total_requests']}회, "
            f"프롬프트 {usage_summary['prompt_tokens']} tokens, 응답 {usage_summary['completion_tokens']} tokens"
        )
    else:
        usage_text = "최근 기간 동안 LLM 사용 기록이 없습니다."

    lines = [
        f"# {period_label} Loot Chronicle — {summary['user_label']}",
        f"생성 시각: {summary['generated_at']}",
        "",
        "## 1. 모험 요약",
        f"- 기간: {summary['start'].date()} ~ {summary['end'].date()}",
        f"- 전리품 기록 횟수: {sum(loot_counts.values())}",
        f"- 에너지 경고 감지: NEEDS_POTION {energy_counts.get('NEEDS_POTION', 0)}회",
        "",
        "## 2. 전리품 요약",
        loot_table,
        "",
        "### 대표 전리품",
        quote_block,
        "",
        "## 3. 보스전 진행도",
        f"- 완료: {boss_completed}",
        f"- 진행 중: {boss_in_progress}",
        f"- 다음 준비: {boss_next}",
        "",
        "## 4. 에너지 & 회복 상태",
        energy_table,
        "",
        "## 5. LLM 사용량",
        usage_text,
    ]
    return "\n".join(lines)


def write_report(content: str, summary: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{summary['user_label']}-{summary['period']}-{summary['end'].date()}.md"
    path = output_dir / filename
    path.write_text(content, encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--period", choices=["monthly", "quarterly"], default="monthly")
    parser.add_argument("--user-id", default=None)
    parser.add_argument("--database-url", default=None)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--usage-log", default=str(DEFAULT_USAGE_LOG))
    args = parser.parse_args()

    session = create_session(args.database_url)
    storage = SQLAlchemyStorage(session)
    summary = gather_summary(
        storage,
        period=args.period,
        user_id=args.user_id,
        usage_log=Path(args.usage_log),
    )
    content = render_report(summary)
    report_path = write_report(content, summary, Path(args.output_dir))
    print(f"Report written to {report_path}")


if __name__ == "__main__":
    main()
