"""Utilities for tracking and enforcing LLM usage quotas."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session, sessionmaker

from .models import LLMUsageDaily, LLMUsageLedger
from .storage import create_session_factory

try:  # pragma: no cover - optional dependency
    import redis  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency
    redis = None  # type: ignore


class LLMRateLimitError(RuntimeError):
    """Raised when an LLM request exceeds configured quotas."""


def _as_int(env_value: Optional[str]) -> Optional[int]:
    if not env_value:
        return None
    try:
        value = int(env_value)
    except ValueError:
        return None
    return value if value > 0 else None


def _start_of_day() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def _today() -> date:
    return _start_of_day().date()


@dataclass
class _UsageTotals:
    tokens: int = 0
    requests: int = 0


_GLOBAL_USER_ID = "__GLOBAL__"


def _redis_key(prefix: str, day: date, user_id: str) -> str:
    return f"{prefix}:{day.isoformat()}:{user_id}"


class LLMQuotaManager:
    """Tracks usage and enforces quotas for LLM requests."""

    def __init__(
        self,
        session_factory: sessionmaker[Session] | None = None,
        *,
        database_url: str | None = None,
    ) -> None:
        self._factory = session_factory or create_session_factory(database_url)
        self._global_token_limit = _as_int(os.getenv("LLM_MAX_DAILY_TOKENS"))
        self._user_token_limit = _as_int(os.getenv("LLM_MAX_DAILY_TOKENS_PER_USER"))
        self._global_request_limit = _as_int(os.getenv("LLM_MAX_DAILY_REQUESTS"))
        self._user_request_limit = _as_int(os.getenv("LLM_MAX_DAILY_REQUESTS_PER_USER"))
        self._block_message = (
            os.getenv(
                "LLM_LIMIT_REACHED_MESSAGE",
                "오늘은 충분히 많은 대화를 했어요. 내일 다시 이어가볼까요?",
            )
            or "LLM usage limit reached for today."
        )
        self._redis_client: Any | None = None
        redis_url = os.getenv("LLM_REDIS_URL")
        if redis_url:
            if redis is None:  # pragma: no cover - optional dependency guard
                raise RuntimeError(
                    "LLM_REDIS_URL is set but the redis package is not installed."
                )
            self._redis_client = redis.Redis.from_url(redis_url)
        self._redis_prefix = os.getenv("LLM_REDIS_KEY_PREFIX", "goaler:llm")
        self._redis_ttl = _as_int(os.getenv("LLM_REDIS_TTL")) or 60 * 60 * 48

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def enforce_limit(self, user_id: str) -> None:
        """Raise if the given user has already exhausted their quota."""

        if not self._any_limits_defined:
            return

        totals_user, totals_global = self._get_totals(user_id)

        if self._user_token_limit is not None and totals_user.tokens >= self._user_token_limit:
            raise LLMRateLimitError(self._block_message)

        if self._global_token_limit is not None and totals_global.tokens >= self._global_token_limit:
            raise LLMRateLimitError(self._block_message)

        if self._user_request_limit is not None and totals_user.requests >= self._user_request_limit:
            raise LLMRateLimitError(self._block_message)

        if self._global_request_limit is not None and totals_global.requests >= self._global_request_limit:
            raise LLMRateLimitError(self._block_message)

    def record_usage(
        self,
        *,
        user_id: str,
        conversation_id: str | None,
        model: str | None,
        usage: dict | None,
    ) -> None:
        """Persist usage metrics returned by the OpenAI client."""

        if not usage:
            return

        prompt_tokens = usage.get("prompt_tokens") or 0
        completion_tokens = usage.get("completion_tokens") or 0
        total_tokens = usage.get("total_tokens") or (prompt_tokens + completion_tokens)

        day = _today()
        now = datetime.now(timezone.utc)

        self._redis_increment(day, user_id, prompt_tokens, completion_tokens, total_tokens)
        self._redis_increment(day, _GLOBAL_USER_ID, prompt_tokens, completion_tokens, total_tokens)

        with self._factory() as session:
            ledger = LLMUsageLedger(
                user_id=user_id,
                conversation_id=conversation_id,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            )
            session.add(ledger)
            self._increment_daily(
                session,
                day,
                user_id,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                now,
            )
            self._increment_daily(
                session,
                day,
                _GLOBAL_USER_ID,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                now,
            )
            session.commit()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @property
    def _any_limits_defined(self) -> bool:
        return any(
            limit is not None
            for limit in (
                self._global_token_limit,
                self._user_token_limit,
                self._global_request_limit,
                self._user_request_limit,
            )
        )

    def _get_totals(self, user_id: str) -> tuple[_UsageTotals, _UsageTotals]:
        day = _today()
        totals_user = self._redis_fetch(day, user_id)
        totals_global = self._redis_fetch(day, _GLOBAL_USER_ID)
        if totals_user is not None and totals_global is not None:
            return totals_user, totals_global
        with self._factory() as session:
            if totals_user is None:
                totals_user = self._daily_totals(session, day, user_id=user_id)
            if totals_global is None:
                totals_global = self._daily_totals(session, day, user_id=_GLOBAL_USER_ID)
        return totals_user, totals_global

    def _daily_totals(self, session: Session, day: date, *, user_id: str) -> _UsageTotals:
        record = session.get(LLMUsageDaily, (day, user_id))
        if record is None:
            return _UsageTotals()
        return _UsageTotals(tokens=int(record.total_tokens), requests=int(record.request_count))

    def _redis_fetch(self, day: date, user_id: str) -> _UsageTotals | None:
        if not self._redis_client:
            return None
        key = _redis_key(self._redis_prefix, day, user_id)
        try:
            data = self._redis_client.hgetall(key)
        except Exception:  # pragma: no cover - network failure fallback
            return None
        if not data:
            return None
        tokens = int(data.get(b"total_tokens", 0))
        requests = int(data.get(b"request_count", 0))
        return _UsageTotals(tokens=tokens, requests=requests)

    def _redis_increment(
        self,
        day: date,
        user_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
    ) -> None:
        if not self._redis_client:
            return
        key = _redis_key(self._redis_prefix, day, user_id)
        try:
            pipe = self._redis_client.pipeline(True)
            pipe.hincrby(key, "prompt_tokens", prompt_tokens)
            pipe.hincrby(key, "completion_tokens", completion_tokens)
            pipe.hincrby(key, "total_tokens", total_tokens)
            pipe.hincrby(key, "request_count", 1)
            pipe.expire(key, self._redis_ttl)
            pipe.execute()
        except Exception:  # pragma: no cover - redis optional
            pass

    def _increment_daily(
        self,
        session: Session,
        day: date,
        user_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        timestamp: datetime,
    ) -> None:
        record = session.get(LLMUsageDaily, (day, user_id))
        if record is None:
            record = LLMUsageDaily(
                day=day,
                user_id=user_id,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                request_count=0,
                updated_at=timestamp,
            )
            session.add(record)

        record.prompt_tokens += prompt_tokens
        record.completion_tokens += completion_tokens
        record.total_tokens += total_tokens
        record.request_count += 1
        record.updated_at = timestamp


__all__ = ["LLMQuotaManager", "LLMRateLimitError"]
