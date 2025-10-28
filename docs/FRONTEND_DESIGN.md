# Frontend Architecture & Design Blueprint

> 목적: Goaler의 웹앱을 단계적으로 구현하기 위한 기술/UX 설계 문서.  
> 범위: MVP(애니메이션 제외) → 고급 이펙트/테마 확장까지 전체 로드맵을 포함한다.

---

## 1. 제품 목표 요약
- 기초 디자인 토큰: `docs/FRONTEND_TOKENS.md`
- API 계약: `docs/FRONTEND_API_CONTRACT.md`
- 이펙트 규칙: `docs/FRONTEND_FX_GUIDE.md`
- QA/자동화: `docs/FRONTEND_QA_PLAN.md`
- CLI로 검증된 목표/퀘스트 루프를 **웹 대시보드 + 대화 UI**로 전환한다.
- 사용자 시나리오:
  1. 오늘의 추천 행동/진행 단계를 한눈에 보고 바로 실행한다.
  2. 챗봇과 자연스럽게 대화하며 목표/퀘스트/전리품을 관리한다.
  3. 회고/리포트를 웹에서 확인하고 Slack 등 알림과 연결한다.
- 제약 조건:
  - 초기에는 단일 사용자, 이후 다중 사용자 및 인증(SSO/OAuth) 확장.
  - 애니메이션은 MVP 검증 이후 단계적으로 추가.

---

## 2. 기술 스택 & 공통 규약
| 구분 | 선택 | 비고 |
| --- | --- | --- |
| 프레임워크 | **Next.js (App Router)** | 서버 사이드 렌더링 + 클라이언트 상호작용 균형 |
| 언어 | **TypeScript** | 도메인 모델을 백엔드와 공유하게끔 align |
| 애니메이션 | Framer Motion + Lottie + Tailwind keyframes | `docs/FRONTEND_FX_GUIDE.md`의 FX 규칙 준수 |
| 상태/데이터 | React Query (클라이언트 캐시), Zustand (UI 상태), React Context (테마) |
| UI | Tailwind CSS + Headless UI (모달/탭) + Radix Primitives (Tooltip 등) |
| Form | React Hook Form + Zod (유효성 검사) |
| 국제화 | MVP 단일 언어(한국어). 확장 시 next-intl 도입 |
| 테스트 | Vitest + React Testing Library (컴포넌트), Playwright (E2E) |
| 품질 | ESLint, Prettier, Husky (pre-commit), Storybook (UI 카탈로그) |
| 빌드/배포 | Vercel (프리뷰), CloudFront/S3 or Netlify (정식), GitHub Actions (CI) |

**API 통신 표준**
- `/api/v1/...` REST 엔드포인트 (FastAPI/Flask로 추출 예정)  
- 응답 형식: JSON, snake_case → camelCase 변환은 프론트에서 처리  
- 에러 표준: `{ code, message, details? }`

---

## 3. 애플리케이션 구조
```
frontend/
 ├─ src/
 │   ├─ app/ (Next.js 라우팅)
 │   │   ├─ layout.tsx (AppShell: 헤더/사이드바)
 │   │   ├─ dashboard/page.tsx
 │   │   ├─ chat/page.tsx
 │   │   ├─ goals/[goalId]/page.tsx
 │   │   ├─ reports/page.tsx
 │   │   └─ settings/reminders/page.tsx
 │   ├─ components/
 │   │   ├─ dashboard/
 │   │   ├─ chat/
 │   │   ├─ goals/
 │   │   ├─ shared/
 │   │   └─ fx/ (후속 단계 애니메이션 컴포넌트)
 │   ├─ hooks/ (공용 훅)
 │   ├─ lib/ (API 클라이언트, 타입)
 │   ├─ stores/ (Zustand 상태)
 │   ├─ styles/
 │   └─ tests/
 └─ public/ (아이콘/폰트)
```

### 3.1 라우팅 & 네비게이션
- 전역 AppShell: 로고·Stage 표시 헤더 + 좌측 내비 (Dashboard / Chat / Goals / Reports / Settings)
- 반응형 디자인: 모바일에서 하단 탭, 데스크톱은 사이드바
- 인증 이후 확장 대비: `/login` 페이지는 Phase 1에서는 숨김, Phase 2에서 OAuth 연동

### 3.2 상태 관리 전략
| 유형 | 도구 | 설명 |
| --- | --- | --- |
| 서버 데이터 (목표, 퀘스트, 전리품, 알림) | React Query | API 응답 캐시, Optimistic Update, background refetch |
| UI 상태 (모달, 토스트, 테마) | Zustand | 독립 스토어, SSR 영향 없음 |
| FX 큐 | Zustand `fxStore` | 현재 재생 중인 FX 상태, 중복 실행 제한 및 접근성 토글 |
| 대화 세션 | React Query + WebSocket (추후) | 초기엔 폴링, 이후 스트리밍으로 전환 |

### 3.3 데이터 모델 매핑 (요약)
| 프런트 타입 | 백엔드 테이블/엔드포인트 | 설명 |
| --- | --- | --- |
| `GoalSummary` | `GET /goals` | 대시보드 카드용 요약 |
| `GoalDetail` | `GET /goals/:id` | 핵심 퀘스트·주간 단계 포함 |
| `QuestSummary` | `GET /goals/:id/quests/today` | 오늘 추천 퀘스트 |
| `QuestLog` | `POST /quests/:id/logs` | 전리품 기록 |
| `Reminder` | `GET/POST/PATCH /reminders` | 알림 설정 |
| `Report` | `GET /reports/monthly` | LLM 요약 포함 |
| `ChatMessage` | `POST /chat` | 챗봇 대화 (Function Calling) |

### 3.4 주요 컴포넌트 분류
| 범주 | 컴포넌트 | 설명 |
| --- | --- | --- |
| 레이아웃 | `AppShell`, `SidebarNav`, `TopBar` | 공통 스켈레톤, 반응형 대응 |
| 대시보드 | `HeroCard`, `QuestCarousel`, `ChecklistItem`, `LootHighlight` | 진행 단계/테마 props 지원 |
| 챗 | `ChatMessage`, `ChatComposer`, `ChatContextPanel` | 메시지 유형별 스타일, 추천 액션 슬롯 |
| 목표 | `BossList`, `BossTimeline`, `WeeklyStepList`, `QuestCard`, `LootTabs` | 게임/전문가 테마 토글, 진행 단계에 따른 비활성화 |
| 리포트 | `ReportSummaryCard`, `StoryCard`, `MetricChart`, `ReportFilterBar` | 차트는 Recharts/D3 래퍼로 구성 |
| 설정 | `ReminderForm`, `ChannelToggle`, `TimePicker`, `SlackTestBanner` | Form 상태 관리 (React Hook Form) |
| 공통 | `Badge`, `Card`, `Modal`, `Toast`, `Tooltip`, `EmptyState` | 디자인 시스템 기반 |
| FX (후속) | `fx/BossDamageEffect`, `fx/QuestCompleteBurst`, `fx/StageUpgradeAura` | Storybook으로 독립 시연, prefers-reduced-motion 존중 |
| FX 컨트롤 | `fx/FxProvider`, `fx/FxLayer`, `fx/FxToggleButton` | FX 큐, 레이어 렌더링, Reduced Motion 스위치 |

### 3.5 FX 시스템 개요
- 상세 규칙은 `docs/FRONTEND_FX_GUIDE.md`에서 색상/모션/이벤트별 플레이북을 따른다.
- `FxProvider`가 글로벌 FX 큐(Zustand)를 관리하고, 각 화면은 `FxLayer` 컴포넌트로 효과를 렌더링한다.
- 모든 FX는 테마 토큰(`theme.fx`)과 접근성 설정(`prefersReducedMotion`)을 고려한다.

### 3.6 Storybook & 테스트 커버리지
- Storybook 스토리 구조는 `Component/State/Theme/Motion`으로 맞춘다.
  - 예: `HeroCard/StageUpgrade/Game`, `HeroCard/StageUpgrade/Pro`, `HeroCard/StageUpgrade/Reduced`.
- 필수 스토리 목록
  - `AppShell` (Game/Pro, Mobile/Desktop)
  - `HeroCard` (기본, Stage 승급, 경고)
  - `QuestCard` (난이도별, 완료 상태)
  - `ChecklistItem` (기본, 완료, 경고)
  - `LootChip` (성과/깨달음/감정)
  - `ChatMessage` (유저/AI/시스템, 로딩)
  - `BossTimeline` (성공, 경고, 조정 필요)
  - `ReminderForm` (기본, 실패, 테스트 성공)
  - FX 전용(`fx_stage_upgrade`, `fx_quest_complete`, `fx_energy_warning`, Reduced 모드)
- 각 스토리는 `prefersReducedMotion` 토글, 테마 전환 버튼을 Storybook Controls로 제공한다.

컴포넌트는 atomic → organism → template 순으로 예측 가능하게 이름을 붙인다. 스토리북에서 상태(기본/경고/성공), 테마(게임/전문가), 해상도(데스크톱/모바일) 스토리를 제공한다.

---

## 4. 화면별 설계 (MVP 기준)

### 4.1 Dashboard
**목표**: 사용자가 접속 즉시 “오늘 무엇을 해야 하는지”를 파악하고 실행하도록 돕는다. 정보 우선순위는 “행동 → 진척 → 회고”.

구성 블록
- **Hero 카드**
  - 좌측: 현재 진행 단계 이름 + 핵심 퀘스트/마일스톤 이름 + 작은 아이콘 (게임/전문가 테마에 따라 변경)
  - 상단 Progress Bar: 준비 단계 완료율 (완료/전체) → 색상은 에너지 상태에 따라 바뀜
  - 경고 배너: Warning/Critical/Emergency 시 버튼 2개(회복 루틴, 보완 퀘스트) + `fxShakeSoft`
  - 하단 CTA: 오늘의 추천 퀘스트/포션 의식/회고 이동 버튼 (`fxSlideUp` 토스트와 연동)
- **오늘의 추천 행동 영역**
  - 수평 카드 캐러셀 (한 화면에 2개, 내비게이션 화살표)
  - 카드 내 요소: 난이도 배지, 예상 소요 시간, 변주 이유, “상세 보기”
  - 완료/보류/건너뛰기 버튼 노출
- **일일 체크리스트**
  - 표 형태가 아닌 카드 리스트, 각 항목은 체크박스 + 결과 버튼 3개
  - 메모 입력 란 (선택), 전리품 안내 문구
- **전리품 하이라이트 & 회고 CTA**
  - 당일 전리품 칩 2개까지 노출 (성과/깨달음/느낌 컬러 칩)
  - “주간 회고” 버튼 → Reports 화면 이동 시 Explore 패널 `fxSlideUp`

UX 주의 사항
- 12-column 그리드 기준: Hero 카드(8) + 체크리스트(4) → 모바일에서는 세로 스택
- Skeleton 로딩, Empty state (“오늘 퀘스트가 준비 중입니다”)
- 토스트/Alert 구성: 성공/실패/건너뛰기 결과 표시

### 4.2 Chat
**목표**: 챗봇 대화와 대시보드 데이터가 자연스럽게 연결되도록 한다.

레이아웃
- 좌측 70%: 대화 로그 (AI/사용자/시스템 메시지 구분) — 메시지 도착 시 240ms Pulse
- 우측 30%: “컨텍스트 패널” – 현재 목표, 전리품, 에너지 상태, 빠른 액션 버튼 (FX 상태에 따라 오라/경고 표시)
- 입력 영역: 텍스트 필드 + 추천 버튼 묶음 (예: “오늘 퀘스트 완료”, “알림 바꾸고 싶어요”), 전송 성공 시 미니 `fxBurst`

기능 포인트
- 메시지가 도착하면 오른쪽 패널도 함께 업데이트 (React Query invalidate) + `FxLayer`가 자동 오라 재생
- 로딩 상태: 말풍선 스켈레톤 + “Goaler가 생각 중…” indicator, Game=네온 Pulse / Pro=라인 Shimmer
- 오류 대응: 재전송 버튼, 최근 실패 메시지 하이라이트
- 모바일: 대화만 전체 화면, 오른쪽 패널은 아이콘 버튼으로 모아서 모달로 열기

### 4.3 Goals (List & Detail)
**Goals List**
- 카드 그리드 (3열 → 모바일 1열), 진행 단계 배지/진척률/다음 퀘스트 정보를 간단히 노출
- 필터: 진행 단계, 테마, 진행 상태(활성/잠금/완료)
- “새 목표” CTA는 Phase 2부터 활성화 (현재는 챗봇 생성 우선)

**Goal Detail**
1. **핵심 퀘스트 타임라인**
   - 좌측: 핵심 퀘스트 목록 (상태 배지, 목표 주차, 성공 기준)
   - 우측: 선택한 핵심 퀘스트의 주간 단계 스텝 + 일일/대안 퀘스트 체크리스트 (`fxBurst`)
2. **일일 기록 보관함**
   - 탭: Memory Shard / Combo Gem / Relic
   - 카드: 칩 아이콘, 한 줄 텍스트, 날짜, 연관 핵심 퀘스트
3. **알림 카드**
   - 현재 설정 요약, 빠른 끄기/켜기, “상세 설정” 버튼
4. **챗봇 하이라이트**
   - 최근 대화 요약, 추천 변주/회복 안내 (`fxAura`/경고 시 붉은 오라)

Empty State: 초기 진행 단계 사용자는 “핵심 퀘스트 미리보기”(설명 카드)만 노출, 체크리스트는 숨김.

### 4.4 Reports
**목표**: “내가 얼마나 성장했는지”를 스토리+숫자로 보여주고 다음 행동을 제시.

구성
- 상단: 기간 선택 (월간/주간), Goal 필터, 날짜 드롭다운 — Level Up 시 `fxAura`
- 성장 서사 영역: LLM summary 텍스트 카드 + 공유 버튼 (클릭 시 `fxSlideUp` 모달)
- 지표 영역: 전리품 분포(도넛 차트), 퀘스트 완료 추이(line chart), 에너지 상태 히트맵
- 회고 CTA: 다음 주 전략(공격/보완/회복) 선택 (`fxPulse`)
- Professional 테마에서는 그래프 색상이 Blue tone, 데이터 라벨에 얇은 underline을 추가해 신뢰감을 높인다.

상태 대응
- 데이터 없음 → “전리품을 남기면 여기에서 이야기를 만들어 드릴게요” 메시지
- 로딩 → Skeleton + 그래프 placeholder
- 에러 → Retry 버튼

### 4.5 Settings > Reminders
**목표**: 알림 채널/주기를 쉽게 관리하고, 필요할 때 끌 수 있게 한다.

구성
- 목표 목록 + 토글: 각 목표 별로 퀘스트/회고 알림 on/off
- 채널 섹션: Slack Webhook, 시간대/요일 선택 (React Hook Form)
- 테스트 버튼: “테스트 메시지 보내기” → 성공/실패 토스트 + Cyan Pulse
- 향후 이메일/SMS 확장을 고려해 탭/아코디언 구조 유지
- 테스트 성공 여부와 최근 알림 상태는 챗봇 대화 패널에 ‘알림 로그’ 메시지로 자동 공유되어 사용자가 진행 흐름을 잃지 않도록 한다.

빈 상태: 알림이 하나도 없을 경우 “알림을 켜두면 챗봇이 잊지 않게 도와드려요” 메시지 + CTA

### 4.6 Game Feel & 테마 가이드
`docs/FRONTEND_FX_GUIDE.md`에서 정의한 색상/모션 규칙을 반영하여 테마별 연출을 구성한다.

- 진행 단계 변환
  - 승급 시: Hero 카드 상단에 1.2초간 축하 배너 + Progress Bar 색상 전환
  - 단계 하락 위험: 경고 배너 + “손실 방지” CTA를 항상 함께 표시
- 난이도/에너지 피드백
  - 카드마다 난이도 배지 색상(초록/주황/빨강) + 아이콘(방패/검)
  - 에너지 상태 `NEEDS_POTION`일 때 Hero 카드 배경을 부드럽게 펄스
- 전리품 감성
  - Memory Shard: 유리 조각 아이콘, 살짝 빛나는 애니메이션(Phase FE-6)
  - Combo Gem: 모서리에 작은 콜렉션 카운터 (3개 달성 시 색상 변화)
- 테마 전환 (GAME ↔ PROFESSIONAL)
  - 용어, 아이콘, 컬러 팔레트를 `ThemeContext`로 교체 (ex: 보스전 → 핵심 마일스톤)
  - 공용 컴포넌트는 `variant="game" | "pro"` prop으로 스타일 제어
  - Professional 테마는 저채도 배경(카드 Linear Gradient `#111827`→`#0B1220`), 라인 애니메이션, 데이터 엑센트(파란색 라인 그래프 강조)를 기본으로 한다.
- 접근성 강화
  - Reduced Motion 환경에서는 FX 대신 outline/색상 강조만 사용하고, 상태 변화가 텍스트와 아이콘으로도 전달되도록 한다.
- 접근성 고려
  - 애니메이션은 기본 0.6~1.2초 범위, `prefers-reduced-motion` 시 fade-in만 적용
  - 색맹 친화 팔레트(적/초록 조합 금지), 배지에는 텍스트 라벨 함께 표기


---

## 5. API 계약 (요약)
| Method | Path | 용도 | 비고 |
| --- | --- | --- | --- |
| GET | `/goals` | 목표 카드 리스트 | 진행 단계/진행률 포함 |
| GET | `/goals/:id` | 목표 상세 | 핵심 퀘스트·주간·일일 구조 |
| POST | `/goals` | 새로운 목표 (챗봇 or UI) | 차후 정식 API 계획 |
| POST | `/quests/:id/logs` | 퀘스트 완료/전리품 기록 | outcome, lootType 등 |
| GET | `/quests/today` | 오늘 추천 리스트 | 챗봇 변주 포함 |
| POST | `/reminders` | 알림 생성 | channel/time/payload |
| PATCH | `/reminders/:id` | 알림 수정 | on/off, 시간 변경 |
| POST | `/chat` | 대화 메시지 → LLM 응답 | Function call 응답 포함 |
| GET | `/reports/monthly?goalId` | 월간 리포트 | 성장 서사 텍스트 포함 |

> 백엔드가 아직 CLI 형태이므로, FastAPI/Flask 백포트를 Phase FE-0에서 진행. Swagger/OpenAPI로 문서화 예정.

---

## 6. 접근성 & 국제화 체크
- 명도 대비 4.5:1 이상 (테마별 컬러 팔레트 사전 정의)
- 키보드 내비 완전 지원 (Tab 순서, ARIA 라벨)
- 모든 애니메이션/이펙트는 `prefers-reduced-motion` 존중 (Phase 2에서 적용)
- 텍스트는 i18n 대응을 염두(문자열 키 사용)하되, MVP는 한글 고정

---

## 7. 테스트 전략
| 구분 | 도구 | 주요 시나리오 |
| --- | --- | --- |
| 단위 테스트 | React Testing Library | 카드/모달 렌더링, 버튼 상호작용 |
| 스냅샷 | Storybook + Chromatic | 컴포넌트 회귀 테스트 |
| 통합 | Playwright e2e | 목표 생성→퀘스트 완료→전리품 기록→리포트 확인 |
| 접근성 | axe-core | 주요 화면 a11y 검증 |
| 퍼포먼스 | Lighthouse | LCP, TBT, CLS 목표 설정 |

테스트 자동화 파이프라인은 GitHub Actions에서 구동, Vercel 프리뷰 링크와 함께 QA가 확인.

---

## 8. 구현 단계 (로드맵)
| 단계 | 내용 | 완료 기준 |
| --- | --- | --- |
| **FE-0 API 게이트웨이** | FastAPI로 CLI 기능 노출 (REST) | `/api/v1/...` 호출 가능, Swagger 문서 |
| **FE-1 Shell & Dashboard** | AppShell, Dashboard 데이터 표시 | 목표/퀘스트 API 연결, 기본 체크리스트 동작 |
| **FE-2 Chat 통합** | 실시간 대화 + 결과 반영 | `POST /chat` 연결, 상태 자동 갱신 |
| **FE-3 Goals & Reports** | 목표 상세/리포트 화면 | 핵심 퀘스트 타임라인, 리포트 조회 |
| **FE-4 Settings & Reminders** | 알림 CRUD UI | Slack 설정/변경, 성공 메시지 |
| **FE-5 QA & Accessibility** | 테스트, a11y, 성능 | Lighthouse 90+, axe 오류 0 |
| **FE-6 Progressive FX** | 애니메이션 컴포넌트 추가 | docs/FX_GUIDE.md 완성, Storybook 시연 |

애니메이션 작업은 FE-6에서 Stage별 효과를 컴포넌트로 분리하고, `fx/` 디렉터리에 정리한다.

---

## 9. 남은 결정 사항 (TBD)
- 다중 사용자 인증 UX (Phase FE-7): OAuth 흐름, 사용자 전환 UI
- 모바일 전용 최적화: 하단 탭/제스처
- 고급 이펙트 명세: `docs/FX_GUIDE.md` 신규 작성 후 Storybook 기반 QC
- Slack 그 외 채널(이메일/SMS) 확장 시 UX 고려

---

## 10. 참고 문서 링크
- `docs/UX_FLOW.md` : 전체 사용자 여정
- `docs/UX_CONVO_FLOW.md` : 챗봇 변주 대화 스크립트
- `docs/UX_WIREFRAME_NOTES.md` : 핵심 퀘스트/일일 기록 UI 힌트
- `docs/DEVELOPMENT_PLAYBOOK.md` : 전체 개발 단계, Phase 6 이후 백로그
- `docs/OPERATIONS_SOP.md` : 운영/알림 절차
- `docs/LLM_USAGE_GUIDE.md` : 비용·한도 정책

---

> 이 문서는 프런트엔드 구현 전 사전 합의 용도로 사용하며, 구현 중 변경 사항은 PR과 함께 갱신한다.
