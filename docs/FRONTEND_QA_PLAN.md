# Frontend QA & Automation Plan

프런트엔드 품질 보장을 위한 Storybook, Playwright, 시각 회귀 테스트 전략을 정리합니다.

## 1. Storybook 전략
- **구성**: `Component/State/Theme/Motion` 네이밍 규칙
- **공통 Decorator**
  - ThemeProvider (Game/Pro 토글)
  - FxProvider (모션 기록, Reduced Motion 토글)
  - LayoutWrapper (데스크톱/모바일 viewport)
- **필수 스토리 목록**
  - `AppShell` (Desktop/Mobile, Game/Pro)
  - `HeroCard` (`default`, `stageUpgrade`, `warning`, Theme별 + Reduced Motion)
  - `QuestCard` (`easy`, `normal`, `hard`, `completed`)
  - `ChecklistItem` (`default`, `completed`, `failing`)
  - `LootChip` (`achievement`, `insight`, `emotion`)
  - `ChatMessage` (`user`, `assistant`, `system`, `loading`)
  - `BossTimeline` (`ready`, `completed`, `adjustmentNeeded`)
  - `ReminderForm` (`default`, `testSuccess`, `testError`)
  - FX 전용 (`fx_stage_upgrade`, `fx_quest_complete`, `fx_energy_warning`, Reduced Motion 버전)
- **Chromatic/Storybook Test**
  - Game Theme + Motion On
  - Game Theme + Reduced Motion
  - Professional Theme + Motion On
  - Professional Theme + Reduced Motion

## 2. Playwright 시나리오
| 시나리오 | 뷰포트 | 설명 |
| --- | --- | --- |
| Dashboard 기본 | 1440×900 | HeroCard, Checklist, FX 발생 여부 스냅샷 |
| Dashboard Reduced Motion | 1440×900 | `prefers-reduced-motion` 플래그 → FX가 Color change로 대체되는지 확인 |
| Chat 상호작용 | 1280×800 | 메시지 전송 → 추천 액션 → 컨텍스트 패널 업데이트 |
| Goals 상세 | 1280×800 | 보스 타임라인/재조정 배너 노출 여부 |
| Reports | 1440×900 | 기간 필터 + 그래프 로딩 스냅샷 |
| Reminders | 1280×800 | Slack 테스트 성공/실패 토스트 |
| Mobile Dashboard | 390×844 | 구성요소 순서/탭 전환 확인 |
| Mobile Chat | 390×844 | Drawer 기반 컨텍스트 패널 여닫기 |

- 모든 시나리오는 Game/Pro 테마를 각각 한 번씩 실행
- 중요한 스냅샷은 `__screenshots__/`로 버전 관리

## 3. 시각 회귀 테스트
- Storybook Chromatic 또는 Loki 사용
- 최소 비교 대상: `HeroCard`, `QuestCard`, `DashboardPage`, `ChatPage`
- Reduced Motion 스토리도 시각 회귀에 포함 (색상 변화 확인)

## 4. 접근성 테스트
- Lighthouse CI (접근성 90점 이상) + axe-core 자동 검사
- Reduced Motion, 색맹 시뮬레이션 (Polypane/Chrome DevTools) → 주요 FX 대체 여부 수동 확인

## 5. 커맨드 예시 (package.json)
```json
{
  "scripts": {
    "storybook": "storybook dev -p 6006",
    "storybook:test": "chromatic --project-token=<token>",
    "e2e": "playwright test",
    "e2e:ci": "playwright test --reporter=line",
    "lint:styles": "ts-node scripts/check-tokens.ts"
  }
}
```

## 6. 배포 전 체크리스트
- [ ] Storybook 스냅샷(Game/Pro, Reduced Motion) 최신화
- [ ] Playwright 시나리오 통과, 핵심 스냅샷 승인
- [ ] Lighthouse 접근성 점수 ≥ 90
- [ ] Fx 로그(`fxStore`)가 Stage/경고 이벤트를 정확히 기록하는지 확인 (Playwright에서 API 호출)
- [ ] 알림 테스트가 챗봇 대화 기록에도 남는지 확인 (API Stub)

---

**오픈 TODO**
1. Playwright 환경에서 Slack Webhook 등을 모킹하는 유틸 작성 필요
2. Chromatic 통합 시 `Game` / `Professional` / Reduced Motion 세션을 pipeline으로 분리할지 결정
3. CSS Tokens 검증 스크립트(`check-tokens.ts`) 구현
