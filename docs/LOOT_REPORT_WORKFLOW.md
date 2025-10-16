# Loot Report Automation Workflow

## 1. 실행 개요
- 주기: 월간(마지막 날), 분기(3/6/9/12월 말)
- 실행 방법: `python tools/generate_loot_report.py --period monthly` (CI 또는 배치 워커에서 호출)
- 출력 대상: 사용자별 Markdown/HTML 파일 + Slack/Email 알림 메시지

## 2. 데이터 추출 단계
1. `quest_logs`
   - 기간 내 전리품 (`loot_type`, `mood_note`, `energy_status`, `created_at`)
2. `boss_stages` & `player_progress`
   - 보스전 상태(완료/진행/다음 목표), stage_order
3. `conversation_summaries` (선택)
   - Flow/회고 텍스트 요약에 활용
4. `usage_logs` (선택)
   - LLM 사용량을 보고서 말미에 부가 정보로 표시 가능

## 3. 리포트 생성 단계
1. **데이터 집계**
   - 전리품을 `loot_type`별 카운트 + 대표 문장 선정(최근 3개)
   - 보스전 진행률(완료/진행/다음) 계산
   - 경고 레벨(Warning/Critical/Emergency) 발생 횟수 집계
2. **템플릿 채우기**
   - `docs/LOOT_REPORT_TEMPLATE.md` 구조에 맞추어 Markdown 생성
   - LLM 호출이 필요한 섹션
     - 전리품 하이라이트 코멘트 → `gpt-5-mini`
     - 다음 달/분기 전략 문구 → `gpt-4o-mini` (필요 시)
   - 토큰 사용량을 `logs/llm_usage.log`에 기록하여 비용 추적
3. **출력**
   - `/reports/{user_id}/{period}-{YYYY-MM}.md` 저장 (필요 시 PDF 변환)
   - 알림(Slack/Email)에 하이라이트 요약(3~4줄) 및 링크 첨부

## 4. 배치/자동화 계획
- 초기 단계
  - GitHub Actions 배치 워크플로우(`.github/workflows/loot_report.yml`)에 nightly 크론을 설정하고,
    실행 시 mock DB 또는 준비된 샘플 데이터를 사용
- 운영 단계
  - Celery/APSscheduler 워커에서 실행
  - 환경 변수: `LOOT_REPORT_OUTPUT_DIR`, `LOOT_REPORT_NOTIFY_SLACK_WEBHOOK`

## 5. 오류 처리 & 재시도
- 데이터 누락 시 기본 메시지 (“이번 달에는 전리품이 없었어요. 다음 달에 함께 채워봐요.”)
- LLM 호출 실패 시 fallback 모델 또는 템플릿 문구 사용
- Slack/Email 전송 실패 시 재시도 로직 또는 관리자 알림

## 6. 테스트 시나리오
- 샘플 데이터로 월간/분기 리포트를 생성해 텍스트 비교(golden 테스트)
- 전리품이 없는 기간, 보스전이 없는 목표에 대한 출력 확인
- LLM 호출이 비활성(mock)일 때도 템플릿이 정상 생성되는지 확인

## 7. 향후 개선
- 리포트 결과를 앱 내 보관함에서 열람 및 공유 가능하도록 UI 연동
- 전리품 하이라이트에 이미지/그래프(텍스트 기반 스파크라인) 추가
- B2B 팀/길드 단위 리포트 확장
