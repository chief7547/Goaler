import pytest

from core.llm_limits import LLMQuotaManager, LLMRateLimitError
from core.storage import create_session_factory


def _make_factory(tmp_path):
    db_path = tmp_path / "quota.db"
    return create_session_factory(f"sqlite:///{db_path}")


def _reset_env(monkeypatch):
    monkeypatch.delenv("LLM_MAX_DAILY_TOKENS", raising=False)
    monkeypatch.delenv("LLM_MAX_DAILY_TOKENS_PER_USER", raising=False)
    monkeypatch.delenv("LLM_MAX_DAILY_REQUESTS", raising=False)
    monkeypatch.delenv("LLM_MAX_DAILY_REQUESTS_PER_USER", raising=False)


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    _reset_env(monkeypatch)


def test_quota_allows_when_no_limits(tmp_path):
    manager = LLMQuotaManager(_make_factory(tmp_path))
    manager.enforce_limit("user-1")  # no exception


def test_token_limit_enforced(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_MAX_DAILY_TOKENS_PER_USER", "100")
    factory = _make_factory(tmp_path)
    manager = LLMQuotaManager(factory)

    manager.enforce_limit("user-1")
    manager.record_usage(
        user_id="user-1",
        conversation_id="conv-1",
        model="gpt-test",
        usage={"prompt_tokens": 80, "completion_tokens": 0, "total_tokens": 80},
    )
    manager.enforce_limit("user-1")
    manager.record_usage(
        user_id="user-1",
        conversation_id="conv-1",
        model="gpt-test",
        usage={"prompt_tokens": 25, "completion_tokens": 0, "total_tokens": 25},
    )
    with pytest.raises(LLMRateLimitError):
        manager.enforce_limit("user-1")


def test_global_request_limit(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_MAX_DAILY_REQUESTS", "2")
    factory = _make_factory(tmp_path)
    manager = LLMQuotaManager(factory)

    for _ in range(2):
        manager.record_usage(
            user_id="user-a",
            conversation_id="conv",
            model="gpt-test",
            usage={"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        )
    with pytest.raises(LLMRateLimitError):
        manager.enforce_limit("user-b")


def test_request_limit_per_user(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_MAX_DAILY_REQUESTS_PER_USER", "1")
    factory = _make_factory(tmp_path)
    manager = LLMQuotaManager(factory)

    manager.record_usage(
        user_id="user-z",
        conversation_id="conv",
        model="gpt-test",
        usage={"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10},
    )
    with pytest.raises(LLMRateLimitError):
        manager.enforce_limit("user-z")


def test_usage_persists_across_manager_instances(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_MAX_DAILY_TOKENS_PER_USER", "50")
    factory = _make_factory(tmp_path)

    manager = LLMQuotaManager(factory)
    manager.record_usage(
        user_id="sticky-user",
        conversation_id="conv-1",
        model="gpt-test",
        usage={"prompt_tokens": 40, "completion_tokens": 5, "total_tokens": 45},
    )
    manager.record_usage(
        user_id="sticky-user",
        conversation_id="conv-1",
        model="gpt-test",
        usage={"prompt_tokens": 10, "completion_tokens": 0, "total_tokens": 10},
    )

    # New instance should still observe prior usage because totals are persisted.
    manager = LLMQuotaManager(factory)
    with pytest.raises(LLMRateLimitError):
        manager.enforce_limit("sticky-user")
