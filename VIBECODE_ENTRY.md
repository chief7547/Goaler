# VIBECODE_ENTRY.md
> Vibecoding 단일-파일 매니페스트 및 초기 부트스트랩 템플릿
>
> 목적: 이 파일을 CLI가 읽고 프로젝트의 모든 초기 파일을 자동 생성하게 한다.
> 이후 사용자는 CLI와 인터뷰 형식으로 응답하며 앱 설계를 점진적으로 완성한다.
>
> 사용법 요약:
> 1. 리포지토리 루트에 이 파일을 둔다.
> 2. CLI(예: `vibe-cli bootstrap --entry VIBECODE_ENTRY.md`)를 실행하면 이 파일의 내장 템플릿으로 초기 파일들을 생성한다.
> 3. 생성된 CLI는 사용자를 인터뷰(한국어)하며 필수 항목을 채우도록 강제한다.
---
## 매니페스트 (자동화 엔진이 직접 파싱하는 YAML)
```yaml
name: "vibecoding-app"
version: "0.1.0"
description: "Vibecoding 단일-파일 매니페스트. CLI가 이 파일을 읽어 초기 세팅과 질문(clarifier)을 실행합니다."
language: "ko"

# 대화형 clarifier 설정
clarifier_max_questions: 12
clarifier_language: "ko"
confirm_every_step: true
defaults_doctrine:
  no_response_timeout_hours: 72
  proceed_if_no_response: false

# 시크릿 검증 (필수화)
preflight:
  checks:
    secrets_bound:
      type: "env_required"
      required_keys: ["OPENAI_API_KEY"]

# lock 체크 동작
lock_check:
  require_init_to_create: true

# mock / real 모드 플로우
mock_mode: true
require_use_real_flag_to_deploy: true

# 프로젝트 필수 파일 (CLI가 생성해야 할 파일 목록)
required_files:
  - "README.md"
  - "CONFIG.yaml"
  - "DATA_SCHEMA.yaml"
  - "requirements.txt"
  - "requirements-dev.txt"
  - ".flake8"
  - ".github/workflows/ci.yml"
  - "docker-compose.ci.yml"
  - "tools/preflight.py"
  - "tools/lock_check.py"
  - "tools/golden_check.py"
  - "tests/test_schema.py"
  - "tests/test_end2end.py"
  - "tests/golden/output_example.json"
  - "CLARIFIERS.md"
  - "PR_TEMPLATE.md"
  - ".gitignore"
  - "Dockerfile"
  - "core/__init__.py"
  - "core/llm_prompt.py"
  - "core/state_manager.py"
  - "ARCHITECTURE.md"

# 강제 테스트 목록 (머지 전 필수)
mandatory_tests:
  - "tests/test_schema.py"
  - "tests/test_end2end.py"
  - "tools/golden_check.py"

# 골든셋 (파일 경로 : sha256)
golden_checks:
  "tests/golden/output_example.json": "718ab90415e512926a69310557448cf3857b858145706c53c203035035616841"

# CI 및 브랜치 보호 권장 상태 이름
ci_required_statuses:
  - "lint"
  - "typecheck"
  - "pytest"
  - "coverage"
  - "golden-check"

# 실행 가이드 (CLI가 이 명령어들을 사용자에게 제시)
bootstrap_commands: |
  - "python -m venv .venv"
  - "source .venv/bin/activate  # or .venv\Scripts\activate on Windows"
  - "pip install -r requirements.txt"
  - "python tools/preflight.py --entry VIBECODE_ENTRY.md --init-lock-if-missing --check-secrets"
  - "python tools/docgen.py --entry VIBECODE_ENTRY.md  # (옵션) 문서 자동생성"
  - "vibe-cli interview --entry VIBECODE_ENTRY.md  # 대화형 clarifier 시작"
```

---

## 자동 생성 파일 템플릿
> 아래 블록들은 CLI가 이 파일을 파싱하여 같은 경로·내용으로 파일을 생성하도록 설계된 완전 템플릿입니다.
> CLI는 파일명 주석(`<!-- FILE: path -->`)을 읽고 해당 파일을 생성하세요.

<!-- FILE: README.md -->
```markdown
# Goaler

GPT 기반 목표 코칭 챗봇을 구현한 레포지토리입니다. `VIBECODE_ENTRY.md` 하나로 프로젝트 뼈대를 생성하고, 그 위에 대화형 목표 설정 로직과 테스트를 쌓아 올렸습니다.

## 빠른 시작

```bash
python -m venv .venv
source .venv/bin/activate  # Windows는 .venv\Scripts\activate
pip install -r requirements.txt
python tools/preflight.py --entry VIBECODE_ENTRY.md --init-lock-if-missing --check-secrets
```

### 실행 모드
- 기본(mock) 모드: 외부 호출 없이 흐름을 체험합니다.
  ```bash
python app.py
  ```

- 실전(OpenAI) 모드: 실제 GPT 모델과 대화합니다. `.env`에 `OPENAI_API_KEY`가 있어야 하며, mock 모드를 끄면 됩니다.
  ```bash
GOALER_USE_MOCK=false python app.py
  ```

## 주요 구성 요소
- `app.py`: 챗봇 진입점. mock/실전 모드를 자동 전환하고, LLM이 내린 함수 호출을 `GoalSettingAgent`에 위임합니다.
- `core/agent.py`: 목표 생성, 메트릭 추가, 동기 기록, 마무리까지 담당하는 비즈니스 로직.
- `core/state_manager.py`: 대화 중간 상태를 메모리에 저장했다가 종료 시 정리합니다.
- `tests/test_core.py`, `tests/test_e2e_conversation.py`: 단위 테스트와 통합 테스트로 로직이 예상대로 움직이는지 검증합니다.

## 테스트
```bash
PYTHONPATH=. pytest
```

## 데이터 저장 전략
- **MVP**: SQLite를 기본 저장소로 사용합니다. 별도 서버 없이 파일 하나로 목표·대화 상태를 영구 보관할 수 있습니다.
- **확장 단계**: PostgreSQL 등 서버형 DB로 전환할 수 있도록 구조를 분리해 두었습니다. 환경 변수로 연결 문자열을 바꾸면 마이그레이션이 가능합니다.

## 로드맵
1. **지속 저장소 고도화**: `StateManager`와 분리된 저장소 모듈을 도입해 SQLite→PostgreSQL 전환을 지원합니다.
2. **경험 확장**: 웹/모바일 UI 혹은 메시징 봇(슬랙 등)으로 챗봇을 옮겨 목표 진행 상황을 시각화합니다.
3. **장기 목표 코칭**: 장기 목표를 작은 단계로 쪼개고, 심리학·게이미피케이션 요소(주간 리포트, 축하 메시지 등)를 챗봇 응답에 녹입니다.
4. **알림/리마인더 연동**: 캘린더, 슬랙 알림 등을 통해 반복 목표를 꾸준히 챙겨줄 자동 체크인 기능을 추가합니다.
5. **운영·보안 강화**: 인증/권한, 배포 파이프라인, 브랜치 보호 규칙을 정교하게 유지합니다.
```

<!-- FILE: CONFIG.yaml -->
```yaml
app:
  name: "vibecoding-app"
  domain: "example.local"
  runtime: "python3.11"
  entry_point: "app.run:main"

data:
  input_path: "data/input"
  output_path: "data/output"

deployment:
  execution_mode: "container" # container | local
  container_image: "vibecoding/app:0.1"

testing:
  coverage_threshold: 0.80
```

<!-- FILE: DATA_SCHEMA.yaml -->
```yaml
# 간단한 데이터 스키마 예시 (YAML)
type: object
required:
  - id
  - payload
properties:
  id:
    type: string
  payload:
    type: object
```

<!-- FILE: requirements.txt -->
```
pytest
coverage
flask
pyyaml
openai
python-dotenv
```

<!-- FILE: requirements-dev.txt -->
```
flake8
mypy
black
types-PyYAML
```

<!-- FILE: .flake8 -->
```
[flake8]
max-line-length = 110
extend-ignore = E203
```

<!-- FILE: .gitignore -->
```
.venv/
__pycache__/
.env
.env.local
*.pyc
.vscode/
.idea/
audit/logs/

# Environment variables
.env
.env.*
```

<!-- FILE: CLARIFIERS.md -->
```markdown
# CLARIFIERS (Goaler 인터뷰 질문 템플릿)

## 1. 목표 개요 파악
- **Q1.** 이번에 달성하고 싶은 목표를 한 문장으로 설명해주세요. (예: “1년 안에 마라톤 완주”, “1년 안에 사이드 프로젝트로 첫 매출 100만 원 만들기”)
- **Q2.** 이 목표는 단발성(한 번 달성)인가요, 아니면 반복 유지형(습관/루틴)인가요?
- **Q3.** 목표를 달성하고 싶은 기한이 있나요? (예: 12개월, 특정 날짜)

## 2. 현재 상태와 측정 지표
- **Q4.** 현재 상태(베이스라인)는 어떤가요? (예: “현재는 5km까지 뛸 수 있음”, “월매출 0원”)
- **Q5.** 진행 상황을 어떻게 측정하고 싶나요? 필요한 지표를 가능한 한 구체적으로 적어주세요. (예: 주간 러닝 횟수, 누적 거리, 월 매출 금액)
- **Q6.** 목표를 이루기 위한 중간 단계(퀘스트/서브 목표)가 있다면 무엇인가요? (예: “3개월차에 하프 마라톤 완주”, “3개월 뒤 베타 서비스 출시”)

## 3. 동기와 보상 설계
- **Q7.** 이 목표를 꼭 이루고 싶은 이유(동기)는 무엇인가요?
- **Q8.** 목표를 지속하기 위해 받고 싶은 피드백이나 보상 방식이 있나요? (예: 주간 리포트, 경험치/뱃지, 코치 메시지)

## 4. 지원 장치 및 알림
- **Q9.** 목표 진행을 도와줄 알림/리마인더가 필요하신가요? 있다면 주기와 채널(앱 알림, 이메일, 슬랙 등)을 알려주세요.
- **Q10.** 목표 진행 중 예상되는 장애물이나 위험 요소가 있다면 무엇인가요? 이를 어떻게 모니터링하고 싶나요?

## 5. 운영 및 보안 고려사항
- **Q11.** 사용자 계정/권한 관리가 필요할까요? (예: 개인 전용, 팀 코치 전용, 관리자 기능)
- **Q12.** 데이터 보관/보안 측면에서 꼭 지켜야 할 규칙이 있다면 적어주세요. (예: 장기 보관, 암호화, 백업 주기)
```


<!-- FILE: PR_TEMPLATE.md -->
```markdown
# PR 템플릿

- [ ] 변경 사유와 요약을 기술했음
- [ ] CLARIFIERS에서 해당 섹션을 업데이트했음
- [ ] 모든 mandatory_tests 통과 (pytest, golden-check)
- [ ] coverage가 threshold를 만족
- [ ] 배포 시 mock->real 전환 정책 검토 완료
```

<!-- FILE: .github/workflows/ci.yml -->
```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          python -m pip install -r requirements.txt
          python -m pip install -r requirements-dev.txt
      - name: Run flake8
        run: flake8 .

  typecheck:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          python -m pip install -r requirements.txt
          python -m pip install -r requirements-dev.txt
      - name: Run mypy
        run: mypy .

  pytest:
    runs-on: ubuntu-latest
    needs: [lint, typecheck]
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          python -m pip install -r requirements.txt
          python -m pip install -r requirements-dev.txt
      - name: Run pytest with coverage
        run: |
          coverage run -m pytest -q
          coverage xml

  golden-check:
    runs-on: ubuntu-latest
    needs: pytest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          python -m pip install -r requirements.txt
          python -m pip install -r requirements-dev.txt
      - name: Verify golden files
        run: python tools/golden_check.py
```

<!-- FILE: docker-compose.ci.yml -->
```yaml
version: "3.8"
services:
  app:
    build: .
    environment:
      - ENV=ci
    command: ["bash","-lc","pytest -q"]
```

<!-- FILE: tools/preflight.py -->
```python
#!/usr/bin/env python3
"""Preflight checks for the Vibecoding manifest."""

from __future__ import annotations

import argparse
import os
import pathlib
import sys

import yaml
from dotenv import load_dotenv


def load_manifest(path: str) -> dict:
    """Extract the YAML manifest block from the entry file."""

    text = pathlib.Path(path).read_text(encoding="utf-8")
    try:
        manifest_section = text.split("## 매니페스트")[1].split("---")[0]
    except IndexError as exc:
        raise SystemExit("manifest section not found") from exc

    start = manifest_section.find("```yaml\n")
    if start == -1:
        raise SystemExit("manifest code fence not found")

    end = manifest_section.find("```", start + 7)
    if end == -1:
        raise SystemExit("manifest code fence terminator not found")

    yaml_text = manifest_section[start + 7 : end].strip()
    return yaml.safe_load(yaml_text)


def check_secrets(manifest: dict) -> list[str]:
    """Return missing environment variables defined in the manifest."""

    required = (
        manifest.get("preflight", {})
        .get("checks", {})
        .get("secrets_bound", {})
        .get("required_keys", [])
    )
    return [key for key in required if os.environ.get(key) is None]


def check_required_files(manifest: dict) -> list[str]:
    """Return missing files that the manifest expects to exist."""

    missing: list[str] = []
    for path_str in manifest.get("required_files", []):
        if not pathlib.Path(path_str).exists():
            missing.append(path_str)
    return missing


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--entry", required=True)
    parser.add_argument("--init-lock-if-missing", action="store_true")
    parser.add_argument("--check-secrets", action="store_true")
    args = parser.parse_args()

    manifest = load_manifest(args.entry)

    if args.check_secrets:
        missing = check_secrets(manifest)
        if missing:
            print("Missing required env keys:", missing)
            sys.exit(3)

    missing_files = check_required_files(manifest)
    if missing_files:
        print("Missing files expected to be generated:", missing_files)

    # Lock behavior delegated to tools/lock_check.py
    print("Preflight OK")


if __name__ == "__main__":
    main()
```

<!-- FILE: tools/lock_check.py -->
```python
#!/usr/bin/env python3
"""Manage the manifest lock file."""

import argparse
import json
import sys
from pathlib import Path

LOCK = Path("audit/manifest.lock")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true")
    args = parser.parse_args()

    if not LOCK.exists():
        if args.init:
            LOCK.parent.mkdir(parents=True, exist_ok=True)
            LOCK.write_text(json.dumps({"lock": "created"}), encoding="utf-8")
            print("Lock created")
        else:
            print(
                "LOCK missing. Run with --init to create after review.",
                file=sys.stderr,
            )
            sys.exit(2)
    else:
        print("Lock present")


if __name__ == "__main__":
    main()
```

<!-- FILE: tools/golden_check.py -->
```python
#!/usr/bin/env python3
"""Verify golden files against the manifest."""

from __future__ import annotations

import hashlib
import pathlib
import sys

import yaml


def load_manifest(path: str = "VIBECODE_ENTRY.md") -> dict:
    """Load the YAML manifest block from the entry file."""

    text = pathlib.Path(path).read_text(encoding="utf-8")
    start = text.find("```yaml")
    if start == -1:
        raise SystemExit("manifest block not found")
    end = text.find("```", start + 6)
    if end == -1:
        raise SystemExit("manifest block terminator not found")
    return yaml.safe_load(text[start + 6 : end])


def digest(path: pathlib.Path) -> str:
    """Return the sha256 digest for the given file path."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    manifest = load_manifest()
    golden = manifest.get("golden_checks", {})
    failures: list[str] = []

    for rel_path, expected_hash in golden.items():
        path = pathlib.Path(rel_path)
        if not path.exists():
            failures.append(f"missing:{rel_path}")
            continue
        if digest(path) != expected_hash:
            failures.append(f"mismatch:{rel_path}")

    if failures:
        print("Golden check failed:", failures)
        sys.exit(2)

    print("Golden verified")


if __name__ == "__main__":
    main()
```

<!-- FILE: tests/test_schema.py -->
```python
def test_schema_file_exists():
    import pathlib
    assert pathlib.Path("DATA_SCHEMA.yaml").exists(), "DATA_SCHEMA.yaml이 존재해야 합니다."
```

<!-- FILE: tests/test_end2end.py -->
```python
import pathlib

import yaml


def test_end2end_load_config() -> None:
    config_path = pathlib.Path("CONFIG.yaml")
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert "app" in cfg, "CONFIG.yaml에 app 섹션이 필요합니다."
```

<!-- FILE: tests/golden/output_example.json -->
```json
{"status":"ok","version":"1.0"}
```

<!-- FILE: tools/docgen.py -->
```python
#!/usr/bin/env python3
"""
간단 문서 생성 툴(placeholder).
실제 CLI는 manifest의 CLARIFIERS.md를 읽어 인터뷰를 시작합니다.
"""
print("docgen: placeholder - 실제 CLI에서 세부 문서 생성 로직을 실행하세요.")
```

<!-- FILE: core/__init__.py -->
```python
"""Core package for Goaler."""

__all__ = [
    "agent",
    "state_manager",
    "llm_prompt",
]
```

<!-- FILE: core/llm_prompt.py -->
```python
"""
This module defines the core prompt and function specifications for the LLM agent
that handles the conversational goal-setting process.
"""

# --- System Prompt for the Goal-Setting Agent ---

SYSTEM_PROMPT = """
# Persona
You are a friendly and expert goal-setting coach named 'Goaler'. Your tone is encouraging, clear, and helpful.

# Core Task
Your primary job is to help a user define their real-world goals through a natural conversation.
You will dynamically build a structured 'goal object' in the background by calling the functions provided to you.
Do not ask for all the information at once. Guide the user step-by-step.

# Rules
1.  **Start:** When a user wants to set a new goal, your first step is to call the `create_goal` function.
2.  **Gather Metrics:** As the user describes what they want to achieve, identify measurable metrics and use the `add_metric` function to add them to the goal.
3.  **Disambiguation (Crucial):** If a user's request is ambiguous, you MUST ask clarifying questions before calling any function.
    -   *Example 1:* If a user says "I want to run 5km", you must ask: "Great! Is that a one-time goal to achieve, or a recurring habit you want to build, like running 5km every week?"
    -   *Example 2:* If a user mentions a target without a clear number, you must ask for a specific value.
4.  **Gather Motivation:** At a natural point in the conversation, ask the user *why* they want to achieve this goal and use the `set_motivation` function.
5.  **Confirmation:** After successfully adding or updating a part of the goal (like adding a new metric), briefly confirm what you've done and show the user the current state of their goal by summarizing it.
6.  **Finalize:** Once the user is happy with their goal and has nothing more to add, call the `finalize_goal` function to complete the process.
"""

# --- Function (Tool) Definitions for the LLM ---
# Note: These are the function signatures the LLM will be trained to call.
# The actual implementation will be in a different module.

def create_goal(title: str):
    """
    Creates a new goal object in the conversation state. This is the first step.
    
    Args:
        title (str): A short, descriptive title for the goal.
    """
    print(f"--- TOOL CALL: create_goal(title='{title}') ---")
    # In a real implementation, this would interact with the StateManager.
    pass

def add_metric(metric_name: str, metric_type: str, target_value: float, unit: str, initial_value: float = None):
    """
    Adds a new measurable metric to the current goal.
    
    Args:
        metric_name (str): The name of the metric (e.g., "Weight", "Running Distance").
        metric_type (str): The type of metric. Supported types: 'INCREMENTAL', 'DECREMENTAL'.
        target_value (float): The target value to achieve.
        unit (str): The unit of measurement (e.g., "kg", "km", "pages").
        initial_value (float, optional): The starting value, if applicable.
    """
    print(f"--- TOOL CALL: add_metric(name='{metric_name}', type='{metric_type}', target={target_value}, unit='{unit}') ---")
    # In a real implementation, this would interact with the StateManager.
    pass

def set_motivation(text: str):
    """
    Sets the user's motivation or "epic meaning" for the goal.
    
    Args:
        text (str): The user's description of why they want to achieve the goal.
    """
    print(f"--- TOOL CALL: set_motivation(text='{text}') ---")
    # In a real implementation, this would interact with the StateManager.
    pass

def finalize_goal():
    """
    Finalizes the goal-setting process and saves the goal to the database.
    """
    print("--- TOOL CALL: finalize_goal() ---")
    # In a real implementation, this would move the goal from the StateManager to the permanent DB.
    pass
```

<!-- FILE: core/state_manager.py -->
```python
"""
This module defines the StateManager, which is responsible for holding and 
managing the state of a goal-setting conversation.
"""

# For a real implementation, this would use a more robust key-value store like Redis.
# For this prototype, a simple Python dictionary is sufficient to demonstrate the logic.
_STATE_CACHE = {}

class StateManager:
    """Manages the in-progress goal object for each conversation."""

    def new_conversation(self, conversation_id: str, initial_state: dict):
        """Starts a new conversation with an initial state."""
        print(f"--- STATE: New conversation started: {conversation_id} ---")
        _STATE_CACHE[conversation_id] = initial_state
        return True

    def get_state(self, conversation_id: str) -> dict | None:
        """Retrieves the current state for a given conversation."""
        return _STATE_CACHE.get(conversation_id)

    def update_state(self, conversation_id: str, new_state: dict):
        """Updates the state for a given conversation."""
        if conversation_id not in _STATE_CACHE:
            return False
        print(f"--- STATE: State updated for {conversation_id} ---")
        _STATE_CACHE[conversation_id].update(new_state)
        return True

    def end_conversation(self, conversation_id: str):
        """Clears the state for a finished or expired conversation."""
        if conversation_id in _STATE_CACHE:
            print(f"--- STATE: Conversation ended: {conversation_id} ---")
            del _STATE_CACHE[conversation_id]
        return True

# --- Example Usage (for demonstration) ---

if __name__ == '__main__':
    conv_id = "user123_session456"
    state_manager = StateManager()

    # 1. A new conversation starts
    state_manager.new_conversation(conv_id, {"goal_title": "Learn Python"})
    print("Current state:", state_manager.get_state(conv_id))

    # 2. A metric is added during the conversation
    current_goal = state_manager.get_state(conv_id)
    if 'metrics' not in current_goal:
        current_goal['metrics'] = []
    current_goal['metrics'].append({
        "metric_name": "Complete exercises",
        "metric_type": "INCREMENTAL",
        "target_value": 50,
        "unit": "exercises"
    })
    state_manager.update_state(conv_id, current_goal)
    print("Updated state:", state_manager.get_state(conv_id))

    # 3. The conversation ends
    state_manager.end_conversation(conv_id)
    print("Final state:", state_manager.get_state(conv_id))
```

---

## 초기 CLI 동작 플로우 (정확히 강제되는 단계)
1. CLI가 `VIBECODE_ENTRY.md`를 읽는다.
2. manifest YAML을 파싱한다.
3. `required_files` 목록에 대해 존재 여부 점검. 없으면 템플릿을 위 블록으로 생성한다.
4. `preflight.checks.secrets_bound.required_keys`가 비어있지 않으면 환경변수 유무를 검사. 없으면 CLI는 사용자에게 입력을 요구하고 파일 `.env.local`에 안전하게 저장하도록 유도한다.
5. `lock_check.require_init_to_create`가 true이면 `tools/lock_check.py --init`을 클라이언트(사용자) 동작으로만 허용. 자동 생성 불가.
6. `clarifier_max_questions` 만큼 인터뷰 질문을 진행하되 `confirm_every_step: true`이면 각 섹션 완료 시 사용자의 명시 확인(yes/no)을 요구한다.
7. 인터뷰를 통해 채워진 값은 `CONFIG.yaml` 등 생성 파일에 반영된다.
8. 사용자가 "배포/실행"을 요청하면 CLI는 다음을 강제 실행:
   - flake8, mypy 실행
   - pytest (coverage 포함)
   - tools/golden_check.py 실행
   - 컨테이너 기반 통합 스모크 (docker-compose.ci.yml) 실행(선택적)
9. 위 검사 중 실패하면 PR/병합 불가. CLI는 실패 리포트를 생성하고 사용자는 수정을 통해 재시도.

---

## 운영·검증 정책 (권장)
- 브랜치 보호 규칙에 `ci_required_statuses`를 필수로 설정하세요.
- PR 템플릿을 통해 작성자가 골든셋·통합테스트 체크박스를 필수화 하세요.
- `mock_mode` 사용 중인 경우 PR 제목/레이블에 `[mock]` 태그를 붙이고, `--use-real` 플래그가 있어야만 배포 브랜치로 머지 가능하도록 정책을 둡니다.

---

## CLI를 위한 간단 구현 계약 (포맷 명세)
- 매니페스트 YAML은 이 파일 내 최초 ```yaml 블록에서 로드됩니다.
- 파일 템플릿은 `<!-- FILE: path -->` 주석을 찾아 다음 코드 블록의 내용을 생성합니다.
- 생성 시 파일이 이미 존재하면 덮어쓰기 전 사용자 확인을 요구합니다.
- 생성 후 `tools/lock_check.py --init`을 사용자에게 실행시키도록 유도합니다.

---

## 빠른 시작(복사·붙여넣기 가능한 명령)
```bash
# 1) VENV 및 의존 설치
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2) 초기 사전검증 (시크릿 체크 포함)
python tools/preflight.py --entry VIBECODE_ENTRY.md --check-secrets

# 3) 락 수동 생성 (검토 후)
python tools/lock_check.py --init

# 4) 대화형 인터뷰 시작 (가상 CLI 명령 예시)
# vibe-cli는 이 매니페스트를 파싱해 생성해야 할 파일들을 만들고 인터뷰를 진행함
vibe-cli interview --entry VIBECODE_ENTRY.md
```

---

## 메모(제한 사항 및 기대치)
- 이 파일은 "강제화" 메커니즘을 최대한 포함합니다. 그러나 AI(코드 생성기)가 문서 일부를 누락해도, CI와 브랜치 보호로 **사람이 수정하도록 강제**하면 운영 오류는 실질적으로 차단됩니다.
- `golden_checks`의 해시는 위 `tests/golden/output_example.json` 내용에 대해 계산된 값입니다. 실제 골든셋을 갱신하면 manifest의 `golden_checks`도 함께 갱신해야 합니다.
- CLI가 이 파일을 기반으로 모든 것을 자동 생성하도록 구현하는 것이 목표입니다. 필요하면 내가 위 파일들을 바로 파일로 생성해 드립니다.

---
끝.
