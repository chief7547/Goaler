# Goaler Risk Register (Template)

> CLARIFIERS.md Q17~Q18에서 수집한 내용으로 채워 주세요. 각 리스크는 가능한 간결하고 구체적으로 작성합니다.

## 1. 리스크 목록 (초안)
| ID | 리스크 설명 | 영향도 (Low/Medium/High) | 발생 가능성 | 감지 방법 | 완화/대응 계획 | 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| R-001 | Slack 리마인더 미전송 또는 중복 전송으로 사용자 신뢰 저하 | Medium | Medium | Slack 응답 로그, 모니터링 알람 | 전송 결과 로깅 + 재시도 로직, 주간 리마인더 테스트 (`docs/ALERT_TEMPLATES.md`) | Monitoring |
| R-002 | 퀘스트/회고 데이터 손실로 동기부여 루프 붕괴 | High | Low | DB 백업 로그, 주간 검증 | SQLite 자동 백업 + 주간 오프사이트 백업, 복원 시나리오 문서화 | Open |
| R-003 | LLM이 과도한 퀘스트를 제안해 사용자 과부하 유발 | Medium | Medium | 사용자 피드백, 챗봇 대화 모니터링 | SDT 기반 난이도 가이드 적용, 챗봇이 "많으면 줄이자" 되묻게 설계 | Open |
| R-004 | APScheduler 워커 중단으로 리포트/알림 누락 | Medium | Low | `logs/report_worker.log` 이상 여부 | `docs/OPERATIONS_SOP.md` 절차에 따라 재기동, 실패 시 Slack 경보 발송 | Open |
| R-005 | LLM 한도 미설정으로 비용 급증 및 서비스 차단 실패 | High | Medium | `logs/llm_usage.log`, 쿼터 경고 알림 | LLMQuotaManager 환경 변수 설정, 한도 초과 시 관리자 Slack 통보 | Open |
| R-006 | QuestLog 대량 데이터로 인한 리포트/조회 성능 저하 | Medium | Medium | 월간 리포트 실행 시간, DB 모니터링 | goal_id/quest_id 인덱스 추가, 주기적 통계 분석 | Mitigated |
| R-007 | LLM 쿼터 데이터 재시작 시 초기화되어 비용 통제가 무력화 | High | Medium | 일일 토큰 사용량 급증, 재시작 후 한도 미적용 사례 | `llm_daily_usage` + (선택) Redis 캐시로 지속성 확보, 모니터링 강화 | Mitigated |
| R-008 | 미인증 요청이 `default_user`로 저장돼 데이터 오염 | High | Low | 비정상 user_id 생성 비율, 감사 로그 | 인증 계층 의무화, 폴백 제거, 미인증 요청 즉시 차단 | Planned |
| R-009 | 스케줄러 중복 실행/실패 재시도 부재로 알림 누락/중복 | Medium | Medium | 워커 로그, Slack 중복 메시지 | 파일/Redis 기반 잠금 + 재시도 도입, 필요 시 Celery 검토 | Mitigated |

## 2. 모니터링 및 백업 전략 (Q18)
- 로그/모니터링 도구: Slack Webhook 응답 로그 + Sentry(알림 실패), DB 백업 자동화 로그
- 알림 실패/데이터 손실 감지 시나리오: 연속 실패 3회 시 경고, 백업 검증 실패 시 이메일 알람
- 백업 주기 및 저장 위치: SQLite 스냅샷 일일, 주간 백업을 Git LFS 또는 S3에 보관
- 비상 대응 절차: 백업 복원 절차 문서화, 복원 후 사용자에게 Slack/이메일 공지

## 3. 업데이트 내역
- 2025-01-XX: 초안 작성 (cli)
- YYYY-MM-DD: `TBD`

> 리스크가 해결되거나 새 항목이 발견되면 ID를 추가하고 상태를 갱신하세요.
