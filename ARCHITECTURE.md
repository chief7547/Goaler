# Goaler 프로젝트 아키텍처

이 문서는 Goaler 프로젝트의 핵심 아키텍처, 설계 원칙, 그리고 개발 워크플로우를 설명합니다.

## 0. 개발 접근 전략: 핵심 로직을 먼저 탄탄하게

이 프로젝트는 “대화만으로 목표를 정의하고 완성할 수 있는가?”라는 질문에서 시작했습니다. 그래서 UI나 데이터베이스를 붙이기 전에, **목표를 단계별로 조립하는 비즈니스 로직**을 TDD로 먼저 만들고 충분히 검증했습니다. 이렇게 해 두니, 나중에 챗봇이 GPT를 통해 어떤 메시지를 보내더라도 결국 믿고 맡길 수 있는 코어가 생겼습니다.

## 1. 핵심 철학: 대화형 목표 설정

초기 `VIBECODE_ENTRY.md`의 인터뷰 방식은 정적인 질문/답변으로 구성되어 복잡하고 유연한 목표 설정을 구현하기에 한계가 있었습니다.

따라서, 우리는 사용자와의 자연스러운 대화를 통해 목표를 구체화하고, 지표를 추가/수정하며, 동기를 부여하는 **대화형 목표 설정(Conversational Goal-Setting)** 방식을 핵심 철학으로 채택했습니다. 이 방식은 LLM의 Function Calling(Tool-use) 능력을 기반으로 하며, 사용자가 복잡한 폼을 채울 필요 없이 AI 코치와 대화하듯 목표를 설정하는 경험을 제공합니다.

## 2. 주요 구성 요소 (`core` 디렉토리)

대화형 목표 설정을 구현하기 위한 핵심 로직은 `core` 디렉토리 안에 캡슐화되어 있습니다.

- **`core/agent.py` (`GoalSettingAgent`):**
  - 전체 대화 과정을 오케스트레이션하는 **총괄 지휘자**입니다.
  - `StateManager`를 소유하여 대화의 '상태'를 관리합니다.
  - LLM이 호출하는 `create_goal`, `add_metric`, `define_boss_stages`, `propose_weekly_plan`, `propose_daily_tasks`, `propose_quests`, `choose_quest`, `log_quest_outcome`, `set_motivation`, `finalize_goal` 등의 비즈니스 로직을 메소드로 포함합니다.

- **`core/state_manager.py` (`StateManager`):**
  - 대화가 진행되는 동안 필요한 최소한의 컨텍스트(대화 ID → `goal_id`, 기능 해금 플래그, 미확정 변주 등)를 보관하는 **단기 메모리**입니다.
  - 모든 영속 데이터(목표, 보스전, 퀘스트, 전리품 로그)는 `core/storage.py`를 통해 데이터베이스에 저장합니다. 즉, DB가 단일 진실 공급원(Single Source of Truth)이고 StateManager는 포인터/캐시만 유지합니다.
  - 이 원칙에 따라 GoalSettingAgent의 각 메서드는 먼저 Storage로 데이터를 쓰거나 읽고, 필요한 경우에만 StateManager를 업데이트합니다.

- **`core/llm_prompt.py`:**
  - LLM 에이전트의 행동을 정의하는 **지시문(Instruction)과 도구(Tool) 명세서**입니다.
  - `SYSTEM_PROMPT`는 LLM의 페르소나, 역할, 규칙(예: 모호할 경우 되묻기)을 정의합니다.
  - `create_goal` 등의 함수 시그니처는 LLM에게 어떤 도구를 사용할 수 있는지 알려주는 API 계약(Contract) 역할을 합니다.

## 3. 대화형 목표 설정 워크플로우

1.  **사용자 입력:** 사용자가 "새로운 목표를 만들고 싶어"와 같이 대화를 시작합니다. UI는 목표 설명·기한·추천 퀘스트 카테고리(6종)를 먼저 보여 주고, 사용자는 체크리스트 형태로 퀘스트를 고르거나 "직접 정의" 버튼을 눌러 챗봇과 새 퀘스트를 만듭니다. 숫자형 지표는 고급 옵션으로 분리하며, 기본 경험은 퀘스트 완료 위주로 설계합니다. MVP는 동시에 하나의 집중 목표를 다루지만, 저장소와 UI 설계는 다중 목표 카드로 확장할 수 있도록 준비해 둡니다.
2.  **LLM 의도 파악:** LLM은 `SYSTEM_PROMPT`와 함수 명세를 바탕으로 사용자의 의도를 파악합니다. (예: `create_goal` 함수 호출 필요)
3.  **함수 호출 (Function Calling):** LLM은 텍스트 대신, 실행해야 할 함수(예: `agent.create_goal(...)`)를 특정 형식으로 반환합니다.
4.  **에이전트 실행:** 애플리케이션은 LLM의 함수 호출 요청을 받아, `GoalSettingAgent`의 해당 메소드를 실행합니다.
5.  **상태 변경:** 에이전트의 메소드는 `StateManager`를 통해 현재 대화의 상태를 변경(생성, 수정)합니다.
6.  **LLM 응답 생성:** 에이전트는 실행 결과를 바탕으로 LLM에게 다음 응답 생성을 요청합니다. (예: "목표가 정리됐어요. 오늘 시작하기 좋은 퀘스트는 ‘주 3회 러닝’입니다. 완료 후 버튼만 눌러 주세요!")
7.  **응답 및 반복:** LLM의 응답이 사용자에게 전달되고, 사용자가 목표 설정을 완료할 때까지 위 과정이 반복됩니다.

## 4. 데이터 저장 전략 (MVP → 확장 단계)

- **MVP (개발 환경/소규모 사용자)**
  - SQLite를 기본 저장소로 채택합니다. 추가 인프라 없이 파일 하나로 목표와 대화 상태를 영구 보관할 수 있으며, 파이썬 표준 라이브러리(`sqlite3`)만으로 구현 가능합니다.
  - 기본 DB 파일 경로는 `data/goaler.db`이며, 환경 변수 `GOALER_DATABASE_URL`로 다른 경로나 엔진(SQLite/PostgreSQL 등)을 지정할 수 있습니다.
  - `StateManager`의 저장/조회 로직을 저장소 어댑터로 분리해 두면, 인메모리 → SQLite 전환을 코드 변경 최소화로 맞출 수 있습니다.
  - 저장소 어댑터는 SQLAlchemy를 사용해 세션을 관리하고, `core/storage.py`에서 CRUD 함수를 제공합니다.
  - 기본 테이블 구조 예시: `users`, `user_preferences`, `player_progress`, `goals`, `boss_stages`, `metrics`, `quests`, `quest_logs`, `conversation_logs`, `conversation_summaries`, `reminders`입니다.
  - `goals`에는 `title`, `goal_type`, `deadline`, `motivation`, `status`, `user_id`, `conversation_id` 등을 저장합니다.
  - `user_preferences`에는 MBTI/성향·도전 선호도·집중 시간대·싫어하는 패턴 등을 기록해 LLM 변주 로직이 사용자 맞춤 제안을 하도록 돕습니다.
  - `quests`에는 `goal_id`, `title`, `description`, `difficulty_tier`, `expected_duration_minutes`, `variation_tags`, `is_custom`, `origin_prompt_hash` 등을 저장합니다.
  - `quest_logs`는 outcome, perceived_difficulty, mood_note, llm_variation_seed 등을 포함해 일별 수행 결과와 감정 메모를 추적합니다.
  - `player_progress`는 현재 집중 목표, Stage/레벨, 경험치, 주간 연속 달성 정보를 저장해 난이도 조정과 보상 루프 계산에 활용합니다.
  - 리마인더 채널은 우선 Slack Webhook을 기본값으로 사용합니다.
  - UI 계층은 대시보드(“오늘의 추천 행동” 히어로 카드 + 집중 목표 카드 + 퀘스트 체크리스트)와 목표 상세 화면(핵심 정보 카드, 퀘스트 보드, 추천 행동 히스토리, 대화 요약, 리마인더 미리보기)을 MVP 기준으로 제공하며, 다중 목표 지원을 위해 카드 리스트 구조로 확장이 용이하도록 설계합니다.

- **서비스 단계 (정식 배포/확장)**
  - PostgreSQL 같은 서버형 RDBMS로 전환합니다. SQL 문법이 SQLite와 동일 계열이어서 마이그레이션 비용이 낮고, 사용자 수가 늘어도 안정적으로 동작합니다.
  - 환경 변수(예: `GOALER_DATABASE_URL`)로 연결 문자열을 주입하고, ORM(SQLAlchemy 등)을 사용하면 저장소 교체가 더욱 쉬워집니다.

- **문서 및 템플릿 연계**
  - `README.md`와 `VIBECODE_ENTRY.md` 템플릿에 “개발: SQLite / 배포: PostgreSQL” 흐름을 명시해 CLI가 생성하는 문서도 같은 전략을 반영하도록 합니다.

### 4.2 일일 퀘스트 변주 전략

- **핵심 목표**: 사용자가 “매일 같은 숙제를 반복한다”는 피로감을 느끼지 않도록, LLM이 동일 카테고리 안에서 조금씩 다른 미션을 제시합니다. 기본 진행률은 유지하되 매일의 경험은 새롭고 가볍게 느껴지게 설계합니다.
- **참고 신호**: LLM이 퀘스트를 생성하거나 변형할 때 아래 요소를 반드시 고려합니다.
  - 최근 달성률과 연속 성공/실패 기록 (`quest_logs.outcome`, `perceived_difficulty`).
  - 사용자 성향(`user_preferences.personality_type`, `challenge_appetite`, `preferred_playstyle`)과 “즐거웠던/싫었던” 패턴(`disliked_patterns`).
  - 게임 디자인 휴리스틱(변동 보상, 난이도 곡선, 선택권 제공, 손실 회피, 러닝 코스트 조절).
  - 생활 맥락(집중 가능한 시간대, 대화 중 언급한 일정, 리마인더 응답 속도)과 감정 상태(`quest_logs.mood_note`).
  - 최근 제시 이력 및 변주 태그(`quests.variation_tags`, `quest_logs.llm_variation_seed`)를 비교해 반복 감지를 수행합니다.
- **데이터 구조**: 위 요소를 담기 위해 `DATA_SCHEMA.yaml`에는 `quests`, `quest_logs`, `user_preferences` 스키마를 정의했습니다. GoalSettingAgent는 이 정보를 `StateManager`와 저장소 모듈을 통해 읽고, LLM 함수 호출 파라미터에 전달합니다.
- **난이도 스케일링**: LLM은 `difficulty_tier`와 `expected_duration_minutes`를 바탕으로 기본 난이도를 설정하고, 사용자 피드백(“너무 쉬웠어요” 등)이 연속으로 들어오면 다음 변주에서 한 단계 상향/하향합니다.
- **선택권 부여**: 가능하면 두 개 이상의 변주를 제안하고 사용자가 택하도록 하며, 선택 결과를 `quest_logs`에 기록해 자율성을 강화합니다.

### 4.1 저장소 인터페이스 개요

- **모델 정의 (`core/models.py`)**: SQLAlchemy `Base`와 각 테이블 클래스를 정의합니다. 모델 간 관계(예: `Goal`→`Quest`, `Goal`→`Conversation`)를 명시해 ORM 상호 참조가 가능하도록 합니다.
- **어댑터 계층 (`core/storage.py`)**: `StorageConfig`에서 엔진과 세션 팩토리를 초기화하고, `Storage` 클래스에서 다음과 같은 메서드를 제공합니다.
  - `create_goal`, `add_metric`, `update_motivation`, `finalize_goal`
  - `get_user_preferences`, `save_user_preferences`, `get_player_progress`, `update_player_progress`
  - `create_quest`, `list_recent_quest_logs`, `log_quest_event`
  - `log_conversation`, `create_conversation_summary`
  - `create_reminder`, `list_reminders_due`
- **세션 관리**: 컨텍스트 매니저(`session_scope`)로 트랜잭션을 안전하게 묶고, 테스트 환경에서는 `sqlite:///:memory:` 구성을 사용합니다.
- **에러/검증 정책**: 필수 값 누락 시 명확한 예외를 던지고, 파이썬 데이터 클래스를 사용해 입력을 검증할 계획입니다.

## 5. 개발 및 테스트 전략

- **테스트 주도 개발 (TDD):** `core` 디렉토리의 기능은 TDD 방식으로 개발합니다. 실패하는 테스트부터 작성하고 이를 통과시키는 코드를 구현합니다.
- **단위 테스트:** 목표 생성, 메트릭 추가, 동기 설정 등 핵심 기능이 독립적으로 정확히 동작하는지 검증합니다.
- **CI 연동:** GitHub Actions에서 `lint`, `typecheck`, `pytest`, `golden-check` job을 분리해 실행합니다. 네 가지 상태 모두 초록불일 때만 브랜치 머지가 가능하도록 브랜치 보호 규칙을 설정합니다.

## 6. GPT 연동 현황과 교훈

- **현재 상태:** `GOALER_USE_MOCK=false`로 실행하면 GPT 모델이 실제로 `create_goal → create_quest → complete_quest → finalize_goal` 순서로 함수를 호출합니다. 사용자는 대부분 퀘스트 완료 버튼만 누르면 되고, 필요한 경우에만 고급 옵션을 통해 숫자형 지표를 추가 설정합니다.
- **Mock 모드:** 기본값은 mock 모드입니다. 덕분에 네트워크가 막혀 있어도 언제든지 흐름을 시연하거나 테스트할 수 있습니다.
- **교훈:** 초기에 다른 모델(Gemini 등)을 검토했지만 라이브러리 안정성이 떨어졌습니다. 반면 OpenAI SDK는 툴 호출 포맷만 정확히 맞추면 안정적으로 응답을 반환하므로, 현재 구조는 GPT 계열 모델을 전제로 설계되어 있습니다.

## 7. 앞으로의 진화 방향

1. **경험 확장:** CLI 기반 데모를 웹/모바일 UI나 메시징 챗봇으로 옮겨 사용자가 목표 카드를 시각적으로 확인할 수 있게 만듭니다.
2. **지속 저장:** 지금은 인메모리 상태이므로, 목표를 DB나 파일에 저장해 다시 접속했을 때 이어서 대화할 수 있도록 합니다.
3. **코칭 콘텐츠 강화:** 목표 유형별 질문 템플릿, 행동 제안, 주간 피드백 루틴 등을 추가하면 “코치”라는 색깔이 더 선명해집니다.
4. **자동 리마인더:** MVP에서는 Slack Webhook을 통해 주기별 알림을 보내고, 정식 서비스 단계에서는 앱 푸시·이메일·문자 등 다중 채널을 지원합니다. 알림 주기·시간대는 챗봇이 대화 중 함수 호출로 저장하거나, 추후 앱 UI에서 사용자가 직접 변경할 수 있도록 설계합니다. MVP 메시지는 목표 설명·남은 기간·최근 완료한 퀘스트·다음 추천 행동을 항상 포함하며, 향후에는 LLM이 맥락을 분석해 응원/퀘스트/동기 문구를 선택적으로 조합합니다.

## 8. 코칭 철학과 장기 목표 지원

- Goaler는 단순한 일상 습관뿐 아니라 “1년 뒤 마라톤 완주”, “1년 안에 사이드 프로젝트로 월 매출 100만 원” 같은 **장기·비전형 목표**를 포기하지 않고 달성하도록 돕는 데 초점을 둡니다.
- 심리학/게이미피케이션 요소를 도입해 목표 진행률을 게임처럼 느끼도록 설계합니다. 예: 단계별 퀘스트, 주간 리포트, 축하 메시지 등.
- 인터뷰 질문(`CLARIFIERS.md`), 시스템 프롬프트, 테스트 시나리오가 이러한 철학을 공유하도록 문서를 지속적으로 보강합니다.
- 금전적 보상이나 인증 부담을 줄여 “스스로 성장하는 감정”을 훼손하지 않도록 하며, 보상은 정서적/인지적 지원(칭호, 난이도 조절, 스토리)으로 제한합니다.

## 9. 심리학 · 게임 디자인 기준

- **자기결정성이론(SDT)**: 퀘스트 선택권과 난이도 조절, 칭찬/응원 메시지로 자율성·유능감·관계성을 만족시킨다.
- **목표 경사 가설**: 대시보드·리마인더에서 남은 퀘스트 수와 진척률을 강조해 “조금만 더” 하고 싶게 만든다.
- **Implementation Intentions**: 퀘스트 생성 시 “언제/어디서/어떻게”를 되묻고 저장해 실행 장벽을 낮춘다.
- **변동 보상 루프**: 퀘스트 완료 시 칭찬, 연속 출석 보상, 주간 회고 리포트로 즉각적인 도파민 루프를 제공한다.
- **레벨링 & 온보딩 전략**: 초기에는 쉬운 퀘스트와 빠른 보상을 제공하고, 이후 레벨·칭호·확장 퀘스트를 점진적으로 공개한다. Duolingo, Ring Fit Adventure 등의 레벨링 방법론을 지속적으로 벤치마킹한다.

## 9. 대화 기록 관리 전략

- **원시 로그(raw logs)**: 모든 발화를 `conversation_logs` 테이블에 저장합니다. `conversation_id`, `role`(user/assistant/tool), `content`, `token_count`, `created_at` 등을 기록해 최근 맥락을 복원하고 분석에 활용합니다.
- **요약본(summaries)**: 조건이 충족되면 `conversation_summaries`에 요약 텍스트를 저장해 장기 역사를 압축합니다.
  - 토큰/메시지 기준: 누적 메시지 수 또는 토큰 수가 임계치를 넘으면 즉시 요약합니다.
  - 시간 기준: 주기적으로(예: 주간) 최근 로그를 묶어 요약합니다.
- **프롬프트 구성**: 대화 재개 시 “최신 요약 1~2개 + 직전 원시 로그 몇 개”를 투입해 자연스러운 흐름을 유지합니다.
- **보관 정책**: 오래된 원시 로그는 요약 이후 “요약됨” 상태로 표시하거나 별도 보관 테이블로 이동해 데이터 증가를 관리합니다.
- **요약 파이프라인**: 요약은 배치 워커가 담당합니다. 조건을 만족하면 `conversation_logs`에서 최근 N개의 메시지를 가져와 LLM을 호출해 요약을 생성하고, `conversation_summaries`에 저장합니다.
  - 워커는 향후 Celery/APScheduer 등으로 교체할 수 있도록 인터페이스(`summary_service.py`)를 분리합니다.
  - 요약 생성 시 메타 데이터(사용한 토큰 수, 요약 시간)를 함께 기록해 품질 모니터링에 활용합니다.

## 10. 알림/리마인더 구현 계획

- **MVP**: Slack Webhook을 사용해 목표별 리마인더를 전송합니다. `reminders` 테이블에는 채널, 주기, 다음 실행 시각과 함께 사용자가 대화에서 지정한 선호 시간대 정보를 저장합니다. 스케줄러는 이 값을 기반으로 실행되며, 챗봇은 필요 시 함수 호출로 값을 갱신합니다. 메시지 포맷은 `CONFIG.yaml` 템플릿을 참고해 목표 요약, 남은 기간, 최근 완료한 퀘스트, 다음 행동을 필수로 구성합니다.
  - 메시지 템플릿은 고정된 포맷으로 "목표 제목" · "최근 완료한 퀘스트" · "남은 기간" · "다음 액션"을 포함합니다.
- **확장 단계**: 앱 푸시 알림, 이메일, SMS 등 다중 채널을 지원합니다. 채널별 설정은 `reminders` 테이블에서 관리하며, 사용자 선호도(예: 알림 수신 여부, 시간대)를 함께 저장합니다.
- **알림 템플릿**: 장기적으로는 LLM이 목표 맥락을 바탕으로 맞춤형 메시지(치얼업, 진행률 요약, 다음 퀘스트 제안 등)를 생성하도록 설계합니다. MVP에서는 정해진 메시지 포맷, 확장 단계에서는 LLM이 메시지 유형을 자동 선택하도록 룰을 보강합니다.
- **알림 파이프라인**: 스케줄러(예: APScheduler)가 `reminders` 테이블에서 `next_run_at`이 지난 항목을 조회해 Slack Webhook으로 메시지를 보냅니다. 발송 후 `next_run_at`을 업데이트하고, 향후 Push/SMS 채널 확장을 위해 메시지 생성 로직과 전송 로직을 분리합니다.

## 11. 인증/보안 기본 방침

- MVP에서는 단일 테스트 사용자를 사용하되, SQLite 스키마에 `users`/`conversations` 테이블을 준비해 OAuth 도입 시 손쉽게 확장할 수 있도록 합니다.
- 구글/카카오 OAuth를 사용해 "provider_type + provider_id" 조합으로 사용자를 식별하고, 내부적으로는 `user_id`(UUID)를 발급합니다.
- 민감한 비밀번호를 저장하지 않고도 인증이 가능하므로 보안 부담을 줄일 수 있지만, 토큰 저장·통신 암호화·접근 제어 등 기본 보안 수칙은 반드시 준수합니다.
- 향후 배포 시 Privacy Policy와 데이터 처리 방침을 명시하고, Slack Webhook/DB 자격 증명은 환경 변수로 관리합니다.

## 12. 구현 단계 및 테스트 전략

1. **모델 계층 구현**: `core/models.py`에 SQLAlchemy 모델을 정의하고, SQLite 인메모리 환경에서 `goals/quests/quest_logs` 스키마 생성 테스트(`tests/test_models.py`)를 작성합니다.
2. **저장소 어댑터 구축**: `core/storage.py`에서 컨텍스트 매니저 및 CRUD 메서드를 구현하고, `tests/test_storage.py`로 목표/퀘스트/리마인더 CRUD를 검증합니다. (고급 사용자를 위한 `metrics` CRUD는 선택 테스트로 분리)
3. **StateManager 통합**: 기존 인메모리 로직을 유지하되, 퀘스트 생성·완료 이벤트를 저장소 어댑터와 연동합니다. 통합 테스트(`tests/test_e2e_conversation.py`)에 DB 백엔드 사용 케이스를 추가합니다.
4. **요약·알림 워커 설계**: 대화 요약 생성기와 리마인더 스케줄러에 대한 스텁을 만들고, 후속 단계에서 실제 작업자(예: Celery, APScheduler)를 붙일 수 있도록 인터페이스를 정의합니다.
5. **CI 강화**: DB 관련 테스트는 SQLite 인메모리를 사용하고, 필요 시 PostgreSQL을 Docker 서비스로 추가해 호환성 테스트를 진행합니다.
