# Frontend Implementation Checklist

> 컨텍스트가 초기화된 뒤에도 같은 품질로 프런트엔드를 구현할 수 있도록 준비한 절차입니다.  
> 각 단계는 반드시 순서대로 진행하고, 명시된 문서/코드를 함께 확인하세요.

---

## 0. 사전 준비
- [ ] `create-next-app --ts`로 새 Next.js(App Router) + TypeScript 프로젝트 생성
- [ ] Tailwind CSS 설치 및 기본 팔레트 제거 (`docs/FRONTEND_TOKENS.md`의 색상을 tailwind.config에 등록)
- [ ] 이 레포의 `frontend/` 디렉터리 구조를 복사하거나 참고해 폴더(`components/`, `stores/`, `theme/`, `app/dashboard/`, `stories/`) 생성
- [ ] 디자인 토큰 적용: `frontend/theme/tokens.ts`
- [ ] FX 상태 관리 연결: `frontend/stores/fxStore.ts`, `frontend/components/FxContext.tsx`, `frontend/components/FxLayer.tsx`
- [ ] Storybook 초기화(`npx storybook@latest init --builder vite`) 후 사용 언어/경로 설정
- [ ] 모킹 도구(MSW 또는 MirageJS) 설치: API 계약 테스트에 사용

## 1. 필독 문서
- [ ] 전체 화면 설계: `docs/FRONTEND_DESIGN.md`
- [ ] 이펙트·모션 가이드: `docs/FRONTEND_FX_GUIDE.md`
- [ ] 디자인 토큰: `docs/FRONTEND_TOKENS.md`
- [ ] API 계약: `docs/FRONTEND_API_CONTRACT.md`
- [ ] QA/자동화 계획: `docs/FRONTEND_QA_PLAN.md`
- [ ] 운영/검증 로드맵: `docs/VALIDATION_PLAN.md`

## 2. 화면 구현 흐름
1. **AppShell / 레이아웃**  
   - 토큰을 Tailwind/스타일 시스템에 매핑  
   - 헤더/사이드바/하단 탭 구성 후 `FxLayer`를 루트에 배치
2. **Dashboard**  
   - 참고: `frontend/app/dashboard/DashboardPage.tsx` (HeroCard, Checklist, QuestCard 샘플)  
   - Stage/콤보/경고 상태를 상태값으로 연결
3. **Chat / Goals / Reports / Settings**  
   - `docs/FRONTEND_DESIGN.md` 각 섹션의 레이아웃·모션 규칙을 적용  
   - FX 트리거는 `triggerFx({ id: ..., priority: FX_PRIORITY[...] })` 형식으로 연결  
   - 모바일 Drawer/Tab 동작도 구현
4. **반응형 점검**  
   - 데스크톱 12컬럼, 태블릿 8, 모바일 4컬럼 그리드로 재배치  
   - Stage 승급 Aura는 모바일에서 Hero 카드에만 적용(헤더 오버플로 방지)

## 3. API 연동 (Mock → 실제)
- [ ] `docs/FRONTEND_API_CONTRACT.md`의 엔드포인트/스키마로 Mock 서버 작성 (MSW 추천)
- [ ] 퀘스트 로그 저장 시 `sanitizeMoodNote`가 작동하는지 확인 (`core/privacy.py` 참고)
- [ ] 알림 테스트(`/reminders/test`) 결과가 챗봇 대화와 리포트에 반영되는지 확인
- [ ] 실제 백엔드와 연결 시 Swagger/DTO가 문서와 일치하는지 검증

## 4. FX & 모션 적용
- [ ] Stage 승급 / 퀘스트 완료 / 에너지 경고 / 보스 재조정 / 전리품 기록 FX 구현
- [ ] Reduced Motion 모드(`prefers-reduced-motion` 또는 설정 토글)에서 `*_reduced` 연출로 대체
- [ ] FX 큐 우선순위/중복 제한 (`frontend/stores/fxStore.ts`) 테스트
- [ ] Professional 테마에서는 라인 애니메이션, 저채도 색상 적용

## 5. Storybook & 시각 회귀
- [ ] Storybook 스토리 작성 (목록: `docs/FRONTEND_QA_PLAN.md` 1장)  
  `HeroCard`, `QuestCard`, `ChecklistItem`, `AppShell`, `BossTimeline`, `ReminderForm`, FX 전용 스토리 등
- [ ] Chromatic(또는 Loki)로 Game/Pro/Reduced Motion 스토리 차이 비교
- [ ] Storybook Controls에 Theme/Reduced Motion 토글 추가

## 6. Playwright & 접근성 테스트
- [ ] Playwright 시나리오 구성 (`docs/FRONTEND_QA_PLAN.md` 2장)  
  대시보드, 챗, 목표, 리포트, 알림, 모바일 뷰포트 포함
- [ ] Mock API를 통해 FX 트리거/로그 확인
- [ ] Lighthouse & axe 검사: 데스크톱/모바일 접근성 ≥ 90

## 7. 배포 전 최종 확인
- [ ] `npm run lint`, `npm run test`, `npm run e2e:ci` 통과
- [ ] Storybook 스냅샷 최신화 및 리뷰 승인
- [ ] Playwright 스크린샷 승인 (경고/Reduced Motion 상태 포함)
- [ ] FX 로그(`fxStore`)가 Stage/경고 이벤트를 기록하는지 확인 (Playwright로 API 호출)
- [ ] 알림 테스트가 챗봇 대화 기록에도 남는지 확인
g- [ ] Release 노트에 주요 FX/테마 변화 기록

## 8. 배포 후 & 운영
- [ ] 사용자 피드백 수집 후 `docs/FRONTEND_FX_GUIDE.md`/`docs/FRONTEND_QA_PLAN.md` 업데이트
- [ ] 디자인 자산(Figma, Lottie, 사운드) 추가 시 경로/버전 문서화
- [ ] `docs/VALIDATION_PLAN.md`에 따라 운영/분석팀과 통합 테스트 진행

---

> 변경이 발생하면 **문서와 코드가 항상 함께 업데이트**되어야 합니다.  
> 실행 중 발견한 이슈는 체크리스트에 주석 또는 TODO로 남겨 다음 작업자가 이어 받을 수 있게 하세요.
