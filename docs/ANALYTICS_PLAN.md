# Analytics & Experimentation Plan

## 1. 핵심 지표(일간/주간)
- **전리품 기록률**: 전체 완료 퀘스트 중 `mood_note`가 채워진 비율
- **에너지 상태 분포**: `READY_FOR_BOSS` / `KEEPING_PACE` / `NEEDS_POTION`
- **휴식 신호 연속 횟수**: `NEEDS_POTION`이나 `DEFERRED`가 연속으로 발생한 일수
- **변주 선택률**: 제안된 변주 중 선택까지 이어진 비율, 건너뛰기 비율
- **Flow 자가 평가**: 주간 회고에서 1~5점 척도로 몰입도를 기록
- **목표 진척 편차**: 계획된 로드맵 대비 실제 완료 속도(일/주)

## 2. 자동 경고 규칙
- Warning: `NEEDS_POTION` 1회 → 다음 변주에 회복 옵션 자동 포함
- Critical: `NEEDS_POTION` 2회 연속 또는 주간 `DEFERRED` ≥ 2 → 회복/보완 퀘스트 기본값, 공격 변주 숨김
- Emergency: `NEEDS_POTION` 3회 연속 → 포션 의식 루틴 실행(+전리품 보호 버프)
- 전리품 기록률 30% 미만 7일 지속 → 챗봇이 긍정 경험 회상 질문 도입
- Flow 점수 2 이하가 2주 연속 → 코치가 장기 전략 재설계 안내

## 3. 실험 아이디어
- **휴식 전략 비교**: 물약 제안 vs 보완 퀘스트 vs 기본 (A/B/C 테스트)
- **전리품 질문 위치**: 미션 직후 vs 회고 화면에서 묻는 방식 비교
- **응원 메시지 톤**: 칭찬형 vs 전략형 vs 데이터형
- **연속 도전 보상**: 연속 5일 성공 시 배지/스토리/보상 중 무엇이 유지율에 효과 있는지 검증
- **경고 버프 실험**: Guardian Buff(전리품 보호) vs Momentum Shield(경고 메시지) 효과 비교, 재도전 성공률 측정

## 4. 데이터 파이프라인
- 앱/챗봇 이벤트 → `quest_logs` 및 `player_progress` 저장소 → 주간 배치 분석 (예: dbt/SQL)
- Flow 설문/주간 회고 결과 → `conversation_summaries`와 별도 `weekly_checkins` 테이블 연동 (향후 설계)
- 지표 집계 대시보드: Superset/Metabase 등에 연결해 운영자가 실시간 모니터링
- 이벤트 스키마 초안 (향후 구현)
  - `quest_completed`: {goal_id, boss_id?, loot_type, energy_status, timestamp}
  - `boss_stage_status_changed`: {boss_id, status_from, status_to, reason, timestamp}
  - `energy_warning_triggered`: {level (warning/critical/emergency), consecutive_days}
  - `boss_success`: {boss_id, total_days_prepared, combo_count}
- 온보딩/테마 이벤트:
  - `onboarding_stage_changed`: {user_id, stage_from, stage_to, timestamp}
  - `theme_selected`: {user_id, theme_preference, timestamp}
- ETL 제안: 일별 스냅샷 테이블(`daily_goal_stats`, `daily_warning_stats`) 생성 → BI 도구에서 Alert 설정
- 월말/분기말에는 ETL 결과를 사용해 `tools/generate_loot_report.py`를 호출하고, 생성된 파일 경로를 알림 시스템(Slack/Email)과 연동한다.

## 5. 개인정보 및 윤리 고려
- 감성 메모는 짧은 텍스트로 수집하며, 민감 정보가 포함되면 자동 마스킹 필터 적용 고려
- 실험(A/B 테스트) 수행 시 사용자에게 기본 안내 제공 및 옵트아웃 경로 마련
