# Validation Plan After Frontend Integration

본 문서는 CLI 프로토타입(P5)을 마친 뒤, 실제 사용자 경험을 검증하기 위해 프론트엔드와 운영팀이 합류했을 때 수행할 Validation 로드맵을 정리한다.

## 1. 준비 단계
- **팀 구성**: 프론트엔드/디자이너, QA, 운영 담당자 지정
- **인프라**: PostgreSQL 전환, Alembic 마이그레이션 파이프라인 구축, Redis(또는 유사 인프라)로 토큰 및 요청량 캐싱
- **문서 숙지**: `docs/DEVELOPMENT_PLAYBOOK.md` Phase 6, `docs/OPERATIONS_SOP.md`, `docs/ALERT_TEMPLATES.md`

## 2. Validation 체크리스트
1. **프론트엔드 통합 테스트**
   - 목표 생성 → 보스/변주 → 전리품 기록 → 리포트 확인까지 전 UX 플로우
   - Stage 해금 UI/툴 동작 점검 (Stage 0~2)
   - `docs/FRONTEND_FX_GUIDE.md`에 정의된 주요 FX(Stage 승급, 퀘스트 완료, 에너지 경고, 보스 재조정)가 테마/Reduced Motion 모드에서 모두 정상 동작하는지 확인
   - Storybook 스냅샷 비교(GAME/PRO, Reduced Motion)로 시각적 회귀 테스트 실행
2. **실시간 운영 시뮬레이션**
   - APScheduler 워커와 웹/CLI 동시 사용 시 DB 락, 로그, 알림 상태 확인
   - Slack/Email 알림 발송, 재시도/에러 핸들링 확인
3. **LLM 비용 및 레이트리밋**
   - 사용자·세션별 토큰 사용량 임계치 설정 및 초과 시 차단 로직 테스트
   - 관리자 알림(슬랙/메일) 확인
4. **알림/리포트 UX 검증**
   - 사용자별 리포트 콘텐츠 품질, 성장 서사 톤 재검토
   - 알림 내용이 의도한 UX와 일치하는지, 과도한 노이즈가 없는지 점검
5. **보안/백업 리허설**
   - PostgreSQL 백업 및 복원 시뮬레이션
   - 비상 시나리오(LLM 장애, 워커 실패) 대응 리허설

## 3. 결과 정리 및 승인
- Validation 결과는 `reports/validation/` 디렉터리에 기록 (테스트 로그, 발견된 이슈, 해결 내역)
- Go/No-Go 회의 후 `docs/DEVELOPMENT_PLAYBOOK.md` Hand-off 체크리스트 업데이트

---

> 이 문서는 프론트엔드와 운영팀이 합류했을 때 업데이트되어야 하며, Validation 완료 후에는 운영 매뉴얼(SOP)과 분석 계획에 반영한다.
