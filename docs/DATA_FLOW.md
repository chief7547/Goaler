# Goaler Data Flow & Integration Notes

> CLARIFIERS.md Q19~Q20의 답변을 기반으로 작성합니다. 이벤트 기반 흐름과 외부 연동 가능성을 명확히 기록하세요.

## 1. 핵심 이벤트 흐름 (Q19)

### 1.1 목표 생성
- 입력: 사용자 ID, 목표 메타 정보 (`title`, `goal_type`, `deadline`, `motivation`)
- 처리: `Storage.create_goal` → `goals` 테이블 기록
- 후속: LLM이 `define_boss_stages`를 호출해 핵심 단계(보스전)를 생성하고 `boss_stages` 테이블에 저장
- 추가 저장: 각 보스전에 대해 `propose_weekly_plan` → 주간 단계 메모, `propose_daily_tasks` → 초기 일일 퀘스트를 생성해 `quests`에 저장
- 선택 입력 프로필(연령대·성별·MBTI 등)을 `user_preferences`에 업데이트하고, Implementation Intentions(언제/어디서/어떻게)를 `quests`/`quest_logs`에 기록해 리마인더와 추천 로직에 활용

### 1.2 퀘스트 보드 및 완료 이벤트
- 이벤트: 사용자가 퀘스트 완료/보류/건너뛰기를 선택하거나, 챗봇 자연어 명령을 통해 처리 요청
- 저장: `quests`는 기본 메타만 유지하고, 실제 수행 이력은 `quest_logs`에 outcome·perceived_difficulty·energy_status·mood_note·llm_variation_seed 등과 함께 적재됩니다.
- 후속: 완료 이벤트는 대화 로그(`conversation_logs`)에 요약 저장, Slack 리마인더 스케줄과 메시지 콘텐츠 재계산에 반영하며, LLM 변주 모듈이 다음 미션을 고를 때 최근 기록을 참고합니다.
- 고급 사용자의 숫자형 지표를 활성화한 경우에만 `optional_metrics.metric_categories`를 참고해 입력을 받고, 검증은 `CONFIG.yaml.optional_metrics.validation_rules` 적용
- Stage/XP 처리: `player_progress`에서 경험치를 누적하고, Stage 조건(연속 성공 주차·챕터 퀘스트 달성 등)을 만족하면 Stage를 승급시키고 신규 퀘스트를 해금
- 변주 루틴: LLM 호출 전 `user_preferences`, 최근 `quest_logs`, `quests.variation_tags`를 조합해 “반복 감지 → 변주 추천 → 사용자 선택” 절차를 수행합니다.

### 1.3 대화 로그 및 요약
- 원시 로그 저장: `conversation_logs`
- 요약 조건: 토큰 수가 기준을 넘거나 하루가 끝날 때마다 LLM이 요약을 생성
- 요약 저장: `conversation_summaries`

### 1.4 리마인더 발송
- 트리거: 스케줄러가 `reminders.next_run_at` 확인
- 메시지 구성: 목표 설명 + 남은 기간 + 최근 완료한 퀘스트 + 다음 추천 행동 (MVP 고정 메시지). 향후에는 LLM이 응원/퀘스트/동기 문구를 조합하며, `quest_logs.mood_note`와 `energy_status`를 참고해 톤과 강도를 조절합니다.
- 후속: 전송 후 `next_run_at` 갱신, 전송 성공/실패 결과를 로깅해 모니터링

### 1.5 회고/리포트 생성
- 이벤트: 주간/월간 마감 시 챗봇이 `quest_logs`와 요약을 바탕으로 리포트 생성
- 출력: 완료/보류/건너뛰기 퀘스트 수, 연속 달성일, LLM 코멘트, 다음 주 추천 퀘스트 리스트
- 후속: 리포트를 Slack으로 공유하고, 사용자가 수정하면 `quests`와 `reminders`에 반영하며, Stage/XP 조정(난이도 상향/하향) 및 새로운 챕터 퀘스트 제안에 활용

## 2. 외부 연동 계획 (Q20)
- 건강 앱: 차후 Apple Health / Google Fit with OAuth + 주기 동기화 또는 웹훅
- 재무/가계부: 국내 가계부 API(토스, 뱅크샐러드) 또는 Plaid 계열 서비스 검토, 월별 요약 목적
- 기타 후보: Google Calendar와 퀘스트 일정 동기화, Slack DM/Channel 분리, Notion 로그 내보내기
- 데이터 수집 방식: MVP는 수동 입력 + CSV 업로드, 확장 단계에서는 OAuth 후 주기적 폴링, 장기적으로 웹훅 이벤트 기반 전환

## 3. 다이어그램/시각 자료
- 데이터 플로우 다이어그램: `docs/diagrams/dfd_mvp.drawio` (작성 예정)
- 시퀀스 다이어그램: `docs/diagrams/sequence_llm_quest.md` (작성 예정)
- 온보딩 플로우 차트: `docs/diagrams/onboarding_flow.fig` (작성 예정)

> 추후 연동 범위가 확정되면, 해당 API 요구 사항과 인증 정책도 함께 문서화하세요.
