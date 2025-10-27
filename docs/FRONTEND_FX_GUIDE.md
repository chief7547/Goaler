# Frontend FX & Motion Guide

> 목적: Goaler의 "현실을 게임처럼" 경험을 웹에서 구현하기 위한 색상, 모션, 이펙트 설계를 구체화한다.  
> 범위: MVP~Phase 2 (몰입형 FX)까지의 공통 규칙과 이벤트별 연출, 접근성 가이드, 산출물 파이프라인을 포함한다.

---

## 1. 디자인 비전 & 원칙
1. **주도적 성장 감정**: 연출은 “내가 직접 올린 성과”를 강조해야 하며, 과도한 자동 연출은 피한다.
2. **모험 + 전문가 혼합**: 게임 테마는 활기찬 색·모션, 전문가 테마는 차분한 하이라이트와 데이터 강조로 차별화한다.
3. **에너지 기반 피드백**: 섬광·오라 등은 에너지 상태(READY/KEEPING/NEEDS)를 즉시 알아볼 수 있게 한다.
4. **회복의 여백**: 정보 전달이 최우선이므로 모든 FX는 2.4초 이내 종료, 인터랙션을 막지 않는다.
5. **접근성 우선**: `prefers-reduced-motion` 사용 시 FX는 축약된 색상 강조/페이드로 대체된다.

---

## 2. 테마별 색상 팔레트 & 소재
| 카테고리 | Game Theme | Professional Theme | 용도 |
| --- | --- | --- | --- |
| 기본 배경 | `#0B1026` (Midnight Indigo) | `#0F172A` (Deep Slate) | 앱 배경, 히어로 카드 |
| 카드 배경 | `#161C3A` | `#111827` | 3D 카드(살짝 블러) |
| 주요 강조 | `#6C5CE7` (Arcane Violet) | `#2563EB` (Pacific Blue) | CTA, 진행률, 보스 게이지 |
| 성공/축하 | `#2CE5A7` (Sprite Green) | `#14B8A6` (Teal) | 퀘스트 완료, FX Glow |
| 경고 | `#FFB347` (Sunburst Amber) | `#F97316` (Warm Orange) | 에너지 경고, 텍스트 배지 |
| 위험 | `#FF5C5C` (Cinder Red) | `#DC2626` (Signal Red) | Emergency, Fail FX |
| 포션 하이라이트 | `#00E0FF` (Potion Cyan) | `#38BDF8` (Light Azure) | 회복 관련 FX |
| 전리품 칩 | 성과 `#FFD166`, 깨달음 `#A6C665`, 감정 `#C792EA` | 동일 색, 채도 80%로 감소 | 칩, 리포트 뱃지 |

**빛/입자 소재**
- Game: 네온 그라디언트(Arcane Violet ↔ Sprite Green), 반짝입자(2px~6px, 투명도 40%).
- Professional: 디퓨즈드 글로우(반경 32px, 투명도 20%), 얇은 라인 모션.

---

## 3. 모션 프리미티브
| 이름 | 지속시간 | Easing | 설명 |
| --- | --- | --- | --- |
| `fx_fade_in` | 240ms | `cubic-bezier(0.34, 0.97, 0.64, 1)` | 카드/알림 등장 |
| `fx_pulse` | 840ms | InOutSine | Hero/Progress pulse, 최대 1.05 스케일 |
| `fx_burst` | 520ms | OutBack | 퀘스트 완료 시 파티클, 180° 확산 |
| `fx_aura` | 1600ms | InOutSine | Stage 업그레이드 오라, 3회 반복 |
| `fx_shake_soft` | 440ms | InOutQuad | 실패/경고 진동, ±6px, 2회 |
| `fx_slide_up` | 320ms | OutCubic | 토스트/패널 슬라이드 |

`prefers-reduced-motion` 시에는 위 모션 대신 투명도 0→1, 배경 색상 교체 등 정적 변화를 사용한다.

### 3.1 Reduced Motion 매핑
| FX ID | 기본 연출 | Reduced Motion 대체 |
| --- | --- | --- |
| `fx_fade_in` | 240ms Fade + Scale 1.02 → 1 | 단순 투명도 전환 0→1 |
| `fx_pulse` | Scale 1.0 ↔ 1.05, 불빛 확장 | 카드 테두리 색상만 600ms 동안 강조 |
| `fx_burst` | 입자 확산 520ms | 배경색 120ms 하이라이트 + 체크 아이콘 색상 변화 |
| `fx_aura` | 네온 오라 3회 반복 | 카드 주변 Outline 2px 추가 후 400ms 유지 |
| `fx_shake_soft` | 좌우 ±6px 진동 2회 | 빨간 라벨과 아이콘으로만 경고 표시 |
| `fx_slide_up` | translateY 24px → 0, opacity | opacity 0→1 + border-top 강조 |

---

## 4. 이벤트 연출 매트릭스
| 이벤트 | 트리거 | 위치/레이어 | 시각 요소 | 복구/겹침 규칙 |
| --- | --- | --- | --- | --- |
| Stage 승급 (예: Stage 0→0.5) | `onboarding_stage` 변경 | Dashboard Hero 카드 전체 + 헤더 Stage 배지 | `fx_aura` + 카드 배경에 4색 그라데이션, Stage 문자 확대 1.12x → 1초 후 원복, 축하 토스트 | 다른 FX보다 우선, 4초 재사용 금지 |
| 퀘스트 완료 | 체크리스트 CTA 클릭 → 성공 반환 | 체크리스트 아이템, Hero 진행률 | 체크 표시가 `fx_burst`, 아이템 배경 `fx_pulse` 1회 | 동일 아이템 중첩 방지, 완료 상태 유지 |
| 전리품 기록 | Loot 칩 저장 시 | 전리품 칩, 회고 모듈 | 칩이 위로 32px 이동 후 내려앉으며 글로우 (Game=네온, Pro=은은한 라인) | 모션 후 칩 상태 고정 |
| 에너지 Warning/Critical/Emergency | 로그 `energy_status` 업데이트 | Hero 카드 경고 배너, 헤더 아이콘 | Game: 배너 `fx_shake_soft` + Amber/Red 글로우, Professional: 라인 강조 + 색상 전환 | Emergency 진동은 1회만 허용 |
| 포션 의식 제안 | 에너지 상태가 연속 2회 이하로 떨어졌을 때 | 챗 컨텍스트 패널, CTA 버튼 | Game: Cyan 포션 버블이 위로 올라가며 사라짐, Professional: 채워지는 Gradient 바 | 15초 내 재생성 금지 |
| 보스 성공 콘페티 | 보스 `status` → `COMPLETED` | 목표 상세 상단 | Game: 입자 24개, 중심에서 확산, Professional: 가느다란 라인 3개 | 다른 보스 카드에 영향 없음 |
| 보스 재조정 제안 | `boss_adjustment_needed` = true | 목표 상세 > 보스 타임라인 | 카드 좌측 붉은 오라 + `fx_shake_soft` 1회, 배너 텍스트 “전략 조정 필요” | 사용자가 “조정 완료” 누르면 FX 제거 |
| 연속 콤보(3일 이상) | Quest streak | Dashboard Hero Progress | Game: 작은 불꽃 로고 + InOutSine 플로팅, Professional: 얇은 라인 그래프 애니메이션 | 콤보 끊기면 300ms FadeOut |
| Slack 리마인더 미발송 경고 | API 실패 | Settings > ReminderForm | Scarlet 경고 배너, `fx_shake_soft` 1회, 톤다운된 아이콘 | 문제 해결 후 FadeOut |

각 이벤트는 Storybook에서 “Game” / “Professional” / “Reduced Motion” 세 가지 스토리로 시연한다.

---

## 5. 기술 구현 지침
1. **애니메이션 도구**: Framer Motion (React) + Tailwind keyframes. 복잡한 FX는 Lottie(JSON)로 내보내되 2D 애니메이션만 허용.
2. **레이어 구조**: Hero/카드 등 FX는 `fx-layer` 절대 포지션 요소(포인터 이벤트 없음)로 분리해 정보 레이어를 가리지 않도록 한다.
3. **상태 연동**: React Query의 mutation success 콜백에서 FX 트리거.
4. **FX 큐 (`fxStore`)**
   ```ts
   type FxPayload = {
     id: "stage_upgrade" | "quest_complete" | "energy_warning" | "boss_adjust" | string;
     priority: 1 | 2 | 3; // 1: 높음
     duration: number; // ms
     meta?: Record<string, unknown>;
   };

   interface FxState {
     queue: FxPayload[];
     prefersReducedMotion: boolean;
     pushFx(fx: FxPayload): void;
     popFx(id: string): void;
     setReducedMotion(flag: boolean): void;
   }
   ```
   - 우선순위 규칙: Stage 업그레이드(1) > 보스 성공/재조정(2) > 일반 퀘스트/알림(3)
   - 동일 ID 중복 방지, 동시에 3개 이상일 때 priority가 가장 낮은 FX부터 대기열로 이동
   - Reduced Motion 켜짐 시 ID에 `_reduced` suffix를 붙여 대체 연출 사용
5. **테마 토큰**: 색상·그라디언트는 `theme.fx` 토큰으로 정의, CSS 변수(`--fx-accent`)를 통해 적용.
6. **성능**: GPU 가속되는 transform/opacity만 사용, box-shadow 반복 금지. 3개의 FX 이상 동시 실행 시 가장 우선도가 낮은 FX부터 중단.

---

## 6. 접근성 & 안전장치
- `prefers-reduced-motion`: 애니메이션 대신 색상 전환/아이콘 변화만 사용.
- 대비 비율: 모든 텍스트 대비 4.5:1 이상, FX Glow는 배경 대비 3:1 이상 확보.
- 색맹 친화: 주요 상태(성공/경고/위험)는 색 + 아이콘 형태(✔︎, !, ×)를 함께 노출.
- 키보드: FX는 포커스 이동을 방해하지 않는다. 포커스 링은 항상 유지.
- 재생 속도 제한: 어떤 FX도 2.4초 이상 지속되지 않으며, 반복은 최대 3회.

---

## 7. 산출물 파이프라인
1. **Design**: Figma 컴포넌트 (Game/Professional 변형, 애니메이션 시퀀스) → Lottie/PNG/GLTF 에셋.
2. **Storybook**: 각 컴포넌트 스토리(`.stories.tsx`)에 FX 시연 상태 추가. 스토리 이름 규칙 `Component/State/Theme`.
3. **자산 버전 관리**: `/frontend/public/fx/`에 버전별로 저장. Lottie는 파일명에 버전 포함 (`stage-aura.v1.json`).
4. **QA**: Playwright 시나리오에서 FX 발생 여부를 스냅샷(감소 모션 모드 포함)으로 검증. Chrome DevTools `prefers-reduced-motion` 테스트 필수.

---

## 8. QA 체크리스트
- [ ] Stage 승급 시 Hero 카드에 aura가 1.6초 동안 3회 맥동한다.
- [ ] 퀘스트 완료 시 체크리스트 항목에서 burst 효과 후 완료 상태가 유지된다.
- [ ] `NEEDS_POTION` 경고가 발생하면 헤더 아이콘과 배너가 동시에 색과 진동으로 표시된다.
- [ ] Reduced-motion 설정 시 모든 FX가 즉시 단색/투명도 전환으로 대체된다.
- [ ] Professional 테마에서 모든 색상이 저채도 톤으로 바뀌고, 빛줄기 대신 라인 애니메이션이 사용된다.
- [ ] FX 실행 중에도 버튼/입력 포커스를 잃지 않는다.
- [ ] FX 로그가 `fxStore`에 남아 중복 실행이 제한되는지 확인한다.
- [ ] Stage 승급과 퀘스트 완료가 동시에 발생했을 때 priority 규칙(승급 우선)이 지켜진다.
- [ ] Storybook Reduced Motion 스토리가 실제 환경과 동일한 대체 연출을 보여준다.

---

## 9. 후속 로드맵
- Phase 2: 실시간 WebSocket 스트리밍으로 챗 FX 동기화, 다중 사용자 이벤트(팀 콜라보) 도입.
- Phase 3: 모바일 네이티브 앱(React Native)으로 동일 모션 시스템 이식, 햅틱 피드백 추가.
- Phase 4: AR(증강현실) 실험을 위한 3D 자산 제작 지침 정의.

본 가이드는 프런트엔드·디자인 팀이 기능을 구현할 때마다 업데이트하며, Storybook/UX QA에서 발견된 개선 사항을 Flow/SDT 원칙에 맞게 반영한다.
