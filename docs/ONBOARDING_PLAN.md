# Progressive Onboarding Plan

> 목적: 신규 사용자가 인지적 과부하 없이 핵심 루프를 익히고, 순차적으로 보스전/전리품/에너지 기능을 해금하도록 안내하기 위한 구체 계획.

## Stage 코드 매핑
| Stage 코드 | 사용자 노출 명칭 | 해금 요약 |
| --- | --- | --- |
| `STAGE_0_ONBOARDING` | Stage 0 – Spark Awakening | 전리품/에너지 숨김, 기초 루프 학습 |
| `STAGE_0_5_LOOT` | Stage 0.5 – Loot Introduction | 전리품 칩만 해금 |
| `STAGE_1_ENERGY` | Stage 1 – Energy Awareness | 에너지 버튼, 회복 루틴 안내 |
| `STAGE_1_5_BOSS_PREVIEW` | Stage 1.5 – Boss Stage Preview | 보스전(핵심 마일스톤) 카드 미리보기, 테마 선택 |
| `STAGE_2_ASCENSION` | Stage 2 – Ascension Path | 전체 보스/변주/전리품 루프 활성화 |
| `STAGE_3_SUMMIT` | Stage 3 – Summit Breakthrough | 장기 목표 마무리 및 확장 기능 |

> `player_progress.stage_label`과 `user_preferences.onboarding_stage`에는 위 코드 값을 저장한다. UI/리포트에서는 본 문서의 한글 명칭을 사용한다.

## Stage 0 – Spark Awakening (Day 0~3)
- **노출 요소:** 목표 생성, 일일 퀘스트 완료, 칭찬 메시지
- **숨김 요소:** 전리품 기록, 에너지 체크, 보스전, Stage UI
- **AI 코치 스크립트:**
  - Day 0: “지금은 단 하나의 퀘스트만 이어가 볼까요?”
  - Day 2: “이틀 연속 성공! 내일도 같은 루틴으로 감각을 익혀봐요.”
- **해금 조건:** 3회 이상 연속 퀘스트 완료 → “전리품” 기능 소개

## Stage 0.5 – Loot Introduction (Day 3~7)
- **노출 요소:** 전리품 칩(성과/깨달음/느낌) + 한 번 탭하기만으로 기록, 에너지 버튼은 숨김
- **AI 코치 안내:**
  - “짧게 전리품을 남겨보면 다음 주에 기분 좋은 기록이 됩니다.”
  - 전리품 입력은 옵션이며, 건너뛰기 버튼 노출 (“오늘은 패스할게요”).
- **해금 조건:** 전리품 3개 이상 기록 → 에너지 체크/회복 메타포 소개

## Stage 1 – Energy Awareness (Day 7~14)
- **노출 요소:** 전리품 + 에너지 버튼, 회복 루틴 소개, Stage 1 UI 일부(Progress 바)
- **AI 코치 안내:**
  - “오늘 전리품을 남겼다면, 에너지 상태도 한 번 눌러볼까요?”
  - “물약이 필요하면 제가 회복 루틴을 준비해 둘게요.”
- **해금 조건:** 전리품/에너지 기록 5회 이상 → 보스전/Stage 메타 소개

## Stage 1.5 – Boss Stage Preview (Day 14~21)
- **노출 요소:** 보스전 카드(요약), “핵심 마일스톤” 설명, 변주 모달의 간단한 이유 텍스트
- **테마 선택 유도:** AI 코치가 “게임 모드 vs 전문가 모드” 중 선호를 묻고 `theme_preference` 저장. UI copy 변경
  - 게임 모드: 보스/물약/전리품 용어 유지
  - 전문가 모드: “핵심 마일스톤”, “성과/인사이트/감정 로그”, “재충전” 용어 사용
- **해금 조건:** 사용자가 보스전과 주간 단계 보기 > Stage 2 Unlock

## Stage 2 이후 – 전체 기능 오픈
- **노출 요소:** 전 기능(보스전, 변주, 전리품 리포트 알림 미리보기)
- **AI 코치 안내:** “이제 완전한 성장 모험을 시작할 준비가 되셨어요! 필요하면 언제든 다시 기초 모드로 돌아가셔도 됩니다.”
- **재설정 옵션:** 설정 화면에서 온보딩 단계를 리셋하거나 전문가/게임 테마 변경 가능

## 구현 체크리스트
- `user_preferences.onboarding_stage`, `theme_preference` 업데이트 로직
- UI/화면: 온보딩 단계에 따라 컴포넌트 표시/숨김
- AI 프롬프트: 현재 `onboarding_stage` 기반으로 기능 소개 대사 분기(`core/agent.py`)
- 테스트: Stage 0~2 시나리오 통합 테스트 (`docs/TEST_PLAN.md` 보강)
