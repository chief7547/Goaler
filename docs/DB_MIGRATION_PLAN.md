# Database Migration & PostgreSQL Transition Plan

이 문서는 SQLite 기반 프로토타입에서 PostgreSQL 환경으로 전환하기 위한 단계별 가이드를 제공한다. 또한 데이터 마이그레이션과 스키마 변경 시 Alembic 사용법을 정리한다.

## 1. 준비 단계
1. PostgreSQL 인스턴스 생성 (로컬 Docker 또는 클라우드 서비스)
2. `.env`에 다음 항목을 추가
   ```
   GOALER_DATABASE_URL=postgresql+psycopg2://user:password@host:5432/goaler
   GOALER_AUTO_CREATE_SCHEMA=false
   GOALER_DB_POOL_SIZE=5
   GOALER_DB_MAX_OVERFLOW=10
   ```
3. psycopg2 설치 필요 시 `pip install psycopg2-binary`

## 2. 스키마 배포
1. 최초 배포: `alembic upgrade head`
2. 변경 사항 발생 시:
   ```bash
   alembic revision --autogenerate -m "describe change"
   alembic upgrade head
   ```
3. 생성된 마이그레이션은 PR에 포함하고, 운영/스테이징 DB에서도 동일하게 적용
4. 성능 튜닝(예: QuestLog 외래키 인덱스 추가)도 Alembic으로 관리해, 배포 환경 간 스키마 차이를 방지한다.

## 3. 데이터 마이그레이션 (SQLite → PostgreSQL)
1. 기존 SQLite 덤프 (`sqlite3 data/goaler.db .dump > backup.sql`)
2. 필요 시 수동 변환 또는 ETL 스크립트 작성
3. PostgreSQL에 import 이후 `alembic upgrade head`로 스키마 최신화

## 4. 검증 체크리스트
- `core/storage.create_session_factory`가 PostgreSQL URL로 정상 연결되는지
- APScheduler 워커와 애플리케이션을 동시 실행해 Lock 오류가 발생하지 않는지
- Alembic downgrade/upgrade가 문제 없이 수행되는지

## 5. 운영 중 변경 사항
- 매 스키마 변경 시 Alembic revision 목록에 추가
- 배포 전 `alembic upgrade head`를 CI/CD 파이프라인에 포함
- 데이터 손실 위험이 있는 변경 시 백업 및 롤백 계획 준비 (SOP 참고)

---

> Phase 6에서는 위 절차를 기반으로 PostgreSQL 전환과 Alembic 파이프라인을 정식 도입한다.
