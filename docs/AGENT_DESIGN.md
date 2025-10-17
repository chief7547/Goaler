# GoalSettingAgent & LLM 함수 계약

이 문서는 LLM이 어떤 형식으로 도구를 호출하고, `GoalSettingAgent`가 어떤 데이터를 읽고/쓰기 위해 저장소와 상호작용하는지를 정의합니다. 설계만으로 동일한 로직을 재구현할 수 있도록 상세 계약을 명시합니다.

## 1. 상태 구성요소
### StateManager
- 대화별 임시 상태를 보관합니다.
- 상태 예시 (JSON)
    ```json
    {
      "goal_summary": {
        "title": "string",
        "goal_type": "ONE_TIME",
        "deadline": "2025-12-31",
        "motivation": null,
        "metrics": [],
        "current_variations": [QuestDraft]
      },
      "conversation_id": "conv_a1b2",
      "user_id": "user_123",
      "last_tool_call": "propose_quests"
    }
    ```
  - `MetricDraft`는 아래 JSON 스키마와 동일합니다.

### Storage (필수 메서드)
- `get_user_preferences(user_id)` → 사용자 성향·선호
- `get_player_progress(user_id)` → 현재 Stage/레벨/스트릭
- `list_recent_quest_logs(goal_id, limit=10)` → 최근 수행 기록
- `create_goal(goal: GoalCreate)` / `update_motivation(goal_id, motivation)`
- `create_metric(goal_id, metric: MetricCreate)`
- `create_quest(goal_id, quest: QuestCreate)`
- `log_quest_event(entry: QuestLogCreate)`
- `finalize_goal(goal_id)`
- `update_player_progress(user_id, progress: PlayerProgressUpdate)`

### ThemeTermResolver (권장)
- 입력: `user_preferences.theme_preference`, `player_progress.stage_label`
- 출력: `theme_terms` 딕셔너리. 예)
  ```json
  {
    "quest": "퀘스트",
    "boss": "보스",
    "loot": "전리품",
    "potion": "물약"
  }
  ```
- 규칙
  - `theme_preference = GAME` → Boss/Loot/Potion/Quest 용어 사용.
  - `theme_preference = PROFESSIONAL` → “핵심 마일스톤/성과·인사이트 로그/재충전/실행 계획”으로 치환.
  - Stage 코드가 `STAGE_1_5_BOSS_PREVIEW` 미만이면, 보스/전리품 용어를 노출하지 않고 기본 표현(“오늘의 할 일”, “기록”)을 반환.
- 모든 함수 프롬프트(`Daily Prompt Templates`, `Response Templates`)는 이 Resolver가 생성한 `theme_terms`를 입력으로 받아 일관된 표현을 유지한다.

## 2. LLM 함수 (Tool) 계약

-### 2.1 create_goal
- **목적**: 새 목표를 초기화
- **입력**
  ```json
  {
    "title": "string",
    "goal_type": "ONE_TIME" | "HABIT",
    "deadline": "2025-12-31" (ISO8601) | null,
    "motivation_hint": "string" | null
  }
  ```
- **출력 (Agent → LLM)**
  ```json
  {
    "status": "ok",
    "goal": {
      "goal_id": "uuid",
      "title": "string",
      "deadline": "2025-12-31" | null,
      "motivation": null,
      "metrics": [],
      "suggested_variations": []
    }
  }
  ```
- **처리**
  1. `StateManager.new_conversation`으로 임시 상태 생성
  2. `Storage.create_goal` 호출
  3. 사용자 성향·최근 기록을 조회하여 추천 퀘스트 2~3개를 `StateManager`에 넣어 둡니다.

-### 2.2 add_metric
- **목적**: 측정 지표 추가
- **입력**
  ```json
  {
    "goal_id": "uuid",
    "metric_name": "string",
    "metric_type": "INCREMENTAL" | "DECREMENTAL" | "THRESHOLD",
    "target_value": number,
    "unit": "string",
    "initial_value": number | null
  }
  ```
- **출력**
  ```json
  {
    "status": "ok",
    "metrics": [
      {
        "metric_id": "uuid",
        "metric_name": "string",
        "metric_type": "INCREMENTAL",
        "target_value": 3,
        "unit": "회",
        "initial_value": 0
      }
    ]
  }
  ```
- **처리**
  - `Storage.create_metric`
  - `StateManager`의 `goal_summary.metrics` 갱신

-### 2.3 define_boss_stages
- **목적**: 장기 목표의 핵심 단계(현실 과업 보스전) 정의
- **입력**
  ```json
  {
    "goal_id": "uuid",
    "boss_candidates": [
      {
        "title": "사업자등록 완료",
        "description": "법적 지위를 확보하고 판매 준비를 마친다",
        "success_criteria": "국세청 등록 완료",
        "target_week": 8
      }
    ]
  }
  ```
- **출력**
  ```json
  {
    "status": "ok",
    "boss_stages": [
      {
        "boss_id": "uuid",
        "title": "사업자등록 완료",
        "stage_order": 2,
        "target_week": 8
      }
    ]
  }
  ```
- **처리**
  - 사용자와 대화를 통해 3~5개의 핵심 과업을 선정합니다.
  - `Storage.create_boss_stage`(추가 예정 메서드)로 저장.
  - Stage 순서는 LLM이 추천하되 사용자가 수정할 수 있도록 State에 저장합니다.

### 2.4 propose_weekly_plan
- **목적**: 특정 보스전을 준비하기 위한 주간 체크포인트 제안
- **입력**
  ```json
  {
    "goal_id": "uuid",
    "boss_id": "uuid",
    "week_index": 2
  }
  ```
- **출력**
  ```json
  {
    "status": "ok",
    "weekly_plan": [
      {
        "title": "사업자등록 서류 목록 확정",
        "description": "필요 서류와 제출 경로 확인",
        "week_index": 2
      }
    ]
  }
  ```
- **처리**
  - 보스전 정보를 참고해 1~3개의 주간 단계 제안.
  - `StateManager.goal_summary.weekly_plan`에 임시 저장 후 사용자 확인을 받습니다.

### 2.5 propose_daily_tasks
- **목적**: 주간 체크포인트를 달성하기 위한 일일 준비 퀘스트 제안
- **입력**
  ```json
  {
    "goal_id": "uuid",
    "weekly_step": {
      "title": "사업자등록 서류 목록 확정"
    }
  }
  ```
- **출력**
  ```json
  {
    "status": "ok",
    "daily_tasks": [
      {
        "title": "사업자등록 필요 서류 검색",
        "description": "홈택스/정부24를 참고해 목록 작성"
      }
    ]
  }
  ```
- **처리**
  - 제안된 일일 퀘스트는 기존 변주 시스템과 동일한 구조로 `quests`에 등록됩니다.

### 2.6 propose_quests
- **목적**: 오늘의 변주 퀘스트 제안 (LLM 단독 호출용)
- **입력**
  ```json
  {
    "goal_id": "uuid",
    "user_id": "uuid",
    "candidate_pool": [
      {
        "title": "주 3회 러닝",
        "variation_tags": ["tempo_up", "outdoor"],
        "difficulty_tier": "NORMAL",
        "expected_duration_minutes": 30
      }
    ]
  }
  ```
- **출력**
  ```json
  {
    "status": "ok",
    "variations": [
      {
        "title": "오늘은 러닝 속도 10% 올려보기",
        "description": "어제보다 조금 빠른 페이스로 30분 달리기",
        "difficulty_tier": "HARD",
        "expected_duration_minutes": 30,
        "variation_tags": ["tempo_up"],
        "reason": "연속 3회 성공으로 난이도 상향",
        "llm_variation_seed": "hash"
      },
      {
        "title": "집에서 체중 운동 콤보",
        "description": "버피-스쿼트-런지 15분 루틴",
        "difficulty_tier": "NORMAL",
        "expected_duration_minutes": 20,
        "variation_tags": ["indoor", "tempo_mix"],
        "reason": "오늘 비 예보 + 에너지 보충",
        "llm_variation_seed": "hash2"
      }
    ]
  }
  ```
- **처리**
  1. Agent가 최근 `quest_logs`, `user_preferences`, `player_progress`를 모아서 LLM 도구 호출
  2. 반환된 변주 후보를 `StateManager`와 DB(`quests`)에 임시 저장

### 2.4 choose_quest
- **목적**: 사용자가 선택한 변주를 확정
- **입력**
  ```json
  {
    "goal_id": "uuid",
    "quest_choice": {
      "title": "집에서 체중 운동 콤보",
      "description": "...",
      "difficulty_tier": "NORMAL",
      "expected_duration_minutes": 20,
      "variation_tags": ["indoor", "tempo_mix"],
      "llm_variation_seed": "hash2"
    }
  }
  ```
- **출력**
  ```json
  {
    "status": "ok",
    "quest": {
      "quest_id": "uuid",
      "title": "집에서 체중 운동 콤보",
      "difficulty_tier": "NORMAL",
      "expected_duration_minutes": 20
    }
  }
  ```
- **처리**
  - `Storage.create_quest`로 영구 저장
  - `StateManager.goal_summary.current_variations` 비우기

### 2.8 log_quest_outcome
- **목적**: 수행 결과와 성취/에너지 피드백 기록
- **입력**
  ```json
  {
    "quest_id": "uuid",
    "goal_id": "uuid",
    "outcome": "COMPLETED" | "SKIPPED" | "FAILED" | "DEFERRED",
    "perceived_difficulty": "TOO_EASY" | "JUST_RIGHT" | "TOO_HARD",
    "energy_status": "READY_FOR_BOSS" | "KEEPING_PACE" | "NEEDS_POTION",
    "loot_type": "ACHIEVEMENT" | "INSIGHT" | "EMOTION",
    "mood_note": "오늘 얻은 전리품은 ‘페이스 유지 자신감’"
  }
  ```
- **출력**
  ```json
  {
    "status": "ok",
    "next_suggestion_hint": "내일은 강도 낮추기 모드"
  }
  ```
- **처리**
  - `Storage.log_quest_event`
  - 필요 시 `player_progress` 업데이트 (연속 성공, 경험치 가산) 및 에너지 상태를 기반으로 다음 변주 강도 조정
  - `perceived_difficulty` 값은 에너지 버튼, 최근 연속 성공, 변주 난이도 정보를 바탕으로 Agent가 산출할 수 있으며 사용자가 직접 입력하지 않아도 됩니다.
  - `loot_type`은 사용자가 선택한 전리품 칩을 그대로 저장하며, 주간 콤보/Relic 계산에 활용됩니다.
  - `energy_status`가 `NEEDS_POTION`이면 경고 레벨을 갱신합니다.
    - Warning: 1회 → 다음 제안에서 회복 변주를 자동 포함.
    - Critical: 2회 연속 또는 동일 주 `DEFERRED` 2회 → 휴식/보완 퀘스트를 기본값으로 제안하고 공격 변주는 숨김.
    - Emergency: 3회 연속 → “포션 의식” 루틴(이틀치 회복 미션 + 전리품 보호) 트리거.
  - Warning/Critical/Emergency 발생 시 `player_progress`에 경고 레벨을 기록하고, 챗봇이 안내 메시지를 전송합니다.

### 2.9 set_motivation / finalize_goal
- 기존 설계와 동일. 단, `set_motivation`은 감정 노트/성향 요약과 함께 저장하고, `finalize_goal`은 요약을 대화 로그에도 기록합니다.
- Stage 변화 로직과 연동: `player_progress`의 Stage/레벨/스트릭을 업데이트할 때 승급/강등 여부를 판단해 텍스트 연출과 경고 메시지를 챗봇이 전송합니다.
- 온보딩 연동: `user_preferences.onboarding_stage`가 `STAGE_0_ONBOARDING`~`STAGE_1_5_BOSS_PREVIEW` 구간에 있을 때는 전리품/에너지 관련 도구 호출을 단계별로 지연하거나 설명을 간소화합니다. 해금 조건은 `docs/ONBOARDING_PLAN.md`를 따라야 합니다.

## 3. 저장소 메서드 요약
- `Storage` 클래스는 위 함수들이 필요로 하는 CRUD를 전부 제공해야 하며, 각 메서드는 실패 시 명시적 예외를 던집니다. 예)
  - `GoalNotFoundError`
  - `QuestNotFoundError`
  - `UserNotFoundError`
  - `StorageConflictError` (동일 변주를 다시 저장하려 할 때)
- 테스트에서는 `sqlite:///:memory:` 구성을 사용해 동작을 검증합니다.

### 3.1 Storage 클래스 설계 (요약)
```python
class Storage:
    def __init__(self, session_factory):
        self._Session = session_factory

    def create_goal(self, goal: GoalCreate) -> Goal: ...
    def add_metric(self, goal_id: str, metric: MetricCreate) -> Metric: ...
    def get_user_preferences(self, user_id: str) -> UserPreferences | None: ...
    def get_player_progress(self, user_id: str) -> PlayerProgress | None: ...
    def list_recent_quest_logs(self, goal_id: str, limit: int = 10) -> list[QuestLog]: ...
    def create_quest(self, goal_id: str, quest: QuestCreate) -> Quest: ...
    def log_quest_event(self, entry: QuestLogCreate) -> QuestLog: ...
    def update_player_progress(self, user_id: str, update: PlayerProgressUpdate) -> PlayerProgress: ...
    def update_motivation(self, goal_id: str, motivation: str) -> Goal: ...
    def finalize_goal(self, goal_id: str) -> Goal: ...
```

각 데이터 클래스는 `DATA_SCHEMA.yaml` 구조와 매핑되며, 필수 필드 누락 시 명확한 오류를 반환합니다.

## 4. LLM 프롬프트 활용 시 주의점
- `SYSTEM_PROMPT`에 “변주를 만들 때 반드시 reason과 variation_tags를 채워라”는 규칙을 추가합니다.
- 오답 방지를 위해 함수 인자/응답 JSON 스키마를 프롬프트에 그대로 삽입합니다.
- 장기적으로는 OpenAI “tool_choice=strict”를 사용해 지정된 함수만 호출하도록 제한합니다.
- `NEEDS_POTION` 신호가 연속으로 나타나면 로드맵 자체는 유지하되 하루 또는 이틀 분량의 “회복 퀘스트”를 제안하고, 이후 다시 표준 난이도로 복귀하도록 프롬프트 예시를 제공합니다.
- 전리품 기록(`mood_note`)이 일정 기간 비어 있으면 LLM이 “이번 주 가장 뿌듯했던 한 순간”을 회상하도록 질문하고, 긍정 경험을 다시 떠올리게 합니다.
- 경고 레벨에 따라 프롬프트 예시를 분리합니다.
  - Warning: 회복 변주 포함, 공격/수비 선택지를 2→1개로 축소.
  - Critical: 회복/보완 퀘스트만 제안, 성공 시 “Guardian Buff” 부여 메시지 포함.
  - Emergency: “포션 의식” 시나리오 묘사와 휴식 후 재도전 계획 안내.
- `docs/COACH_TONE_GUIDE.md`에 정리된 말투 가이드를 SYSTEM_PROMPT에 반영하여,
  `challenge_appetite`, `energy_status`, `loot_type`, `boss_stages` 등을 근거로 톤을
  변화시키도록 합니다.
- 응답 템플릿 활용: `docs/RESPONSE_TEMPLATES.md`의 문구를 우선적으로 사용하고, LLM은 플레이스홀더만 채우거나 템플릿과 생성 문장을 조합합니다. 같은 문장이 반복되지 않도록 최근 사용 템플릿을 캐시합니다.
- 온보딩 단계 반영: `user_preferences.onboarding_stage`가 `STAGE_0_ONBOARDING`이면 복잡한 기능 언급을 피하고, Stage 0.5/1/1.5에 해당하는 코드(`STAGE_0_5_LOOT`, `STAGE_1_ENERGY`, `STAGE_1_5_BOSS_PREVIEW`) 해금 시점에 맞춰 “새 장비를 소개할게요” 등 단계별 문구를 사용합니다.
