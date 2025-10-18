"""End-to-end tests for the conversational loop."""

import json
import os
import subprocess
import threading
import time
import unittest
from types import SimpleNamespace

import pytest


class TestE2EConversation(unittest.TestCase):
    """Process-level smoke test that exercises the default mock loop."""

    def test_simple_greeting(self):
        """Simulates a simple greeting to test basic CLI behaviour."""

        inputs = [
            "안녕",
            "exit",
        ]

        stdout_lines = []
        stderr_lines = []

        env = os.environ.copy()
        env["PYTHONPATH"] = "."

        process = subprocess.Popen(
            ["python", "-u", "app.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            env=env,
        )

        def read_pipe(pipe, output_list):
            for line in iter(pipe.readline, ""):
                output_list.append(line)

        stdout_thread = threading.Thread(
            target=read_pipe, args=(process.stdout, stdout_lines)
        )
        stderr_thread = threading.Thread(
            target=read_pipe, args=(process.stderr, stderr_lines)
        )
        stdout_thread.start()
        stderr_thread.start()

        try:
            time.sleep(3)

            for line in inputs:
                if process.poll() is not None:
                    break
                print(f"[TEST INPUT] > {line}")
                process.stdin.write(line + "\n")
                process.stdin.flush()
                time.sleep(5)

        finally:
            process.stdin.close()
            process.terminate()
            process.wait(timeout=5)
            stdout_thread.join(timeout=5)
            stderr_thread.join(timeout=5)

        full_stdout = "".join(stdout_lines)
        full_stderr = "".join(stderr_lines)

        print("\n--- Full STDOUT ---")
        print(full_stdout)
        print("--- Full STDERR ---")
        print(full_stderr)
        print("--- End of Output ---")

        self.assertIn("Goaler (OpenAI) 준비 완료", full_stdout)
        self.assertIn("안녕하세요", full_stdout)
        self.assertEqual(full_stderr, "")


def _make_tool_call(name: str, arguments: dict, call_id: str) -> object:
    """Utility to emulate an OpenAI tool call payload."""

    return SimpleNamespace(
        id=call_id,
        function=SimpleNamespace(
            name=name,
            arguments=json.dumps(arguments),
        ),
    )


class _FakeMessage:
    """Lightweight stand-in for the SDK response message."""

    def __init__(self, *, content: str | None, tool_calls: list | None = None):
        self.content = content
        self.tool_calls = tool_calls or []


class _FakeResponse:
    """Wrapper that mimics the OpenAI Chat Completions response."""

    def __init__(self, message):
        self.choices = [SimpleNamespace(message=message)]


def test_tool_call_driven_goal_flow(monkeypatch, capsys):
    """Simulates a full goal flow where the LLM issues tool calls in sequence."""

    monkeypatch.syspath_prepend(os.getcwd())

    import app

    monkeypatch.setenv("GOALER_USE_MOCK", "false")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    class FakeGoalSettingAgent:
        """Agent double that records tool usage while mimicking state updates."""

        last_instance = None

        def __init__(self):
            self.state = {}
            self.calls: list[tuple] = []
            FakeGoalSettingAgent.last_instance = self

        def create_goal(self, conversation_id: str, title: str):
            self.state[conversation_id] = {
                "goal_title": title,
                "metrics": [],
                "motivation": None,
            }
            self.calls.append(("create_goal", conversation_id, title))
            return self.state[conversation_id]

        def add_metric(self, conversation_id: str, metric_details: dict):
            self.state[conversation_id]["metrics"].append(metric_details)
            self.calls.append(("add_metric", conversation_id, metric_details))
            return self.state[conversation_id]

        def set_motivation(self, conversation_id: str, text: str):
            self.state[conversation_id]["motivation"] = text
            self.calls.append(("set_motivation", conversation_id, text))
            return self.state[conversation_id]

        def finalize_goal(self, conversation_id: str):
            final_snapshot = self.state.get(conversation_id, {}).copy()
            self.calls.append(("finalize_goal", conversation_id, final_snapshot))
            return True

        # Phase 2 stubs -------------------------------------------------
        def define_boss_stages(
            self,
            conversation_id: str,
            goal_id: str,
            boss_candidates: list[dict],
        ):
            self.calls.append(
                ("define_boss_stages", conversation_id, goal_id, boss_candidates)
            )
            return {"status": "ok", "boss_stages": []}

        def propose_weekly_plan(
            self,
            conversation_id: str,
            goal_id: str,
            boss_id: str,
            weekly_plan: list[dict],
        ):
            self.calls.append(
                ("propose_weekly_plan", conversation_id, boss_id, weekly_plan)
            )
            return {"status": "ok", "weekly_plan": weekly_plan}

        def propose_daily_tasks(
            self,
            conversation_id: str,
            goal_id: str,
            weekly_step: dict,
            daily_tasks: list[dict],
        ):
            self.calls.append(
                ("propose_daily_tasks", conversation_id, weekly_step, daily_tasks)
            )
            return {"status": "ok", "daily_tasks": daily_tasks}

        def choose_quest(self, conversation_id: str, goal_id: str, quest_choice: dict):
            self.calls.append(("choose_quest", conversation_id, quest_choice))
            return {"status": "ok", "quest": quest_choice}

        def propose_quests(
            self, conversation_id: str, goal_id: str, candidate_pool: list[dict]
        ):
            self.calls.append(("propose_quests", conversation_id, candidate_pool))
            return {"status": "ok", "variations": candidate_pool}

        def log_quest_outcome(self, conversation_id: str, payload: dict):
            self.calls.append(("log_quest_outcome", conversation_id, payload))
            return {"status": "ok", "log": payload}

    monkeypatch.setattr(app, "GoalSettingAgent", FakeGoalSettingAgent)

    class FakeOpenAI:
        """Minimal OpenAI stub that replays scripted responses."""

        def __init__(self, api_key: str):
            self.api_key = api_key
            self._cursor = 0
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=self._create)
            )
            self._script = [
                _FakeMessage(
                    content=None,
                    tool_calls=[
                        _make_tool_call(
                            "create_goal", {"title": "체중 감량 목표"}, "call_create"
                        ),
                    ],
                ),
                _FakeMessage(content="'체중 감량 목표'를 생성했어요."),
                _FakeMessage(
                    content=None,
                    tool_calls=[
                        _make_tool_call(
                            "add_metric",
                            {
                                "metric_details": {
                                    "metric_name": "주간 러닝",
                                    "metric_type": "INCREMENTAL",
                                    "target_value": 3,
                                    "unit": "회",
                                }
                            },
                            "call_metric",
                        )
                    ],
                ),
                _FakeMessage(content="주간 러닝 지표를 추가했어요."),
                _FakeMessage(
                    content=None,
                    tool_calls=[
                        _make_tool_call(
                            "set_motivation",
                            {"text": "건강을 위해서예요."},
                            "call_motivation",
                        )
                    ],
                ),
                _FakeMessage(content="동기를 기록했어요. 다른 도움이 필요할까요?"),
                _FakeMessage(
                    content=None,
                    tool_calls=[
                        _make_tool_call("finalize_goal", {}, "call_finalize"),
                    ],
                ),
                _FakeMessage(content="목표 설정을 마무리했습니다."),
            ]

        def _create(self, **_kwargs):
            if self._cursor >= len(self._script):
                pytest.fail("FakeOpenAI 스크립트가 예상보다 먼저 소진되었습니다.")
            message = self._script[self._cursor]
            self._cursor += 1
            return _FakeResponse(message)

    monkeypatch.setattr(app, "OpenAI", FakeOpenAI)

    inputs = iter(
        [
            "체중 감량 목표 세우고 싶어",
            "주당 3회 러닝으로 측정하고 싶어",
            "동기는 건강 때문이야",
            "이제 마무리하자",
            "exit",
        ]
    )

    def fake_input(_prompt: str) -> str:
        try:
            return next(inputs)
        except StopIteration:
            return "exit"

    monkeypatch.setattr("builtins.input", fake_input)

    app.run_conversation()

    captured = capsys.readouterr().out

    assert "TOOL CALL: create_goal" in captured
    assert "TOOL CALL: add_metric" in captured
    assert "TOOL CALL: finalize_goal" in captured

    agent = FakeGoalSettingAgent.last_instance
    assert agent is not None

    call_order = [entry[0] for entry in agent.calls]
    assert call_order == [
        "create_goal",
        "add_metric",
        "set_motivation",
        "finalize_goal",
    ]

    _, conv_id, goal_title = agent.calls[0]
    assert goal_title == "체중 감량 목표"
    assert conv_id.startswith("conv_")

    _, _, metric_details = agent.calls[1]
    assert metric_details["metric_name"] == "주간 러닝"
    assert metric_details["target_value"] == 3

    _, _, motivation_text = agent.calls[2]
    assert motivation_text == "건강을 위해서예요."

    _, _, final_state = agent.calls[3]
    assert final_state["goal_title"] == "체중 감량 목표"
    assert len(final_state["metrics"]) == 1
    assert final_state["motivation"] == "건강을 위해서예요."


if __name__ == "__main__":
    unittest.main()
