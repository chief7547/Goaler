# Boss Stage Examples

> 목적: `docs/BOSS_DESIGN_GUIDE.md`에서 정의한 절차를 구체적으로 실행할 때 참고할 수 있는 예시를 제공한다. 
> GoalSettingAgent와 CLI가 동일한 규칙으로 보스전(핵심 마일스톤)을 생성하도록 Stage 코드, 필드 예시, 대화 샘플을 정리했다.

## 1. Stage 라벨 권장 표기
`DATA_SCHEMA.yaml`의 `player_progress.stage_label`과 온보딩 문서(Stage 0/0.5/1…)를 연결하기 위해 다음 표준을 사용한다.

| 코드 | 온보딩/Stage 명칭 | 설명 |
| --- | --- | --- |
| `STAGE_0_ONBOARDING` | Stage 0 – Spark Awakening | 전리품/에너지 비노출, 기초 루프 학습 |
| `STAGE_0_5_LOOT` | Stage 0.5 – Loot Introduction | 전리품 칩만 해금 |
| `STAGE_1_ENERGY` | Stage 1 – Energy Awareness | 에너지 버튼/회복 루틴 해금 |
| `STAGE_1_5_BOSS_PREVIEW` | Stage 1.5 – Boss Preview | 핵심 마일스톤 카드 미리보기 |
| `STAGE_2_ASCENSION` | Stage 2 – Ascension Path | 전체 보스/변주 시스템 해금 |
| `STAGE_3_SUMMIT` | Stage 3 – Summit Breakthrough | 장기 목표 마무리 단계 |

> 스키마 저장 시 `stage_label` 필드는 위 코드 중 하나를 사용하고, UI/리포트에서 사람이 읽는 문구는 `docs/PRODUCT_SPEC.md` Stage 테이블을 따른다.

## 2. 도메인별 보스전 예시
아래 예시는 `boss_stages` 레코드 생성 시 참고하는 샘플이다. Stage 진행 순서(`stage_order`)와 목표 주차(`target_week`)는 사용자의 일정에 맞춰 조정한다.

### 2.1 운동/건강 – “1년 안에 하프마라톤 완주”
| 필드 | 값 | 비고 |
| --- | --- | --- |
| `goal_id` | `goal_running_2025` | 예시용 UUID |
| `boss_id` | `boss_running_form` | |
| `title` | 러닝 폼 교정 세션 완료 | 현실 과업 명사형 |
| `description` | 코치와 일대일 레슨으로 착지/호흡 교정 | 왜 중요한지 |
| `success_criteria` | 레슨 피드백 시트 제출 | 측정 가능한 지표 |
| `stage_order` | 1 | Stage 1 진입 전 |
| `target_week` | 4 | 주차 기준 |
| `status` | `READY` | 초안 생성 후 | 

추가 보스전
```
2. 주간 30km 주행 루틴 적응 (stage_order=2, target_week=8)
3. 하프마라톤 예행연습 참가 (stage_order=3, target_week=20)
4. 공식 하프마라톤 완주 (stage_order=4, target_week=26, status=PLANNED)
```

### 2.2 사업/프로젝트 – “사이드 프로젝트 첫 매출 100만 원”
| 필드 | 값 |
| --- | --- |
| `goal_id` | `goal_sidebiz_2025`
| `boss_id` | `boss_business_license`
| `title` | 사업자등록 완료 |
| `description` | 홈택스 신청 및 사업자등록증 발급 |
| `success_criteria` | 사업자등록증 사본 확보 |
| `stage_order` | 1 |
| `target_week` | 6 |
| `status` | `IN_PROGRESS` |

후속 보스전:
1. 첫 고객 인터뷰 3건 완료 (`stage_order`=2, `target_week`=9)
2. MVP 베타 공개 (`stage_order`=3, `target_week`=12)
3. 첫 유료 결제 처리 (`stage_order`=4, `target_week`=16)

### 2.3 학습/자격 – “6개월 안에 데이터 분석 자격증 취득”
- `boss_id`: `boss_mock_exam`
- `title`: 모의고사 1회 응시 및 분석
- `success_criteria`: 점수표 업로드 + 오답노트 5항목 작성
- `stage_order`: 2 (`target_week`=10, status=`PLANNED`)

추가 예시: 기출문제 풀이 50%, 온라인 스터디 발표, 본 시험 응시/합격.

## 3. JSON 스니펫 예시
보스전 생성 후 저장소에 기록되는 구조 예시. (필드는 필요 시 추가)

```json
{
  "boss_id": "boss_business_license",
  "goal_id": "goal_sidebiz_2025",
  "title": "사업자등록 완료",
  "description": "홈택스 신청 및 사업자등록증 발급",
  "success_criteria": "사업자등록증 사본 확보",
  "stage_order": 1,
  "status": "READY",
  "target_week": 6,
  "created_at": "2025-01-20T09:00:00Z",
  "updated_at": "2025-01-27T11:30:00Z"
}
```

## 4. 인터뷰/대화 예시
챗봇이 사용자와 함께 보스전을 정의할 때 활용할 수 있는 흐름.

1. **챗봇**: “이번 목표를 이루기 위해 반드시 넘어야 하는 큰 단계가 있다면 무엇일까요? 예를 들어 ‘사업자등록 완료’처럼요.”
2. **사용자**: “사업자등록이 제일 먼저 필요할 것 같아요.”
3. **챗봇**: “좋아요. 언제까지 완료하고 싶으신가요? 성공했다고 확인할 수 있는 기준도 같이 정해볼까요?”
4. **사용자**: “6주 안에 끝내고, 등록증 사본을 받으면 완료라고 볼게요.”
5. **챗봇**: `define_boss_stages` 호출 → 위 값 저장.
6. **챗봇**: “다음 보스로는 첫 고객 인터뷰 3건을 추천드릴게요. 괜찮으면 그대로 등록하고, 아니면 수정해도 좋아요.”

## 5. 체크리스트
- [ ] 제목은 명확한 현실 과업(명사형)인가?
- [ ] 성공 기준이 측정 가능한가?
- [ ] Stage 순서가 실제 로드맵과 일치하는가?
- [ ] `target_week`이 사용자 일정과 호흡이 맞는가?
- [ ] 테마(게임/전문가)에 따라 용어를 바꿔야 하는가? → 대시보드/UI 렌더 시 `theme_preference` 반영.
