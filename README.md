# README

프로젝트 초기화:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python tools/preflight.py --entry VIBECODE_ENTRY.md --init-lock-if-missing --check-secrets
```

개요:
- 이 리포지토리는 Vibecoding 대화형 부트스트랩을 위한 샘플 앱입니다.
- 모든 초기 파일은 `VIBECODE_ENTRY.md`만으로 생성됩니다.
- 생성된 CLI는 한국어 인터뷰(clarifier)를 통해 필수 항목을 채우도록 강제합니다.
