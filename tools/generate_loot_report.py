#!/usr/bin/env python3
"""Generate monthly/quarterly loot reports.

This script is a scaffold that loads aggregated data, renders a textual report
using the templates defined in docs/LOOT_REPORT_TEMPLATE.md, and writes the
result to the reports/ directory. Actual data access should be implemented by
integrating with the storage layer or analytics pipeline.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

DEFAULT_OUTPUT_DIR = Path("reports")


def load_mock_data(period: str) -> dict:
    """Return sample data for demonstration/testing purposes."""

    return {
        "period": period,
        "generated_at": datetime.utcnow().isoformat(),
        "user_id": "sample-user",
        "loot": {
            "ACHIEVEMENT": ["서류 체크리스트 완성", "5km 테스트 완료"],
            "INSIGHT": ["제출 절차 이해"],
            "EMOTION": ["오늘 회복 모드가 마음을 지켜줬어요"],
        },
        "boss_progress": {
            "completed": ["사업자등록 완료"],
            "in_progress": ["첫 고객 인터뷰"],
            "next": ["MVP 공개"]
        },
        "warnings": {
            "warning": 1,
            "critical": 0,
            "emergency": 0,
        },
    }


def render_report(data: dict) -> str:
    """Render a simple markdown report from aggregated data."""

    lines = [
        f"# {data['period'].title()} Loot Report",
        f"Generated at: {data['generated_at']}",
        "",
        "## Highlights",
        f"- ACHIEVEMENT: {', '.join(data['loot'].get('ACHIEVEMENT', [])) or 'None'}",
        f"- INSIGHT: {', '.join(data['loot'].get('INSIGHT', [])) or 'None'}",
        f"- EMOTION: {', '.join(data['loot'].get('EMOTION', [])) or 'None'}",
        "",
        "## Boss Progress",
        f"- Completed: {', '.join(data['boss_progress'].get('completed', [])) or 'None'}",
        f"- In Progress: {', '.join(data['boss_progress'].get('in_progress', [])) or 'None'}",
        f"- Next: {', '.join(data['boss_progress'].get('next', [])) or 'None'}",
        "",
        "## Energy Warnings",
        json.dumps(data.get("warnings", {}), ensure_ascii=False),
    ]
    return "\n".join(lines)


def write_report(content: str, period: str, user_id: str, output_dir: Path) -> Path:
    """Write the report to disk and return the path."""

    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{user_id}-{period}-{datetime.utcnow().date()}.md"
    path = output_dir / filename
    path.write_text(content, encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--period", choices=["monthly", "quarterly"], default="monthly")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()

    data = load_mock_data(args.period)
    content = render_report(data)
    report_path = write_report(content, args.period, data["user_id"], Path(args.output_dir))
    print(f"Report written to {report_path}")


if __name__ == "__main__":
    main()
