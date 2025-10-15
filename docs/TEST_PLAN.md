# Test Plan (보스전 & 변주 흐름)

## 1. 단위 테스트 권장 항목
- `Storage`
  - `create_boss_stage` → 데이터가 올바르게 저장되는지, stage_order 자동 증가 검증
  - `list_boss_stages` → 순서 정렬, 상태 필터링
  - 경고 레벨 업데이트(`player_progress`) → Warning/Critical/Emergency 단계별 상태 변화 확인
- `GoalSettingAgent`
  - `define_boss_stages` → 사용자 입력 모킹 후 boss_stages가 State/Storage에 반영되는지 확인
  - `propose_weekly_plan` / `propose_daily_tasks` → LLM 모킹 후 State 업데이트 검증
  - `log_quest_outcome` → energy_status 연속 감지, 경고 레벨과 향후 변주 제안 분기 확인

## 2. 통합 테스트 시나리오
1. **목표 생성 루프**
   - 장기 목표 입력 → 보스전 후보 제안 → 사용자 확정 → 주간/일일 계획 생성
2. **일일 실행 루프**
   - 일일 퀘스트 변주 제안 → 전리품/에너지 입력 → 다음 날 변주에 반영
3. **보스전 성공/실패 루프**
   - 특정 보스전이 활성화된 상태에서 준비 퀘스트 완료 → 성공 조건 충족 → Stage 승급/Relic 생성 확인
   - 실패 흐름: `NEEDS_POTION` 연속 발생 → 회복 루틴 제안 → 재도전 → 성공 시 전리품 보호 확인

## 3. UI/시각 요소 점검
- 대시보드 상단 카드가 Stage/보스전 상태에 따라 변경되는지 스냅샷 테스트
- 변주 모달이 보스전/회복 상황에 맞는 텍스트를 보여주는지 확인
- 전리품 보관함에서 전리품 유형별 필터가 작동하는지 확인

## 4. 회귀 테스트 자동화 후보
- `pytest` + `responses`(LLM 모킹)으로 보스전 정의/변주/로그 기록 흐름을 시뮬레이션
- `golden` 테스트를 보스전 타임라인 JSON 스냅샷으로 추가해 예상 구조가 변하지 않는지 감리

## 5. 추후 확장
- 실제 LLM 통합 E2E 테스트 시, 보스전 생성 → 목표 달성까지의 시나리오를 기록해 리그레이션 테스트로 활용
- 장기적으로는 분석 지표(전리품 기록률, 경고 레벨 등)를 모니터링하는 모의 데이터 테스트도 추가 예정
