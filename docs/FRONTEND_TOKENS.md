# Frontend Design Tokens

Goaler 웹앱 구현 시 공통으로 사용하는 색상, 타이포그래피, 간격, 그림자 등 기초 토큰을 정의합니다. 모든 UI 컴포넌트는 이 토큰을 기반으로 작성해야 합니다.

## 1. 색상

### 1.1 Game Theme
| 용도 | 토큰 | 값 |
| --- | --- | --- |
| 배경 | `color.background.surface.game` | `#0B1026` |
| 카드 | `color.background.card.game` | `#161C3A` |
| 기본 텍스트 | `color.text.primary.game` | `#E5E9FF` |
| 보조 텍스트 | `color.text.secondary.game` | `#9AA4D6` |
| 주요 강조 | `color.primary.game` | `#6C5CE7` |
| 성공 | `color.success.game` | `#2CE5A7` |
| 경고 | `color.warning.game` | `#FFB347` |
| 위험 | `color.danger.game` | `#FF5C5C` |
| 포션 하이라이트 | `color.accent.cyan.game` | `#00E0FF` |
| 전리품: 성과 | `color.loot.achievement` | `#FFD166` |
| 전리품: 깨달음 | `color.loot.insight` | `#A6C665` |
| 전리품: 감정 | `color.loot.emotion` | `#C792EA` |
| 그래프 라인 | `color.chart.line.game` | `#6C5CE7` |

### 1.2 Professional Theme
| 용도 | 토큰 | 값 |
| --- | --- | --- |
| 배경 | `color.background.surface.pro` | `#0F172A` |
| 카드 | `color.background.card.pro` | `#111827` |
| 기본 텍스트 | `color.text.primary.pro` | `#F8FAFC` |
| 보조 텍스트 | `color.text.secondary.pro` | `#CBD5F5` |
| 주요 강조 | `color.primary.pro` | `#2563EB` |
| 성공 | `color.success.pro` | `#14B8A6` |
| 경고 | `color.warning.pro` | `#F97316` |
| 위험 | `color.danger.pro` | `#DC2626` |
| 포션 하이라이트 | `color.accent.cyan.pro` | `#38BDF8` |
| 그래프 라인 | `color.chart.line.pro` | `#2563EB` |

### 1.3 중립 색상
| 용도 | 토큰 | 값 |
| --- | --- | --- |
| 경계선 | `color.border.default` | `#1E293B` |
| 공간 분리 | `color.divider` | `rgba(148, 163, 184, 0.24)` |
| 아이콘 비활성 | `color.icon.muted` | `rgba(148, 163, 184, 0.56)` |

## 2. 타이포그래피
| 스타일 | 토큰 | 폰트 | 크기/줄 간격 | 굵기 |
| --- | --- | --- | --- | --- |
| Title 32 | `typography.title.lg` | Outfit (Game) / Work Sans (Pro) | 32 / 40 | 600 |
| Title 24 | `typography.title.md` | Outfit / Work Sans | 24 / 32 | 600 |
| Heading | `typography.heading` | Inter | 20 / 28 | 600 |
| Body | `typography.body` | Inter | 16 / 24 | 400 |
| Small | `typography.small` | Inter | 14 / 20 | 400 |
| Caption | `typography.caption` | Inter | 12 / 16 | 400 |

## 3. 간격 & 레이디우스
| 토큰 | 값 |
| --- | --- |
| `spacing.xs` | 4 |
| `spacing.sm` | 8 |
| `spacing.md` | 12 |
| `spacing.lg` | 16 |
| `spacing.xl` | 24 |
| `spacing.2xl` | 32 |
| `spacing.3xl` | 40 |
| `spacing.4xl` | 48 |
| `radius.sm` | 8 |
| `radius.md` | 16 |
| `radius.lg` | 24 |

## 4. 그림자 & 블러
| 토큰 | 값 |
| --- | --- |
| `shadow.card.game` | `0 24px 60px rgba(19, 21, 41, 0.55)` |
| `shadow.card.pro` | `0 24px 48px rgba(8, 12, 24, 0.45)` |
| `shadow.toast` | `0 12px 32px rgba(0,0,0,0.4)` |
| `glow.success` | `0 0 24px rgba(44, 229, 167, 0.45)` |
| `glow.danger` | `0 0 24px rgba(255, 92, 92, 0.55)` |

## 5. Z-Index 레이어
| 레이어 | 토큰 | 값 |
| --- | --- | --- |
| 기본 콘텐츠 | `z.base` | 0 |
| 고정 헤더/사이드바 | `z.shell` | 20 |
| 모달/드로어 | `z.modal` | 40 |
| FX 레이어 | `z.fx` | 50 |
| 토스트 | `z.toast` | 60 |

## 6. 상태 색상 매핑
| 상태 | Game | Pro |
| --- | --- | --- |
| Stage 승급 | Gradient `#6C5CE7`→`#2CE5A7` | Gradient `#2563EB`→`#14B8A6` |
| 경고 | `#FFB347` | `#F97316` |
| 위험 | `#FF5C5C` | `#DC2626` |
| 회복 | `#00E0FF` | `#38BDF8` |

## 7. 테마 변환 규칙
- 텍스트/아이콘은 항상 테마 토큰으로 렌더링한다.
- Game 테마에는 네온 글로우, Professional 테마에는 디퓨즈드 라인 하이라이트를 사용한다.
- Reduced Motion 모드에서는 색상/outline만 변경한다.

## 8. 참고
- 모든 값은 `frontend/theme/tokens.ts`에서 재사용 가능한 형태로 제공된다.
- 변경 시 본 문서와 TypeScript 토큰 파일을 동시에 업데이트한다.
