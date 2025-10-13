# Goaler Data Flow & Integration Notes (Template)

> CLARIFIERS.md Q19~Q20의 답변을 기반으로 작성합니다. 이벤트 기반 흐름과 외부 연동 가능성을 명확히 기록하세요.

## 1. 핵심 이벤트 흐름 (Q19)

### 1.1 목표 생성
- 입력: 사용자 ID, 목표 메타 정보 (`title`, `goal_type`, `deadline`, `motivation`)
- 처리: `Storage.create_goal` → `goals` 테이블 기록
- 후속 작업: 초기 메트릭 생성 여부(TBD)

### 1.2 메트릭 관리 및 진행률 업데이트
- 이벤트: 사용자가 진행률 입력 / 챗봇 자동 업데이트
- 저장: `metrics.progress`, `metrics.updated_at`
- 후속: 대화 로그 기록, 리마인더 재계산 여부(TBD)

### 1.3 대화 로그 및 요약
- 원시 로그 저장: `conversation_logs`
- 요약 조건: 토큰 수 / 주기 (세부 수치 TBD)
- 요약 저장: `conversation_summaries`

### 1.4 리마인더 발송
- 트리거: 스케줄러가 `reminders.next_run_at` 확인
- 메세지 구성: 목표 제목 + 진행률 + 남은 기간 + 다음 액션
- 후속: `next_run_at` 갱신, 전송 결과 로그(TBD)

## 2. 외부 연동 계획 (Q20)
- 건강 앱(운동 데이터) 연동 여부: `TBD`
- 재무/가계부 앱(수익 데이터) 연동 여부: `TBD`
- 기타 API 후보: `TBD`
- 데이터 수집 방식(웹훅/폴링 등): `TBD`

## 3. 다이어그램/시각 자료
- 데이터 플로우 다이어그램(DFD) 링크: `TBD`
- 시퀀스 다이어그램 링크: `TBD`

> 추후 연동 범위가 확정되면, 해당 API 요구 사항과 인증 정책도 함께 문서화하세요.
