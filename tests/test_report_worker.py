from pathlib import Path
import json
import logging
from io import StringIO

import pytest

import tools.report_worker as worker


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    monkeypatch.delenv("SLACK_CHANNEL", raising=False)


def test_notify_slack_skips_without_config(caplog):
    caplog.set_level(logging.INFO)
    summary = {"user_label": "tester", "period": "monthly", "loot_counts": {}}
    worker._notify_slack(summary, "story", Path("/tmp/report.md"))
    assert any(
        "Slack configuration missing" in message for message in caplog.text.splitlines()
    )


def test_notify_slack_posts(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    summary = {
        "user_label": "tester",
        "period": "monthly",
        "loot_counts": {"ACHIEVEMENT": 2},
    }

    requests = []

    def fake_urlopen(req):
        payload = json.loads(req.data.decode("utf-8"))
        requests.append(payload)
        assert "Authorization" in req.headers
        assert req.headers["Authorization"].startswith("Bearer ")
        return StringIO(json.dumps({"ok": True}))

    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    monkeypatch.setenv("SLACK_CHANNEL", "#goaler")
    monkeypatch.setattr(worker.urllib_request, "urlopen", fake_urlopen)

    worker._notify_slack(summary, "story", Path("/tmp/report.md"))
    assert len(requests) == 1
    assert requests[0]["channel"] == "#goaler"
    assert "tester" in requests[0]["text"]
    assert any("Slack notification delivered" in line for line in caplog.text.splitlines())
