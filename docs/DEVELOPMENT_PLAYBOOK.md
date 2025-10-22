# Development Playbook

> 목적: Goaler를 “문서→코드→운영” 순으로 일관되게 구현하기 위한 단계별 지침서. CLI 혹은 신규 팀원이
> 이 문서 하나만 보고도 모든 필수 산출물과 검증 절차를 빠짐없이 수행하도록 구성했다.

## 0. 전체 구조
- **Phase 0: Groundwork** – 환경/의존성/Manifest 검증
- **Phase 1: Core MVP Loop** – Mock 모드에서 목표→퀘스트→전리품 루프 구현
- **Phase 2: Boss Stage & Variation** – 보스전 분해, 주간/일일 계획, 변주 시스템
- **Phase 3: Coach Persona** – AI 톤, 시간대/데이터 기반 응답, 전리품 대화
- **Phase 4: Reports & Analytics** – 전리품 리포트, LLM 비용 추적, ETL 파이프라인
- **Phase 5: Launch Hardening** – 비동기 워커, 알림 확장, 보안/운영 체계

각 Phase에는 다음 요소가 반복된다.
1. **Inputs** – 착수 전 준비물, 참고 문서
2. **Tasks** – 순차적으로 수행해야 할 세부 작업
3. **Quality Gates** – 단계 종료 전 반드시 통과해야 할 조건
4. **Artifacts** – 생성/수정되어야 할 파일 및 기록
5. **Hand-off Checklist** – 다음 Phase로 넘어가기 위한 승인 항목

문서 간 교차 참조는 괄호로 명시된다. 예: (`docs/UX_FLOW.md §2`).

---

## Phase 0 — Groundwork & Environment
**목표:** 프로젝트 뼈대가 기준 문서와 동일한 상태인지 검증하고 CI를 준비한다.

### Inputs
- `README.md` (빠른 시작, 도구 명령)
- `VIBECODE_ENTRY.md` (manifest 요구사항)
- `.github/workflows/ci.yml`

### Tasks
1. **환경 구성**  
   - `python -m venv .venv`  
   - `source .venv/bin/activate` (또는 Windows 스크립트)  
   - `pip install -r requirements.txt -r requirements-dev.txt`
2. **Manifest 검증**  
   - `python tools/preflight.py --entry VIBECODE_ENTRY.md --init-lock-if-missing --check-secrets`
   - 누락 파일 생성 여부 확인 (`required_files` 항목)
3. **CI Dry-run**  
   - `flake8 .`, `pytest`를 로컬에서 실행  
   - Mock 모드 기본 설정(`GOALER_USE_MOCK=true`) 확인

### Quality Gates
- `tools/preflight.py`가 오류 없이 종료
- `pytest` 기본 세트 통과 (`tests/test_core.py`, `tests/test_schema.py` 등)
- 워킹 디렉토리 `git status` clean

### Artifacts
- `.venv/` (로컬)  
- `audit/manifest.lock` (필요 시)

### Hand-off Checklist
- [x] README에 기재된 “빠른 시작” 절차 완료 증빙 (`python -m venv .venv`, pip install, preflight)
- [x] CI 구성 확인 (로컬 `flake8`, `pytest` 통과 / Actions 기본 워크플로우 정상)

---

## Phase 1 — Core MVP Loop (Mock)
**목표:** LLM 없이도 목표 생성 → 일일 퀘스트 → 전리품 기록이 되는 CLI MVP를 만든다.

### Inputs
- `core/agent.py` (기본 메서드), `core/state_manager.py`
- `app.py` (mock 루프)
- `tests/test_core.py`, `tests/test_e2e_conversation.py`
- `docs/UX_FLOW.md §1~3`, `docs/PRODUCT_SPEC.md Q1~Q16`

### Tasks
1. **GoalSettingAgent 기본 기능 확립**  
   - `create_goal`, `add_metric`, `set_motivation`, `finalize_goal` 구현/검증  
   - StateManager가 dict 기반으로 상태를 유지 (`docs/AGENT_DESIGN.md §2`).
2. **Mock Loop 실행**  
   - `python app.py` 실행 후 CLI에서 목표→퀘스트 입력 흐름 테스트  
   - Mock 모드 메시지가 README 예시와 일치하는지 확인.
3. **전리품 입력 최소형**  
   - Stage 0에서는 칭찬 메시지와 다음 퀘스트 안내만 노출한다(`docs/ONBOARDING_PLAN.md`).
   - 해금 이후 사용자가 퀘스트 완료 후 “전리품 유형(성과/깨달음/느낌) 칩”을 탭하는 것만으로 기록할 수 있도록 CLI 루틴 추가(텍스트 입력은 선택 사항).
4. **테스트 강화**  
   - `tests/test_core.py`에 기본 상태 검증이 포함되어 있는지 확인  
   - `pytest tests/test_core.py tests/test_e2e_conversation.py` 통과.

### Quality Gates
- CLI에서 목표 생성→전리품 기록까지 시뮬레이션 성공 (수동 테스트 로그 남기기)
- Mock 모드 전용 테스트 모두 통과

### Artifacts
- 초기 사용자 스토리 시연 기록(스크린샷/터미널 로그) → `reports/mock_loop_stage0.log`

### Hand-off Checklist
- [x] Mock 루프 시연 결과 공유 (`app.py` Stage 0 대화 흐름 정비)
- [x] 테스트 커버리지 보고 (`coverage run -m pytest` → 86% 보고)
- [x] Stage 0 온보딩 플래그가 정상 동작하는지 확인 (전리품/에너지 기능 숨김)

---

## Phase 2 — Boss Stage Planning & Daily Variation
**목표:** 현실 과업을 보스전으로 정의하고, 주간/일일 준비와 일일 변주 시스템을 구현한다.

### Inputs
- `DATA_SCHEMA.yaml` (`boss_stages`, `quest_logs` 구조)
- `docs/BOSS_DESIGN_GUIDE.md`, `docs/BOSS_STAGE_EXAMPLES.md`
- `docs/UX_FLOW.md §1.2`, `docs/DATA_FLOW.md §1`
- `docs/AGENT_DESIGN.md` (보스전 관련 도구: `define_boss_stages`, `propose_weekly_plan`, `propose_daily_tasks`)
- `docs/TEST_PLAN.md` Phase 2 시나리오

### Tasks
1. **보스전 데이터/스토리지 구현**  
   - `boss_stages` CRUD 추가 (`core/storage.py`)  
   - 샘플 보스전 생성 스크립트 또는 테스트 작성 (`docs/BOSS_STAGE_EXAMPLES.md` 참조)
   - 온보딩 단계에 따라 용어가 “보스전/핵심 마일스톤”으로 변경되는지 확인
2. **LLM Toolchain 확장**  
   - `GoalSettingAgent`에 새 도구 호출 연결  
   - 사용자가 보스전/주간/일일 단계를 확정하는 질문 흐름 구현
3. **일일 변주 로직**  
   - `quest_logs`에 `loot_type`, `energy_status`, `llm_variation_seed` 저장  
   - LLM `reason`이 변주 이유(보스 준비, 회복 등)를 설명하도록 프롬프트 보완
   - Stage 0에서는 변주 모달을 표시하지 않도록 UI/상태 가드 추가
4. **UX 반영**  
   - 텍스트 와이어프레임(`docs/wireframes/boss_timeline.md`, `dashboard.md`)과 데이터 필드 일치 여부 검토
5. **테스트**  
   - 보스전 생성→주간 계획→일일 변주까지의 통합 테스트 추가 (`docs/TEST_PLAN.md §2`)
   - 온보딩 단계별 기능 해금 시나리오(Stage 0→0.5→1→1.5) 포함
    - `tests/conftest.py`에서 Sqlite 인메모리 세션/스토리지를 fixture로 제공해 테스트 격리 확보

### Quality Gates
- 보스전 정의 → 주간 단계 → 일일 변주가 시뮬레이션에서 정상 동작
- `pytest`에 새 시나리오 포함, CI 통과

### Artifacts
- 보스전 포함 e2e 대화 로그 1개 이상 (PR 첨부) → `tests/test_e2e_conversation.py` Phase 2 스텁 반영
- `tests/test_core.py`에 `define_boss_stages`/`propose_weekly_plan`/`propose_quests` 시나리오 추가

### Hand-off Checklist
- [x] 보스전 1개 이상 성공/실패 루프 테스트 (정렬·실패 처리 시나리오)
- [x] 변주 reason이 로그에 남는지 확인 (`test_propose_quests_after_unlock_returns_variations`에서 reason 확인)
- [x] 온보딩 상태에 따라 노출 기능이 달라지는지 확인 (`test_propose_quests_locked_until_loot_unlocked`)

---

## Phase 3 — Coach Persona & Tone Refinement
**목표:** AI 코치가 사용자 성향과 상태에 맞춰 자연스러운 톤과 대사를 제공.

### Inputs
- `core/agent.py` (SYSTEM_PROMPT)
- `docs/COACH_TONE_GUIDE.md`, `docs/DAILY_PROMPT_TEMPLATES.md`
- `docs/BOSS_STAGE_EXAMPLES.md` (맥락 예시)

### Tasks
1. **프롬프트 업데이트**  
   - 시간대(아침/점심/저녁), 전리품 유형, 에너지 상태 별 조건 반영  
   - Boss stage 상황(`READY_FOR_BOSS`, `NEEDS_POTION`)에 따른 대사 변화 구현
2. **응답 템플릿 정비**  
   - `docs/RESPONSE_TEMPLATES.md`에 축하/감정 공감/회복 문구를 정리하고, LLM 호출 전 템플릿을 우선 탐색하도록 구현 (`core/coach.py`)  
   - 동일 템플릿 반복을 방지하기 위해 최근 사용 목록 캐시
3. **샘플 대화 작성**  
   - 각 성향(`challenge_appetite`)별 트랜스크립트 생성  
   - 월간 보고서/전리품 회고 예시 대화 작성
4. **수동 검증**  
   - Mock 모드에서 대사를 확인하고, “전리품 덱”, “회복 루틴” 등의 키워드가 자연스럽게 쓰이는지 평가

### Quality Gates
- 최소 3가지 사용자 프로필(도전적/안정형/회복 모드)에 대한 대화 로그 준비
- 리뷰어(또는 본인) 확인 코멘트 기록

### Artifacts
- 샘플 대화 로그 (docs/ 또는 PR 첨부) → `docs/COACH_SAMPLE_DIALOGUE.md`, `tests/test_coach.py`

### Hand-off Checklist
- [x] 톤 가이드와 실제 응답이 일치하는지 확인 (CoachResponder + compose_coach_reply)
- [x] 향후 튜닝 포인트(To-do) 목록 업데이트 (`docs/COACH_TUNING_BACKLOG.md`)

---

## Phase 4 — Loot Report & Analytics
**목표:** 전리품 데이터를 리포트로 변환하고, LLM 비용/지표를 수집한다.

### Inputs
- `docs/LOOT_REPORT_TEMPLATE.md`, `docs/LOOT_REPORT_WORKFLOW.md`
- `tools/generate_loot_report.py`
- `docs/LLM_USAGE_GUIDE.md`, `app.py` (usage 로그)
- `docs/ANALYTICS_PLAN.md`

### Tasks
1. **LLM 사용 로깅 검증**  
   - 실제 LLM 호출 후 `logs/llm_usage.log` 생성 확인  
   - 샘플 집계 스크립트(토큰 합계) 작성
2. **전리품 리포트 생성**  
   - `python tools/generate_loot_report.py --period monthly` 실행  
   - mock 데이터 → `/reports/`에 결과 저장  
   - 실제 데이터 연결(스토리지/ETL) TODO 기록
3. **분석 파이프라인 설계**  
   - ETL에서 일별 스냅샷 생성(토큰/경고/전리품 수)  
   - 분석 대시보드 설계 음성(예: Superset/Metabase)
4. **알림 설정**  
   - Slack/Email 알림 메시지 초안 작성  
   - 경고 조건(토큰 초과, 휴식 신호 반복)을 알림과 연결

### Quality Gates
- 전리품 리포트 파일 예시 및 알림 메시지 초안
- 토큰 사용량 로깅이 최소 1회 이상 검증됨

### Artifacts
- `reports/SAMPLE_MONTHLY_REPORT.md`
- 토큰 비용 집계 스크립트(예: notebooks or tools/)

### Hand-off Checklist
- [x] 관리자용 비용/성장 지표 대시보드 설계안 공유 (`docs/ANALYTICS_PLAN.md`)
- [x] 리포트 자동화 계획(PRD/티켓) 생성 (`tools/report_worker.py` 스케줄링 스텁)

---

## Phase 5 — Launch Hardening & Scale-out
**목표:** 실서비스 런칭을 위한 운영/보안/확장 준비.

### Inputs
- `ARCHITECTURE.md` (알림/요약/워커 설계)
- `docs/DATA_FLOW.md`, `docs/RISK_REGISTER.md`
- README (실전 모드, 인증 계획)

### Tasks
1. **실전 모드 전환**  
   - `.env`에 API 키 설정, `GOALER_USE_MOCK=false` 실행  
   - OpenAI 호출/에러 처리 확인, 비용 로그 점검
2. **비동기 워커 도입**  
   - APScheduler로 요약/알림 처리 (`tools/report_worker.py`)  
   - 워커 헬스체크, 재시도 로직 구현 → `logs/report_worker.log` 확인 루틴 정리
3. **알림 채널 확장**  
   - Email/SMS 템플릿, 사용자 설정 UI 준비 (`docs/ALERT_TEMPLATES.md`)  
   - 알림 실패 시 재시도 및 관리자 알림 경로 정의
4. **모니터링/경보 설정**  
   - 로그/지표/토큰 비용 대시보드 설정  
   - 경고 조건(Alert) 정의 (`docs/RISK_REGISTER.md`, `docs/OPERATIONS_SOP.md` 기반)
5. **보안/백업**  
   - Secrets Vault, DB 백업 자동화, 개인정보 보존 정책 수립
6. **리포트 워커 자동화**  
   - APScheduler 기반 `tools/report_worker.py` 스케줄러로 월간/주간 리포트, 알림을 자동 실행
   - 실행 내역 및 성공/실패 로그를 중앙화하고 재시도 전략 정의
7. **리포트 요약 프롬프트 고도화**  
   - `core/coach.py`에 리포트 전용 SYSTEM_PROMPT를 정의하고 LLM 호출 시 사용
### Quality Gates
- 실제 사용자 대상으로 베타/도그푸드 테스트 실시(기록 남김)
- 운영 문서(SOP) 작성: 장애 대응, 백업/복원 절차 기록

### Artifacts
- `docs/OPERATIONS_SOP.md` (운영 플레이북)
- `docs/ALERT_TEMPLATES.md` (알림 채널별 템플릿)
- 보안/백업 정책 문서

### Hand-off Checklist
- [ ] 운영팀/협력자와 런칭 리허설 *(프론트엔드 및 운영 담당자 합류 후 수행)*
- [ ] Go/No-Go 체크리스트 완료 *(동일 조건)*
- [x] Phase 6 준비 계획 확정 (PostgreSQL 전환, Alembic 도입, LLM 비용 제한 정책)

---

## Phase 6 — Operational Hardening
**목표:** 초기 런칭 직후 서비스가 안정적으로 굴러가도록 데이터베이스·비용·모니터링 체계를 강화한다.

### Inputs
- `docs/DB_MIGRATION_PLAN.md` (PostgreSQL 전환 절차)
- `alembic/` 디렉터리, `alembic.ini`
- `docs/OPERATIONS_SOP.md §1~3, §7` (운영 루틴/백업/동시성 주의사항)
- `docs/LLM_USAGE_GUIDE.md`, `core/llm_limits.py` (쿼터 설정)
- `tools/report_worker.py`, `docs/LOOT_REPORT_WORKFLOW.md` (스케줄러 운용)

### Tasks
1. **PostgreSQL 전환 리허설**  
   - `.env`에 Postgres용 `GOALER_DATABASE_URL` 작성, `GOALER_AUTO_CREATE_SCHEMA=false` 확인  
   - `alembic upgrade head` 실행 → 연결/권한/마이그레이션 성공 로그 캡처  
   - `GOALER_DB_POOL_SIZE`, `GOALER_DB_MAX_OVERFLOW`로 세션 풀 파라미터 조정 후 `python app.py` 스모크 테스트
2. **Alembic 워크플로우 내재화**  
   - 스키마 변경 시 `alembic revision --autogenerate -m "<변경 설명>"` → 코드와 diff 검토  
   - `alembic history --verbose`로 마이그레이션 체인 점검, 실패 시 롤백(`alembic downgrade -1`) 리허설  
   - SOP에 명시된 백업 절차와 함께 배포 전/후 체크리스트에 Alembic 명령어 포함
3. **LLM 비용·요청 레이트리밋 구성**  
   - 한도 환경 변수(`LLM_MAX_*`, `LLM_LIMIT_REACHED_MESSAGE`)를 정의하고 기본값 문서화  
   - `pytest tests/test_llm_limits.py`로 한도 초과 시 `LLMRateLimitError`가 발생하는지 확인  
   - `GOALER_USE_MOCK=false python app.py`에서 의도적으로 임계치를 낮게 설정하여 차단 메시지 출력 로그 수집
4. **리포트 워커 운영 자동화**  
   - `python tools/report_worker.py --period monthly --verbose` 단발 실행으로 로그/Slack 통지 확인  
   - APScheduler 설치 시 `--cron "0 9 * * *"` 등으로 장기 스케줄러 기동 → `logs/report_worker.log`에 성공/실패 기록 남김  
   - 워커와 CLI가 동시에 DB를 사용할 때 잠금이 발생하면 재시도 정책을 설정하고 SOP에 갱신
5. **모니터링 및 리스크 업데이트**  
   - 핵심 로그(`logs/llm_usage.log`, `logs/report_worker.log`) 일일 점검 루틴을 SOP·Risk Register에 반영  
   - 예상되는 실패 시나리오(비용 급등, 마이그레이션 실패)를 `docs/VALIDATION_PLAN.md`와 연동해 운영 리허설 계획 수립

### Quality Gates
- PostgreSQL 환경에서 `alembic upgrade head` 및 `alembic downgrade -1` 리허설 로그 확보
- `pytest tests/test_llm_limits.py` 및 샘플 LLM 차단 시나리오 실행 결과 캡처
- `tools/report_worker.py` 실행으로 생성된 리포트/Slack 알림/로그 파일 보존
- `docs/OPERATIONS_SOP.md`, `docs/DB_MIGRATION_PLAN.md`, `docs/LLM_USAGE_GUIDE.md`에 최신 운영 절차 반영되었는지 재확인

### Artifacts
- `alembic/versions/` 마이그레이션 스크립트와 실행 로그
- `tests/test_llm_limits.py`, `logs/llm_usage.log`, `logs/report_worker.log`
- 업데이트된 운영 문서: SOP, Migration Plan, Validation Plan, Risk Register

### Hand-off Checklist
- [x] PostgreSQL 전환 및 롤백 리허설 기록 공유 (`reports/postgres_dryrun.log`)
- [ ] LLM 쿼터 파라미터와 임계치 확정 후 운영팀 합의 메모 보관
- [ ] 리포트 워커 상시 기동 절차(스케줄러/Slack 경보)가 자동화되어 있는지 운영팀과 확인

> Phase 6까지 수행한 뒤 프론트엔드·운영팀이 합류하면 `docs/VALIDATION_PLAN.md`에 따라 실제 사용자 검증을 진행한다.

---

## 감사 이후 전문 백로그 (Audit Backlog)
최종 감사에서 도출된 운영 안정화 항목은 아래 순서로 진행한다. 각 항목은 별도 티켓으로 전환해 추적한다.

1. **Quest 로그 인덱스 확장** *(완료됨)*  
   - 대상: `core/models.py`의 `QuestLog.goal_id`, `QuestLog.quest_id`  
   - 작업: SQLAlchemy 모델에 `index=True` 추가 → Alembic 마이그레이션 작성 (`0003_add_indexes_to_quest_log`)  
   - 검증: `GOALER_DATABASE_URL=sqlite:///data/alembic_ci.db alembic upgrade head` + `pytest tests/test_loot_report.py`
2. **LLM 쿼터 지속성 강화** *(DB + Redis 옵션 적용 완료)*  
   - `llm_daily_usage` 테이블로 재시작 시에도 한도가 유지되며, `LLM_REDIS_URL`을 설정하면 Redis 캐시를 병행 사용  
   - Redis 사용 여부에 따라 SOP/환경 변수(`LLM_REDIS_KEY_PREFIX`, `LLM_REDIS_TTL`)를 점검하고 모니터링을 유지한다.
3. **사용자 식별 강제**  
   - `core/agent.py` 등에서 `user_id="default_user"` 폴백 제거  
   - 인증 계층 도입 시, 미인증 요청은 게이트웨이/미들웨어에서 차단  
   - CLI mock 흐름 전용 폴백은 별도 가드로 분리
4. **스케줄러 내구성 향상** *(기본 재시도 + Redis 잠금 옵션 적용)*  
   - APScheduler 실패 재시도와 파일/Redis 기반 잠금 도입 (`REPORT_WORKER_REDIS_URL`, `REPORT_WORKER_REDIS_KEY`)  
   - 향후 트래픽 증가 시 Celery/분산 큐 전환 여부를 검토하고 필요 시 로드맵을 갱신한다.

> 위 항목은 Phase 6 이후 우선순위에 따라 진행하며, 완료 시 본 섹션을 업데이트한다.

---

## Phase 7 — Web Frontend MVP
**목표:** CLI에서 검증된 엔진을 웹 대시보드/챗 UI로 구현하고 QA까지 마친다.

### Inputs
- `docs/FRONTEND_DESIGN.md`, `docs/UX_FLOW.md`, `docs/UX_CONVO_FLOW.md`, `docs/UX_WIREFRAME_NOTES.md`
- FastAPI/Flask API 게이트웨이 스펙 (Phase FE-0 산출물)
- `docs/FX_GUIDE.md` *(애니메이션 사양 문서, FE-6에서 작성)*

### Tasks
1. **FE-0 API 게이트웨이**  
   - FastAPI/Flask로 CLI 함수를 `/api/v1/...` REST 엔드포인트로 노출  
   - 응답 스키마를 TypeScript 타입으로 자동 생성 (OpenAPI → `frontend/src/lib/api/types.ts`)  
   - Swagger 문서화, Newman/Postman 스모크 테스트
2. **FE-1 AppShell & Dashboard**  
   - Next.js App Router로 AppShell 구성 (헤더/사이드바/테마 토글)  
   - Dashboard 화면: 목표 카드, 오늘의 추천 행동, 체크리스트 표시  
   - React Query로 `GET /goals`, `GET /quests/today` 데이터 연동
3. **FE-2 Chat 통합**  
   - Chat 화면 구현 (대화 로그 + 입력 영역 + 추천 버튼)  
   - `POST /chat` 호출 → Function call 결과에 따라 React Query 캐시 무효화  
   - Optimistic update + 지연/오류 대응 UI 구성 (재시도 버튼, 토스트)
4. **FE-3 Goals & Reports**  
   - 목표 상세 페이지: 보스 타임라인, 주간 단계, 전리품 보관함  
   - 리포트 페이지: 월간/주간 조회, LLM 성장 서사, 공유 버튼  
   - Skeleton 로딩, 에러/빈 상태, 테마 전환 대응
5. **FE-4 Settings & Reminders**  
   - 알림 CRUD UI (`GET/POST/PATCH /reminders`) 및 Slack 설정 안내  
   - 알림 테스트 버튼, 토스트/모달 피드백  
   - 향후 이메일/SMS 확장을 고려한 폼 구조화
6. **FE-5 QA & Accessibility**  
   - Vitest/RTL 단위 테스트, Playwright로 핵심 사용자 플로우 검증  
   - Storybook 구축 + Chromatic 시각 회귀  
   - Lighthouse(모바일) LCP<3s, axe-core Critical=0 목표
7. **FE-6 Progressive FX**  
   - `docs/FX_GUIDE.md` 작성 (트리거/효과/정리 조건 문서화)  
   - `src/components/fx/`로 애니메이션 컴포넌트 분리, `prefers-reduced-motion` 반영  
   - Storybook에서 효과별 스토리와 QA 체크리스트 제공

### Quality Gates
- API 게이트웨이 Swagger + Newman 스모크 테스트 통과  
- 대시보드/챗/목표/리포트/알림 5개 화면 Playwright 시나리오 통과  
- Storybook에 상태/테마별 컴포넌트 문서화, Chromatic 회귀 테스트  
- 접근성: axe-core Critical 0, 키보드 내비게이션 문제 없음  
- 퍼포먼스: Lighthouse(모바일) LCP < 3s, TBT < 300ms, CLS < 0.1

### Artifacts
- `frontend/` 디렉터리 (Next.js 프로젝트) + Storybook  
- `docs/FRONTEND_DESIGN.md`, `docs/FX_GUIDE.md`  
- QA 로그 (`reports/frontend_e2e_log.md` 등)  
- 배포 가이드 (`docs/OPERATIONS_SOP.md` 업데이트)

### Hand-off Checklist
- [ ] API 게이트웨이와 프런트 타입 정의가 동일 버전(OpenAPI → TS)으로 동기화  
- [ ] 핵심 화면 5종 Playwright 스크린샷 캡처 및 QA 승인  
- [ ] Storybook 문서화/Chromatic 회귀 테스트 통과  
- [ ] `docs/FX_GUIDE.md` 초안 작성, 애니메이션 우선순위 합의  
- [ ] Vercel/Netlify 프리뷰 + Lighthouse 리포트 공유

---

## 부록 — 빠른 참조
- **설계 개요:** `ARCHITECTURE.md`, `docs/PRODUCT_SPEC.md`
- **데이터/파이프라인:** `DATA_SCHEMA.yaml`, `docs/DATA_FLOW.md`, `docs/ANALYTICS_PLAN.md`
- **보스전:** `docs/BOSS_DESIGN_GUIDE.md`, `docs/BOSS_STAGE_EXAMPLES.md`
- **코치 톤:** `docs/COACH_TONE_GUIDE.md`, `docs/DAILY_PROMPT_TEMPLATES.md`
- **전리품:** `docs/LOOT_REPORT_TEMPLATE.md`, `docs/LOOT_REPORT_WORKFLOW.md`
- **LLM 운영:** `docs/LLM_USAGE_GUIDE.md`, `logs/llm_usage.log`
- **테스트 전략:** `docs/TEST_PLAN.md`

> Playbook은 프로젝트 진행 중 새로운 기능/위험 요소가 발견될 때마다 업데이트되어야 한다.
