# Storage 인터페이스 설계

이 문서는 `core/storage.py`가 제공해야 하는 메서드와 데이터 계약을 정의합니다. ORM 구현 여부와 상관없이, 아래 시그니처와 동작을 유지해야 합니다.

## 1. 기본 구조
```python
class Storage:
    def __init__(self, session_factory):
        self._Session = session_factory

    def create_goal(self, payload: GoalCreate) -> Goal: ...
    def add_metric(self, goal_id: str, payload: MetricCreate) -> Metric: ...
    def update_motivation(self, goal_id: str, motivation: str) -> Goal: ...
    def finalize_goal(self, goal_id: str) -> Goal: ...

    def create_boss_stage(self, goal_id: str, payload: BossStageCreate) -> BossStage: ...
    def list_boss_stages(self, goal_id: str) -> list[BossStage]: ...
    def update_boss_stage_status(self, boss_id: str, status: str) -> BossStage: ...

    def get_user_preferences(self, user_id: str) -> UserPreferences | None: ...
    def save_user_preferences(self, payload: UserPreferencesUpsert) -> UserPreferences: ...

    def get_player_progress(self, user_id: str) -> PlayerProgress | None: ...
    def update_player_progress(self, user_id: str, payload: PlayerProgressUpdate) -> PlayerProgress: ...

    def create_quest(self, goal_id: str, payload: QuestCreate) -> Quest: ...
    def list_recent_quest_logs(self, goal_id: str, limit: int = 10) -> list[QuestLog]: ...
    def log_quest_event(self, payload: QuestLogCreate) -> QuestLog: ...

    def log_conversation(self, payload: ConversationLogCreate) -> ConversationLog: ...
    def create_conversation_summary(self, payload: ConversationSummaryCreate) -> ConversationSummary: ...

    def create_reminder(self, payload: ReminderCreate) -> Reminder: ...
    def list_reminders_due(self, now_ts: datetime) -> list[Reminder]: ...
```

## 2. 데이터 클래스 (요약)
- `GoalCreate`: `title`, `goal_type`, `deadline`, `user_id`, `conversation_id`
- `MetricCreate`: `metric_name`, `metric_type`, `target_value`, `unit`, `initial_value`
- `QuestCreate`: `title`, `description`, `difficulty_tier`, `expected_duration_minutes`, `variation_tags`, `is_custom`, `origin_prompt_hash`
- `QuestLogCreate`: `quest_id`, `goal_id`, `user_id`, `outcome`, `perceived_difficulty`, `mood_note`, `llm_variation_seed`
- `BossStageCreate`: `title`, `description`, `success_criteria`, `stage_order`, `target_week`
- `UserPreferencesUpsert`: `user_id`, `personality_type`, `challenge_appetite`, `preferred_playstyle`, `calm_time_window`, `disliked_patterns`
- `PlayerProgressUpdate`: `focus_goal_id`, `stage_label`, `level`, `experience_points`, `streak_weeks`, `last_reflection_at`
- 각 반환 객체는 `DATA_SCHEMA.yaml` 필드명과 동일한 구조를 가진 데이터 클래스로 표현합니다.

## 3. 예외 정책
- 존재하지 않는 엔티티에 접근 시
  - `GoalNotFoundError`
  - `QuestNotFoundError`
  - `UserNotFoundError`
- 중복 저장/일관성 위반 시
  - `StorageConflictError`
- 데이터 검증 실패 시
  - `StorageValidationError`

## 4. 트랜잭션
- 각 메서드는 자체적으로 트랜잭션을 시작/커밋합니다.
- 필요 시 `session_scope()` 컨텍스트 매니저를 제공해 배치 작업에서 묶어서 처리할 수 있게 합니다.

```python
@contextmanager
def session_scope(self):
    session = self._Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

## 5. 테스트 요구사항
- 단위 테스트는 `sqlite:///:memory:` 엔진으로 구동합니다.
- 최소 검증 시나리오
  1. 목표 생성 → 메트릭 추가 → 동기 업데이트 → 최종 저장
  2. 변주 퀘스트 생성 → 선택 → 수행 결과 기록 → 플레이어 진척 업데이트
  3. 사용자 성향 저장/조회, 알림 등록/조회
- 에러 시 별도 예외가 발생하고, 메시지에 식별자를 포함해야 합니다.
