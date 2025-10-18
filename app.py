"""Main entrypoint for the Goaler conversational agent."""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from core.agent import STAGE_0, GoalSettingAgent, SYSTEM_PROMPT

STAGE_LABELS = {
    STAGE_0: "Stage 0 – Spark Awakening",
}


DEFAULT_CHAT_MODEL = "gpt-5-mini"
# Task-specific model plan (see docs/LLM_USAGE_GUIDE.md for details)
LLM_MODEL_PLAN = {
    "goal_planning": {
        "primary": "gpt-5-mini",
        "fallback": "gpt-4o-mini",
    },
    "summaries": {
        "primary": "gpt-4o-mini",
        "fallback": "gpt-5-mini",
    },
    "reflection_reports": {
        "primary": "gpt-5-mini",
        "fallback": "gpt-4o-mini",
    },
}

USAGE_LOG_PATH = Path("logs/llm_usage.log")


def _log_llm_usage(model: str, usage: dict | None) -> None:
    """Append token usage information to a local log for cost monitoring."""

    if not usage:
        return

    USAGE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "model": model,
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
    }
    with USAGE_LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def _usage_to_dict(usage_obj: object) -> dict | None:
    """Best-effort conversion from SDK usage object to plain dict."""

    if usage_obj is None:
        return None
    for attr in ("to_dict", "model_dump", "dict"):
        method = getattr(usage_obj, attr, None)
        if callable(method):
            return method()
    if isinstance(usage_obj, dict):
        return usage_obj
    # Fallback: use attribute dictionary if available
    return getattr(usage_obj, "__dict__", None)


def _use_mock_mode() -> bool:
    """Decide whether to run with the lightweight mock loop."""

    flag = os.getenv("GOALER_USE_MOCK")
    if flag is None:
        # Manifest 기본값(mock_mode: true)을 그대로 따릅니다.
        return True
    return flag.strip().lower() not in {"0", "false", "no"}


def _run_mock_conversation():
    """Fallback loop that emulates the agent without external API calls."""

    print("--- Goaler (OpenAI) 초기화 중... ---", flush=True)
    print(
        "--- Goaler (OpenAI) 준비 완료. 대화를 시작하세요. (종료하려면 'exit' 입력) ---",
        flush=True,
    )
    print("(mock 모드 활성화: OpenAI 호출 없이 대화를 시뮬레이션합니다.)", flush=True)

    agent = GoalSettingAgent()
    conversation_id = f"mock_{uuid.uuid4()}"

    greeted = False
    goal_created = False

    while True:
        user_input = input("> ")
        if user_input.lower() == "exit":
            print("대화를 종료합니다.")
            break

        if not greeted:
            print(
                "Goaler: 안녕하세요! 목표 설정을 도와드릴게요. 이루고 싶은 목표가 있다면 말씀해주세요.",
                flush=True,
            )
            greeted = True
            continue

        if not goal_created:
            title = user_input.strip() or "나의 목표"
            agent.create_goal(conversation_id=conversation_id, title=title)
            context = agent.get_onboarding_context(conversation_id)
            stage_code = context["onboarding_stage"]
            stage_label = STAGE_LABELS.get(stage_code, stage_code)
            print(
                f"Goaler: '{title}' 목표를 생성했어요. 지금은 {stage_label} 단계라서 한 걸음씩만 가볼게요.",
                flush=True,
            )
            print(
                "Goaler: 오늘은 작게 해볼 '기본 퀘스트' 하나만 떠올려볼까요? 전리품이나 에너지 체크는 아직 숨겨 둘게요.",
                flush=True,
            )
            goal_created = True
            continue

        reply = agent.compose_coach_reply(conversation_id)
        print(f"Goaler: {reply}", flush=True)


def _run_openai_conversation():
    """Runs the main conversational loop using the OpenAI API."""

    print("--- Goaler (OpenAI) 초기화 중... ---", flush=True)

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    except Exception as exc:
        print(
            f"오류: OpenAI 클라이언트 초기화에 실패했습니다. OPENAI_API_KEY를 확인하세요. 에러: {exc}"
        )
        return

    agent = GoalSettingAgent()
    agent_tools = {
        "create_goal": agent.create_goal,
        "add_metric": agent.add_metric,
        "set_motivation": agent.set_motivation,
        "finalize_goal": agent.finalize_goal,
        "define_boss_stages": agent.define_boss_stages,
        "propose_weekly_plan": agent.propose_weekly_plan,
        "propose_daily_tasks": agent.propose_daily_tasks,
        "choose_quest": agent.choose_quest,
        "propose_quests": agent.propose_quests,
        "log_quest_outcome": agent.log_quest_outcome,
    }

    model_name = DEFAULT_CHAT_MODEL

    tools_json_schema = [
        {
            "type": "function",
            "function": {
                "name": "create_goal",
                "description": "Creates a new goal. This should be the first step.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "A short, descriptive title for the goal.",
                        }
                    },
                    "required": ["title"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "add_metric",
                "description": "Adds a new measurable metric to the current goal.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "metric_details": {
                            "type": "object",
                            "description": "Full metric payload to append to the goal.",
                            "properties": {
                                "metric_name": {"type": "string"},
                                "metric_type": {"type": "string"},
                                "target_value": {"type": "number"},
                                "unit": {"type": "string"},
                                "initial_value": {"type": "number"},
                            },
                            "required": [
                                "metric_name",
                                "metric_type",
                                "target_value",
                                "unit",
                            ],
                        },
                        "metric_name": {"type": "string"},
                        "metric_type": {"type": "string"},
                        "target_value": {"type": "number"},
                        "unit": {"type": "string"},
                        "initial_value": {"type": "number"},
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "define_boss_stages",
                "description": "Persists boss stage candidates for the goal.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "boss_candidates": {
                            "type": "array",
                            "items": {"type": "object"},
                        },
                        "goal_id": {"type": "string"},
                    },
                    "required": ["boss_candidates", "goal_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "propose_weekly_plan",
                "description": "Registers weekly plan steps for a boss stage.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goal_id": {"type": "string"},
                        "boss_id": {"type": "string"},
                        "weekly_plan": {"type": "array", "items": {"type": "object"}},
                    },
                    "required": ["goal_id", "boss_id", "weekly_plan"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "propose_daily_tasks",
                "description": "Suggests daily tasks for the selected weekly step.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goal_id": {"type": "string"},
                        "weekly_step": {"type": "object"},
                        "daily_tasks": {"type": "array", "items": {"type": "object"}},
                    },
                    "required": ["goal_id", "weekly_step", "daily_tasks"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "propose_quests",
                "description": "Offers quest variations for user choice.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goal_id": {"type": "string"},
                        "candidate_pool": {
                            "type": "array",
                            "items": {"type": "object"},
                        },
                    },
                    "required": ["goal_id", "candidate_pool"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "choose_quest",
                "description": "Locks in a quest variation for execution.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goal_id": {"type": "string"},
                        "quest_choice": {"type": "object"},
                    },
                    "required": ["goal_id", "quest_choice"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "log_quest_outcome",
                "description": "Logs the result of a quest execution.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goal_id": {"type": "string"},
                        "quest_id": {"type": "string"},
                        "occurred_at": {"type": "string"},
                        "outcome": {"type": "string"},
                        "energy_status": {"type": "string"},
                        "loot_type": {"type": "string"},
                        "perceived_difficulty": {"type": "string"},
                        "mood_note": {"type": "string"},
                        "llm_variation_seed": {"type": "string"},
                    },
                    "required": ["goal_id", "quest_id", "occurred_at", "outcome"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "set_motivation",
                "description": "Sets the user's motivation for the goal.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The user's motivation.",
                        }
                    },
                    "required": ["text"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "finalize_goal",
                "description": "Finalizes the goal-setting process.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    ]

    conversation_id = f"conv_{uuid.uuid4()}"
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    print(
        "--- Goaler (OpenAI) 준비 완료. 대화를 시작하세요. (종료하려면 'exit' 입력) ---",
        flush=True,
    )

    while True:
        user_input = input("> ")
        if user_input.lower() == "exit":
            print("대화를 종료합니다.")
            break

        messages.append({"role": "user", "content": user_input})

        while True:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=tools_json_schema,
                tool_choice="auto",
            )
            usage_dict = _usage_to_dict(getattr(response, "usage", None))
            _log_llm_usage(model_name, usage_dict)
            response_message = response.choices[0].message

            if not response_message.tool_calls:
                final_text = response_message.content
                if final_text:
                    print(f"Goaler: {final_text}", flush=True)
                    messages.append({"role": "assistant", "content": final_text})
                break

            messages.append(response_message)
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                agent_method = agent_tools.get(function_name)

                if not agent_method:
                    print(
                        f"오류: 알 수 없는 함수({function_name}) 호출을 시도했습니다.",
                        flush=True,
                    )
                    continue

                function_args = json.loads(tool_call.function.arguments or "{}")
                function_args["conversation_id"] = conversation_id

                if (
                    function_name == "add_metric"
                    and "metric_details" not in function_args
                    and {"metric_name", "metric_type", "target_value", "unit"}.issubset(
                        function_args.keys()
                    )
                ):
                    function_args["metric_details"] = {
                        key: function_args[key]
                        for key in (
                            "metric_name",
                            "metric_type",
                            "target_value",
                            "unit",
                            "initial_value",
                        )
                        if key in function_args
                    }

                print(
                    f"--- TOOL CALL: {function_name}({function_args}) with conv_id: {conversation_id} ---",
                    flush=True,
                )

                tool_response = agent_method(**function_args)

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(tool_response),
                    }
                )


def run_conversation():
    """Entry point that selects mock or OpenAI-backed chat loop."""

    load_dotenv()
    if _use_mock_mode():
        _run_mock_conversation()
    else:
        _run_openai_conversation()


if __name__ == "__main__":
    run_conversation()
