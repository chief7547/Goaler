# Alert Templates

> 알림 채널별 기본 메시지 구조. Phase 5에서 Slack/Email/SMS 확장을 고려하며, 템플릿은 LLM 변형이 필요한
> 부분과 고정 카피를 구분해 기록한다.

## 1. Slack – 일일 리마인더
```
[Goaler] 오늘의 준비: {quest_title}
- 목표: {goal_title}
- 남은 기간: {days_left}
- 최근 전리품: {latest_loot}
- 다음 단계: {next_step}

{motivation_line}
```
- `motivation_line`: CoachResponder 템플릿에서 추출 (예: “오늘도 한 걸음 나아가볼까요?”)
- 실패 시 재시도: 5분 후 3회, 모두 실패하면 `#goaler-alerts` 채널에 관리자 경고 발송

## 2. Slack – 월간 전리품 리포트
```
[Goaler] {user_display}님의 {period_label} 전리품 연대기가 도착했습니다.
- 완료 퀘스트: {quest_completed}
- 전리품 하이라이트: {top_loot}
- 추천 전략: {strategy_summary}

전체 리포트 보기 → {report_link}
```
- `strategy_summary`: `compose_growth_story` 결과에서 한 문장 발췌

## 3. Email 템플릿 (확장 단계)
Subject: "Goaler 월간 리포트 – {period_label}"
Body:
```
안녕하세요, {user_display}님!

이번 달은 {top_loot} 등의 전리품이 인상적이었어요. 아래 버튼을 눌러 성장 서사를 확인해보세요.
- 완료 퀘스트: {quest_completed}
- 에너지 경고: {needs_potion_count}회
- 다음 추천 행동: {next_step}

다음 달에도 함께 도약해요!
```
CTA Button: "전리품 연대기 열람"

## 4. SMS 템플릿 (백업 채널)
```
[Goaler] 오늘의 준비: {quest_title} (남은 기간 {days_left})
최근 전리품: {latest_loot}
계속 이어가볼까요?
```

## 5. 경보(Alert) 메시지
| 상황 | 템플릿 |
| --- | --- |
| Slack Webhook 연속 실패 | `[경보] Slack 전송 실패 – {goal_id} ({attempts}회). 워커 로그 확인 필요.` |
| LLM 토큰 한도 초과 | `[경보] LLM 토큰 사용량 경고 – {model} {total_tokens} tokens 사용 (임계치 {threshold}).` |
| 에너지 Emergency 지속 | `[경보] 포션 의식 발동 – 사용자 {user_id}가 3일 연속 NEEDS_POTION 상태입니다.` |

템플릿 변경 시 `docs/LOOT_REPORT_WORKFLOW.md`와 `docs/OPERATIONS_SOP.md`에서 알림 절차를 함께 갱신한다.
