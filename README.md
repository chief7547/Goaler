# Goaler

GPT 기반 목표 코칭 챗봇을 구현한 레포지토리입니다. `VIBECODE_ENTRY.md` 하나로 프로젝트 뼈대를 생성하고, 그 위에 대화형 목표 설정 로직과 테스트를 쌓아 올렸습니다.

## 빠른 시작

```bash
python -m venv .venv
source .venv/bin/activate  # Windows는 .venv\Scripts\activate
pip install -r requirements.txt
python tools/preflight.py --entry VIBECODE_ENTRY.md --init-lock-if-missing --check-secrets
```

### 실행 모드
- 기본(mock) 모드: 외부 호출 없이 흐름을 체험합니다.
  ```bash
python app.py
  ```

- 실전(OpenAI) 모드: 실제 GPT 모델과 대화합니다. `.env`에 `OPENAI_API_KEY`가 있어야 하며, mock 모드를 끄면 됩니다.
  ```bash
GOALER_USE_MOCK=false python app.py
  ```

## 주요 구성 요소
- `app.py`: 챗봇 진입점. mock/실전 모드를 자동 전환하고, LLM이 내린 함수 호출을 `GoalSettingAgent`에 위임합니다.
- `core/agent.py`: 목표 생성, 메트릭 추가, 동기 기록, 마무리까지 담당하는 비즈니스 로직.
- `core/state_manager.py`: 대화 중간 상태를 메모리에 저장했다가 종료 시 정리합니다.
- `tests/test_core.py`, `tests/test_e2e_conversation.py`: 단위 테스트와 통합 테스트로 로직이 예상대로 움직이는지 검증합니다.

## 테스트
```bash
PYTHONPATH=. pytest
```

## 추후 진행 방향
- UI·알림 채널 연동: 현재는 CLI 기반이므로, 웹/모바일 UI나 메시징 봇으로 확장할 수 있습니다.
- 지속 저장소: 목표 결과를 파일/DB에 영구 저장해 재접속 시 이어서 진행하도록 만듭니다.
- 추가 메트릭 템플릿: 식단, 수면 등 자주 쓰는 목표 유형을 템플릿화하면 챗봇 안내가 더 부드러워집니다.
