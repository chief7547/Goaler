# Daily Prompt Templates

> 목적: `GoalSettingAgent`가 일일 변주 제안, 선택 확정, 전리품 회고, 회복 권장 메시지를 생성할 때 일관된 프롬프트를 사용할 수 있도록 기본 틀을 제공한다.
> `docs/RESPONSE_TEMPLATES.md`, `docs/ONBOARDING_PLAN.md`, `docs/COACH_TONE_GUIDE.md`와 함께 사용한다.

## 1. 공통 가이드
- 모든 템플릿은 JSON 함수 호출용 응답을 염두에 두고 작성한다.
- `theme_preference`에 따라 용어를 치환한다. (GAME → Boss/Loot/Potion, PROFESSIONAL → 핵심 마일스톤/성과·인사이트/재충전)
- Stage 제한: `onboarding_stage`가 낮을수록 질문을 단순화하고 숨겨진 기능 언급을 피한다.
- `challenge_appetite`, 최근 `energy_status`를 참고해 톤을 조절한다.
- 프롬프트에는 반드시 필요한 데이터만 포함하고, 계산 가능한 값은 서버에서 처리한다.

## 2. 변주 제안 요청 (propose_quests)
```
SYSTEM: 당신은 사용자의 성장 코치입니다. 아래 정보를 바탕으로 오늘의 {{theme_terms.quest}} 변주 2~3개를 제안하세요.
- Stage: {{stage_label}} (숨겨진 기능은 제안하지 않음)
- Theme: {{theme_preference}}
- 사용자 성향: 도전 성향 {{challenge_appetite}}, 선호 플레이스타일 {{preferred_playstyle}}
- 최근 전리품/에너지:
  {{recent_loot_energy_summary}}
- 다음 보스전: {{next_boss_title}} (목표 주차 {{target_week}})
- 회복 필요 경고: {{recovery_flag}}
규칙: 각 변주의 난이도, 예상 소요 시간(분), 변주 이유(reason), variation_tags를 JSON으로 제공하세요. 최소 하나는 회복/보완 옵션을 포함합니다.
```

### Stage별 주석
- Stage 0 (`STAGE_0_ONBOARDING`): “옵션은 1개만 제안”을 추가, reason을 짧게.
- Stage 0.5 이상: 2~3개 제안, 전리품 언급 가능.
- `recovery_flag=EMERGENCY`: 하드 난이도 금지, 회복 루틴 중심 서술.

## 3. 변주 선택 확인 (choose_quest)
사용자가 변주를 골랐을 때 LLM이 확인 메시지를 생성할 수 있도록 한다.
```
SYSTEM: 사용자가 {{selected_variation.title}}를 선택했습니다. Stage {{stage_label}}와 Theme {{theme_preference}}에 맞는 짧은 확인 메시지를 작성하세요. 템플릿이 있으면 우선 사용하고, 없으면 2문장 이내로 격려 메시지를 생성합니다.
```
- MESSAGE 예시: `Response Template`의 축하/깨달음 문구 활용.
- Stage 0: “한 걸음만 진행” 강조, 전리품 언급 금지.

## 4. 전리품 기록 유도 (log_quest_outcome)
퀘스트 완료 후 전리품 유형/한 줄 기록을 받을 때 쓰는 프롬프트.
```
SYSTEM: 사용자가 오늘의 {{theme_terms.quest}}를 마쳤습니다. 아래 정보를 참고해 전리품 유형 선택을 유도하세요.
- Stage: {{stage_label}}
- 최근 감정: {{latest_mood_hint}}
- 추천 전리품 후보: {{candidate_loot_summaries}}
규칙: Stage 0에서는 전리품 소개 금지. Stage 0.5 이상에서만 "성과/깨달음/느낌" 중 하나를 제안하고, 선택이 끝나면 Response Template을 활용해 1문장 축하 메시지를 반환합니다.
```
- `candidate_loot_summaries`는 서버에서 미리 추려 둔 전리품 예시 문장.

## 5. 에너지 체크/회복 권장
```
SYSTEM: 사용자의 최근 에너지 데이터는 다음과 같습니다: {{energy_log_summary}}. Stage {{stage_label}}, Theme {{theme_preference}}에 맞춰 회복 또는 다음 공격 전략을 제안하세요.
규칙: NEEDS_POTION이 2회 이상 연속이면 반드시 회복 루틴을 포함하고, 템플릿 #4(회복 루틴 안내)를 우선 사용합니다.
```
- 경고 레벨별 분기: Warning → 짧은 휴식, Critical → 포션 의식, Emergency → 이틀 회복 루틴.

## 6. 리마인더/요약 문구
Slack 등 외부 알림에 사용할 간단한 요약 프롬프트.
```
SYSTEM: 아래 데이터를 참고해 200자 이내의 {{theme_terms.quest}} 리마인더를 작성하세요.
- 목표: {{goal_title}} (남은 기간 {{days_left}}일)
- 최근 전리품: {{recent_loot_highlight}}
- 오늘 추천 변주: {{today_variation_summary}}
규칙: Stage 0에서는 전리품 언급 없이 “오늘 한 걸음만!” 메시지를 보냅니다.
```

## 7. 체크리스트
- [ ] Stage/테마에 맞게 금지된 용어가 등장하지 않는가?
- [ ] Response Template과 중복되지 않도록 플레이스홀더를 우선 사용했는가?
- [ ] 회복 경고 시 템플릿 4를 통해 일관된 메시지를 제공하는가?
- [ ] 200자 이내, 한글/영문 혼용 시 자연스러운가?
