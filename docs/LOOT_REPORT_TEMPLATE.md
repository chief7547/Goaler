# Loot Report Template

> 목적: `docs/LOOT_REPORT_WORKFLOW.md` 단계 2에서 사용할 월간/분기 전리품 리포트를 일관된 포맷으로 생성하기 위한 기본 서식.
> LLM 또는 템플릿 엔진이 아래 구조에 맞춰 값을 치환한다.

## 1. 데이터 전제조건
- 사용자 프로필: `users`, `user_preferences`, `player_progress`
- 목표/보스: `goals`, `boss_stages`
- 실행 기록: `quest_logs` (loot_type, energy_status, mood_note, outcome), `conversation_summaries` (선택)
- 경고 지표: 휴식 신호(`NEEDS_POTION`), 연속 실패, streak 정보
- 비용 로그: `logs/llm_usage.log` (선택, 비용 섹션에 포함)

## 2. 필수 플레이스홀더
| 키 | 의미 | 비고 |
| --- | --- | --- |
| `{{period_label}}` | "2025년 2월" 같이 사람이 읽기 쉬운 기간명 | 월간/분기 모두 사용 |
| `{{generated_at_iso}}` | 생성 시각(ISO-8601) | UTC 기준, 필요 시 로컬시각 병기 |
| `{{user_display_name}}` | `users.display_name` 또는 별칭 | 값이 없으면 "Adventurer" 등 기본값 |
| `{{theme_terms.quest}}` | 테마에 맞는 용어, GAME → "퀘스트", PROFESSIONAL → "실행 계획" | `theme_preference`를 참고 |
| `{{stage_name}}` | 현재 Stage 명칭(예: Momentum Forge) | `player_progress.stage_label` 매핑 테이블 필요 |
| `{{xp}}` | 누적 경험치 | 미집계 시 `TBD` 허용 |
| `{{streak_weeks}}` | 연속 성공 주차 | 값이 없으면 "0" |
| `{{focus_goal_title}}` | 현재 집중 목표 제목 | 없으면 "집중 목표 미지정" |
| `{{focus_boss_title}}` | 주력 보스/핵심 마일스톤 | 없으면 "준비 중" |
| `{{boss_completed_list}}` | 완료된 보스전 목록 | bullet 문자열 |
| `{{boss_in_progress_list}}` | 진행 중 보스전 목록 | |
| `{{boss_next_list}}` | 다음으로 준비할 보스전 목록 | |
| `{{loot_summary_table}}` | 전리품 유형별 요약 테이블 Markdown | §3 예시 참고 |
| `{{loot_quotes_block}}` | 대표 전리품 문장 3~5개 | 종류 믹스 권장 |
| `{{energy_stats_table}}` | Warning/Critical/Emergency 집계 | |
| `{{streak_highlight}}` | 연속 기록 코멘트 | 없으면 "이번 기간에는 새로운 연속 기록이 없어요." |
| `{{recovery_recommendation}}` | 회복/보완 전략 텍스트 | `NEEDS_POTION` 빈도 기반 |
| `{{next_focus_actions}}` | 다음 기간 핵심 행동 2~3개 bullet | 보스/변주 추천 요약 |
| `{{coach_tone_salute}}` | 코치 인사/격려 문구 | 테마/성향에 맞춰 Response Template 활용 |
| `{{usage_cost_summary}}` | (선택) 모델별 토큰/비용 요약 | 비용 데이터 없으면 섹션 생략 |

## 3. Markdown 기본 구조
아래 서식은 최소 단위이며, 필요 시 섹션을 추가할 수 있다. 값이 비어 있으면 해당 bullet/문장을 제거한다.

```markdown
# {{period_label}} Loot Chronicle — {{user_display_name}}
생성 시각: {{generated_at_iso}}

## 1. 모험 요약
- 현재 Stage: **{{stage_name}}** (XP {{xp}}, 연속 {{streak_weeks}}주)
- 집중 {{theme_terms.quest}}: **{{focus_goal_title}}**
- 핵심 보스: **{{focus_boss_title}}**
- 하이라이트: {{streak_highlight}}

## 2. 전리품 요약
{{loot_summary_table}}

{{loot_quotes_block}}

## 3. 보스전 진행도
- 완료: {{boss_completed_list}}
- 진행 중: {{boss_in_progress_list}}
- 다음 준비: {{boss_next_list}}

## 4. 에너지 & 회복 상태
{{energy_stats_table}}

{{recovery_recommendation}}

## 5. 다음 턴 전략
{{next_focus_actions}}

{{coach_tone_salute}}

---
{{usage_cost_summary}}
```

### 3.1 전리품 테이블 예시
```markdown
| 유형 | 획득 횟수 | 대표 문장 |
| --- | --- | --- |
| 성과(ACHIEVEMENT) | 5 | “서류 체크리스트 완성” |
| 깨달음(INSIGHT) | 3 | “신청 절차 흐름을 이해했다” |
| 감정(EMOTION) | 2 | “회복 루틴이 마음을 지켜줬다” |
```

### 3.2 대표 전리품 블록 예시
```markdown
> “서류 체크리스트 완성” — 연속 3일 집중이 만든 성과예요.
> 
> “신청 절차 흐름을 이해했다” — 다음 보스전을 대비한 통찰입니다.
> 
> “회복 루틴이 마음을 지켜줬다” — 회복도 모험의 일부였습니다.
```

### 3.3 에너지 통계 예시
```markdown
| 경고 레벨 | 발생 횟수 | 코멘트 |
| --- | --- | --- |
| Warning | 2 | 필요할 때마다 10분 회복 루틴을 적용했어요. |
| Critical | 0 | 안정적으로 페이스를 유지했습니다. |
| Emergency | 0 | 전리품이 안전하게 보호되고 있어요. |
```

## 4. 조건별 처리 규칙
- 데이터가 없거나 집계 실패 시: 해당 bullet/테이블을 제거하고 “이번 기간에는 데이터가 없어요.”와 같이 간단히 안내.
- 테마 치환: `theme_terms.quest` 등은 `theme_preference`에 따라 `Response Template`의 용어 세트를 적용한다.
- Stage 명칭 매핑: `player_progress.stage_label` → `PRODUCT_SPEC.md` Stage 테이블 기반 문자열 (예: `STAGE_1` → `Momentum Forge`).
- 회복 권장 문구: `NEEDS_POTION` 비율이 20% 이상이면 회복 루틴을 우선 제안, 그 외에는 공격/보완 전략을 강조.
- LLM 사용량 섹션: `docs/LLM_USAGE_GUIDE.md` 기준으로 모델별 토큰/비용을 정리하거나 섹션 자체를 생략.

## 5. 검증 체크리스트
- [ ] 모든 필수 플레이스홀더가 치환되었는가?
- [ ] 전리품/보스전 목록이 Stage 규칙과 일관성 있는가?
- [ ] 테마 용어가 문서 전반에 동일하게 적용되었는가?
- [ ] 회복 권장 문구가 경고 지표와 상충하지 않는가?
- [ ] (선택) LLM 비용 정보가 있을 경우 형식이 맞는가?
