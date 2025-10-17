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
- (계획) `core/models.py`: SQLAlchemy 모델 정의. 현재는 저장소 계층에서 직접 스키마를 참조하며, 향후 모델 클래스를 도입할 예정입니다.
- `core/storage.py`: 현재는 인메모리에서 보스전/퀘스트/전리품 로그를 관리하며, 향후 영속 저장소 어댑터로 교체할 수 있도록 설계되었습니다.
- `tests/test_core.py`, `tests/test_e2e_conversation.py`: 단위 테스트와 통합 테스트로 로직이 예상대로 움직이는지 검증합니다.

## 테스트
```bash
PYTHONPATH=. pytest
```

## 데이터 저장 전략
- **MVP**: SQLite를 기본 저장소로 사용합니다. 별도 서버가 필요 없고 파일 하나로 목표·메트릭·대화 기록(선택)을 영구 보관할 수 있습니다.
- **확장 단계**: PostgreSQL 등 서버형 DB로 전환할 수 있도록 구조를 분리해 두었습니다. 환경 변수로 연결 문자열만 바꾸면 마이그레이션이 가능합니다.

저장 예상 테이블 및 경로 정책
- 기본 DB 파일: `data/goaler.db` (환경 변수 `GOALER_DATABASE_URL`로 경로/엔진 재정의 가능)
- ORM 어댑터: SQLAlchemy 기반(`core/storage.py`)으로 SQLite/PostgreSQL을 동일 인터페이스로 사용
- `users`: OAuth 공급자 타입/ID, 닉네임 등 사용자 메타 정보
- `conversations`: 사용자별 대화 세션 상태
- `goals`: 목표 메타 정보(제목, 유형, 기한, 동기 등)
- `metrics`: 목표별 측정 지표(목표값, 단위, 초기값, 진행률) ※ `metric_name`, `metric_type`, `target_value`, `unit`은 필수이며, `initial_value`, `progress`, `updated_at`을 함께 관리합니다. (진행률과 시각은 수동/자동 갱신 모두 지원 예정)
- `conversation_logs`: 원시 대화 히스토리(누적 토큰/메시지 기준으로 요약 트리거)
- `conversation_summaries`: 주기별 대화 요약본
- `reminders`: 알림/리마인더 설정(채널, 주기, 다음 실행 시각 및 선호 시간대)

## 로드맵
1. **지속 저장소 고도화**: `StateManager`와 분리된 저장소 모듈을 도입해 SQLite→PostgreSQL 전환을 지원합니다.
2. **경험 확장**: 웹/모바일 UI 혹은 메시징 봇(슬랙 등)으로 챗봇을 옮겨 목표 진행 상황을 시각화합니다.
3. **장기 목표 코칭**: 장기 목표를 작은 단계로 쪼개고, 심리학·게이미피케이션 요소(주간 리포트, 축하 메시지 등)를 챗봇 응답에 녹입니다.
4. **알림/리마인더 연동**: MVP는 Slack Webhook으로 고정 포맷(목표 제목 + 현재 진행률 + 남은 기간 + 다음 액션)을 보내고, 확장 단계에서는 LLM이 메시지 유형(치얼업, 퀘스트 제안 등)을 자동 생성하며 앱 푸시·이메일·SMS로 확장합니다. 주기·시간대는 챗봇 대화나 앱 UI에서 사용자가 직접 지정할 수 있습니다.
5. **운영·보안 강화**: 인증/권한, 배포 파이프라인, 브랜치 보호 규칙을 정교하게 유지합니다.

## 인증 계획
- MVP에서는 테스트용 단일 사용자를 사용하되, DB 스키마에 `users`/`conversations` 테이블을 준비해 둡니다.
- 정식 서비스에서는 구글/카카오 OAuth를 사용해 사용자 식별을 처리하고, 내부적으로는 `user_id`(UUID)만 저장합니다.
- OAuth 토큰·환경 변수는 서버 측 안전한 저장소에 보관하고, HTTPS 통신 및 기본 보안 정책(토큰 만료, 접근 제어)을 준수합니다.

## 설계 참고 문서
- `ARCHITECTURE.md`: 저장소·알림·요약 전략과 구현 단계, 테스트 계획을 상세히 정리했습니다.
- `CLARIFIERS.md`: 챗봇 인터뷰 질문 템플릿입니다.
- `docs/PRODUCT_SPEC.md`: 질문별 현재 답변/결정 사항을 정리한 문서입니다.
- `docs/UX_FLOW.md`: UX 및 화면 구성 템플릿입니다.
- `docs/RISK_REGISTER.md`: 리스크 식별·완화 계획 템플릿입니다.
- `docs/DATA_FLOW.md`: 데이터 이벤트 흐름 및 외부 연동 계획 템플릿입니다.
- `docs/BOSS_DESIGN_GUIDE.md`: 핵심 단계(보스전) 정의와 질문 가이드입니다.
- `docs/COACH_TONE_GUIDE.md`: AI 코치의 말투/응답 패턴 가이드입니다.
- `docs/LOOT_REPORT_TEMPLATE.md`: 월간/분기 전리품 리포트 구조를 정의합니다.
- `docs/LLM_USAGE_GUIDE.md`: LLM 모델 사용 전략과 비용 모니터링 지침입니다.
- `VIBECODE_ENTRY.md`: CLI가 프로젝트를 재생성할 때 사용할 템플릿과 정책을 포함합니다.

## 추가 도구
- `python tools/preflight.py --entry VIBECODE_ENTRY.md --init-lock-if-missing --check-secrets`
- `python tools/generate_loot_report.py --period monthly`
