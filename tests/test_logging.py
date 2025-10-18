import json
from app import _log_llm_usage


def test_log_llm_usage_writes_record(tmp_path, monkeypatch):
    log_path = tmp_path / "usage.log"
    monkeypatch.setattr("app.USAGE_LOG_PATH", log_path, raising=False)
    usage = {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}

    _log_llm_usage("test-model", usage)

    assert log_path.exists()
    records = [
        json.loads(line)
        for line in log_path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    record = records[0]
    assert record["model"] == "test-model"
    assert record["prompt_tokens"] == 10
    assert record["total_tokens"] == 15
