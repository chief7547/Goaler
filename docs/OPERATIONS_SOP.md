# Operations SOP (Launch Hardening)

> 목적: Phase 5 이후 실서비스 운영 시 개발자/운영자가 동일한 기준으로 대응할 수 있도록 체크리스트와
> 절차를 문서화한다. 장애 대응, 스케줄러 운용, 백업·복원 프로세스를 포함한다.

## 1. 서비스 가동 전 점검
- `.env`에 `OPENAI_API_KEY`, `GOALER_DATABASE_URL`, `LOOT_REPORT_OUTPUT_DIR` 등 필수 값 설정
- Redis를 사용하는 경우 `GOALER_STATE_REDIS_URL`을 설정해 대화 상태가 인스턴스 재시작에도 유지되는지 확인
- LLM 한도 환경 변수(`LLM_MAX_*`, `LLM_LIMIT_REACHED_MESSAGE`)가 목표치에 맞게 설정되었는지 확인
- `alembic upgrade head` 로 마이그레이션을 최신 상태로 맞춘 뒤 결과 로그를 보관
- `GOALER_ACTIVE_USER_ID`가 배포 환경의 실제 사용자/세션 ID로 설정되었는지 검증
- `python tools/report_worker.py --period monthly --cron "0 9 * * *" --verbose` 로 스케줄러 드라이런
- `GOALER_USE_MOCK=false python app.py` 로 실전 모드 스모크 테스트 수행 (목표 생성 → 퀘스트 완료 → 전리품 기록)
- CI 대시보드 확인: lint/typecheck/pytest/coverage/golden-check 5가지가 녹색인지 확인
- 워커 재시도 설정(`REPORT_WORKER_RETRIES`, `REPORT_WORKER_RETRY_DELAY`)과 잠금 파일(`logs/report_worker.lock`) 관리 정책 점검
- Redis 사용 시 `LLM_REDIS_URL`, `REPORT_WORKER_REDIS_URL` 연결 테스트 및 TTL 설정 확인

## 2. 일일/주간 루틴
| 빈도 | 수행 항목 | 참고 |
| --- | --- | --- |
| 매일 | `logs/report_worker.log`, `logs/llm_usage.log` 확인, 오류 발생 시 재시도 | `docs/LOOT_REPORT_WORKFLOW.md` |
| 매일 | 대화 로그 요약 워커 실행(`ConversationSummarizer`) 후 요약 생성 여부 확인 | `docs/DATA_FLOW.md` |
| 매주 | DB 백업(`sqlite3 data/goaler.db .backup data/backups/YYYY-MM-DD.db`) 후 무결성 검증 | `docs/RISK_REGISTER.md` |
| 매주 | 토큰 사용량 집계(`python tools/generate_loot_report.py --period monthly --usage-log logs/llm_usage.log`)로 비용 체킹 | `docs/ANALYTICS_PLAN.md` |
| 분기 | Stage 승급/강등 로직 튜닝 회고, `docs/COACH_TUNING_BACKLOG.md` 업데이트 |  |

## 3. 장애 대응 프로토콜
1. **감지**: Slack 경고 또는 `logs/report_worker.log`에 `ERROR` 감지 → 즉시 `incident-YYYYMMDD.md` 템플릿 작성
2. **초응답**
   - 목표 데이터 손실 → 즉시 읽기 전용 모드(`GOALER_USE_MOCK=true`) 전환, 최신 백업으로 복구
   - LLM API 장애 → `GOALER_USE_MOCK=true` 설정 후 코치 응답을 템플릿 캐시로 전환
3. **조치**
   - DB 복구: `sqlite3 data/goaler.db ".restore data/backups/latest.db"`
   - 스케줄러 재기동: `pkill -f report_worker.py` 후 `python tools/report_worker.py --cron ...` 재실행
4. **사후 처리**
   - `docs/RISK_REGISTER.md` 상태 업데이트 및 재발 방지 액션 기록
   - 운영 Slack에 회고 공유 (문제 요약, 영향도, 해결책, 다음 액션)

## 4. 백업/복원 체크리스트
- 자동 백업 스크립트: `cron`으로 `00 02 * * * sqlite3 data/goaler.db .backup data/backups/$(date +\%F).db`
- 보존 정책: 최근 7개 일일 백업 + 최근 3개 주간 백업 유지
- 복원 절차
  1. 사용자 통지 → 서비스 일시 중단 알림
  2. 최신 백업을 staging DB에 복원해 무결성 확인
  3. 본 DB 복원 → smoke 테스트 → 서비스 재개 안내

## 5. 알림 채널 설정
- Slack: `.env`에 `SLACK_BOT_TOKEN`, `SLACK_CHANNEL` 지정 (봇을 채널에 초대 필요), 메시지 템플릿은 `docs/ALERT_TEMPLATES.md`
- Email/SMS: Phase 5 확장 스코프, Postmark/Twilio 후보. 채널 추가 시 `reminders` 테이블 `channel` enum 업데이트
- 실패 재시도: 5분 후 3회 재시도, 모두 실패 시 운영 Slack `#goaler-alerts`로 알림

## 6. 개인정보 요청 대응
- 감정 메모(`mood_note`)는 저장 전 자동 마스킹되며, 운영팀은 노출된 로그를 두 번 확인한다.
- 사용자 삭제/열람 요청이 들어오면 ① `conversation_logs` → ② `conversation_summaries` → ③ `reports/` 순으로 데이터를 제거하고, 처리 결과를 24시간 이내 사용자에게 회신한다.
- 민감 로그가 탐지되면 즉시 Slack `#goaler-privacy` 채널에 공유하고, 72시간 내 재발 방지 조치를 문서화한다.

## 7. 데이터베이스 동시성 · 마이그레이션 계획 (P6 사전 준비)
- SQLite는 APScheduler 워커와 CLI/앱이 동시에 쓰기 작업을 수행하면 `database is locked` 오류가 발생할 수 있다. 단기적으로는 `timeout` 파라미터와 재시도 래퍼를 두되, Phase 6(운영 개선)에서 PostgreSQL로 이전하는 것을 필수로 한다.
- PostgreSQL 전환 시도 전 체크리스트
  1. `GOALER_DATABASE_URL`을 Postgres 호스트로 지정하고 연결 테스트
  2. SQLAlchemy 세션팩토리의 `pool_size`, `max_overflow` 등을 환경에 맞춰 조정
  3. 백업/복원 절차를 PostgreSQL 버전으로 갱신하고, 장애 훈련을 시행
- 스키마 변경을 안전하게 수행하기 위해 Alembic을 도입한다. (예: `alembic revision --autogenerate -m "add column"`, `alembic upgrade head`) 배포 전에는 반드시 마이그레이션 스크립트를 검토한다.
- `docs/DEVELOPMENT_PLAYBOOK.md` Phase 6에 “PostgreSQL 전환 + Alembic 도입” 작업을 명시하고, 책임자/일정을 추적한다.
- 감사 백로그 반영: QuestLog 인덱스 추가, LLM 쿼터 외부 저장소, `default_user` 제거, 스케줄러 재시도/분산 락 설계를 진행하면서 본 SOP와 리스크 레지스터를 동기화한다.

## 6. 문서 히스토리
- 2025-02-20: 초기 SOP 초안 작성 (cli)
- YYYY-MM-DD: TBD

운영 절차 변경 시 본 문서를 우선 업데이트하고, 관련된 `docs/RISK_REGISTER.md`, `docs/DEVELOPMENT_PLAYBOOK.md` 체크리스트도 함께 조정한다.
