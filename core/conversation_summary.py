"""Conversation summarisation helper utilities."""

from __future__ import annotations

from datetime import datetime
from typing import Callable, Iterable

from .storage import SQLAlchemyStorage


class ConversationSummarizer:
    """Summarise conversation logs when 메시지가 일정 개수를 넘었을 때."""

    def __init__(
        self,
        storage: SQLAlchemyStorage,
        summary_fn: Callable[[Iterable[dict]], str],
        *,
        threshold: int = 40,
        keep_latest: int = 10,
    ) -> None:
        self.storage = storage
        self.summary_fn = summary_fn
        self.threshold = threshold
        self.keep_latest = keep_latest

    def summarise_if_needed(self, conversation_id: str) -> str | None:
        """Create a summary and trim old logs if threshold를 초과하면 요약."""

        count = self.storage.count_conversation_logs(conversation_id)
        if count <= self.threshold:
            return None

        logs = self.storage.list_conversation_logs(conversation_id, limit=self.threshold)
        if not logs:
            return None

        ordered_logs = list(reversed(logs))
        summary_text = self.summary_fn(ordered_logs)
        if not summary_text:
            return None

        period_start = _parse_datetime(ordered_logs[0]["created_at"])
        period_end = _parse_datetime(ordered_logs[-1]["created_at"])
        self.storage.create_conversation_summary(
            {
                "conversation_id": conversation_id,
                "period_start": period_start,
                "period_end": period_end,
                "summary_text": summary_text,
            }
        )
        self.storage.trim_conversation_logs(
            conversation_id,
            keep_latest=self.keep_latest,
        )
        return summary_text


def _parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


__all__ = ["ConversationSummarizer"]
