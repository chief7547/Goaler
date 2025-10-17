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
- [x] 테스트 커버리지 보고 (`coverage run -m pytest` → 81% 보고)
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

### Quality Gates
- 보스전 정의 → 주간 단계 → 일일 변주가 시뮬레이션에서 정상 동작
- `pytest`에 새 시나리오 포함, CI 통과

### Artifacts
- 보스전 포함 e2e 대화 로그 1개 이상 (PR 첨부) → `tests/test_e2e_conversation.py` Phase 2 스텁 반영
- `tests/test_core.py`에 `define_boss_stages`/`propose_weekly_plan`/`propose_quests` 시나리오 추가

### Hand-off Checklist
- [x] 보스전 1개 이상 성공/실패 루프 테스트 (`test_define_boss_stages_persisted_and_sorted`, `test_log_quest_outcome_handles_failure`)
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
   - `docs/RESPONSE_TEMPLATES.md`에 축하/감정 공감/회복 문구를 정리하고, LLM 호출 전 템플릿을 우선 탐색하도록 구현  
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
- 샘플 대화 로그 (docs/ 또는 PR 첨부)

### Hand-off Checklist
- [ ] 톤 가이드와 실제 응답이 일치하는지 확인
- [ ] 향후 튜닝 포인트(To-do) 목록 업데이트

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
- `/reports/sample-user-monthly-YYYY-MM-DD.md`
- 토큰 비용 집계 스크립트(예: notebooks or tools/)

### Hand-off Checklist
- [ ] 관리자용 비용/성장 지표 대시보드 설계안 공유
- [ ] 리포트 자동화 계획(PRD/티켓) 생성

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
   - APScheduler/Celery로 요약/알림 처리  
   - 워커 헬스체크, 재시도 로직 구현
3. **알림 채널 확장**  
   - Email/SMS 템플릿, 사용자 설정 UI 준비  
   - 알림 실패 시 재시도 및 관리자 알림
4. **모니터링/경보 설정**  
   - 로그/지표/토큰 비용 대시보드 설정  
   - 경고 조건(Alert) 정의 (`docs/RISK_REGISTER.md` 기반)
5. **보안/백업**  
   - Secrets Vault, DB 백업 자동화, 개인정보 보존 정책 수립

### Quality Gates
- 실제 사용자 대상으로 베타/도그푸드 테스트 실시(기록 남김)
- 운영 문서(SOP) 작성: 장애 대응, 백업/복원 절차 기록

### Artifacts
- 운영 플레이북, 알림 채널 설정 문서, 보안/백업 정책 문서

### Hand-off Checklist
- [ ] 운영팀/협력자와 런칭 리허설
- [ ] Go/No-Go 체크리스트 완료

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
