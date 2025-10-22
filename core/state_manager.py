"""Manage conversation state with persistent backing stores."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from typing import Any

from .storage import SQLAlchemyStorage, create_session

try:  # pragma: no cover - optional dependency
    import redis  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency
    redis = None  # type: ignore

_STATE_TTL_DEFAULT = 60 * 60 * 24  # 24 hours


class StateManager:
    """Persist conversation state in Redis when available, else database."""

    def __init__(
        self,
        *,
        storage: SQLAlchemyStorage | None = None,
        redis_client: Any | None = None,
    ) -> None:
        self._cache: dict[str, dict] = {}
        self.storage = storage or SQLAlchemyStorage(create_session())
        self._redis = redis_client or self._initialise_redis()
        self._redis_prefix = os.getenv("GOALER_STATE_REDIS_KEY", "goaler:state")
        self._ttl = int(os.getenv("GOALER_STATE_TTL", str(_STATE_TTL_DEFAULT)))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def new_conversation(self, conversation_id: str, initial_state: dict):
        """Starts a new conversation with an initial state."""
        snapshot = deepcopy(initial_state)
        self._cache[conversation_id] = snapshot
        self._persist(conversation_id, snapshot)
        return True

    def get_state(self, conversation_id: str) -> dict | None:
        """Retrieves the current state for a given conversation."""
        cached = self._cache.get(conversation_id)
        if cached is not None:
            return deepcopy(cached)

        state = self._load_from_redis(conversation_id)
        if state is None:
            record = self.storage.get_conversation_state(conversation_id)
            if record and record.get("state"):
                state = record["state"]

        if state is None:
            return None

        self._cache[conversation_id] = state
        return deepcopy(state)

    def update_state(self, conversation_id: str, new_state: dict):
        """Updates the state for a given conversation."""
        if conversation_id not in self._cache and not self.get_state(conversation_id):
            return False
        snapshot = deepcopy(new_state)
        self._cache[conversation_id] = snapshot
        self._persist(conversation_id, snapshot)
        return True

    def end_conversation(self, conversation_id: str):
        """Clears the state for a finished or expired conversation."""
        if conversation_id in self._cache:
            del self._cache[conversation_id]
        self._delete_from_redis(conversation_id)
        self.storage.delete_conversation_state(conversation_id)
        return True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _initialise_redis(self) -> Any | None:
        url = os.getenv("GOALER_STATE_REDIS_URL")
        if not url:
            return None
        if redis is None:
            raise RuntimeError(
                "GOALER_STATE_REDIS_URL is set but the redis package is not installed."
            )
        return redis.Redis.from_url(url)

    def _redis_key(self, conversation_id: str) -> str:
        return f"{self._redis_prefix}:{conversation_id}"

    def _persist(self, conversation_id: str, state: dict) -> None:
        user_id = state.get("user_id")
        status = state.get("status", "ACTIVE")
        self.storage.save_conversation_state(
            conversation_id,
            state,
            user_id=user_id,
            status=status,
        )
        if self._redis is None:
            return
        payload = json.dumps(state, ensure_ascii=False)
        try:  # pragma: no cover - network dependent
            self._redis.set(self._redis_key(conversation_id), payload, ex=self._ttl)
        except Exception:
            pass

    def _load_from_redis(self, conversation_id: str) -> dict | None:
        if self._redis is None:
            return None
        try:  # pragma: no cover - network dependent
            raw = self._redis.get(self._redis_key(conversation_id))
        except Exception:
            return None
        if not raw:
            return None
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return None
        return data if isinstance(data, dict) else None

    def _delete_from_redis(self, conversation_id: str) -> None:
        if self._redis is None:
            return
        try:  # pragma: no cover - network dependent
            self._redis.delete(self._redis_key(conversation_id))
        except Exception:
            pass


# --- Example Usage (for demonstration) ---

if __name__ == "__main__":
    conv_id = "user123_session456"
    state_manager = StateManager()

    state_manager.new_conversation(conv_id, {"goal_title": "Learn Python"})
    print("Current state:", state_manager.get_state(conv_id))

    current_goal = state_manager.get_state(conv_id)
    if current_goal is not None:
        current_goal.setdefault("metrics", []).append(
            {
                "metric_name": "Complete exercises",
                "metric_type": "INCREMENTAL",
                "target_value": 50,
                "unit": "exercises",
            }
        )
        state_manager.update_state(conv_id, current_goal)
        print("Updated state:", state_manager.get_state(conv_id))

    state_manager.end_conversation(conv_id)
    print("Final state:", state_manager.get_state(conv_id))
