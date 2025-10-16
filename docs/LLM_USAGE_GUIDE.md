# LLM Usage & Cost Management Guide

## 1. Task별 권장 모델
| Task | Primary Model | Fallback Model | 비고 |
| --- | --- | --- | --- |
|Realtime Goal Coaching / Daily Conversation| gpt-5-mini | gpt-4o-mini | 낮은 지연과 우수한 reasoning이 필요. 기본 모델.|
|주간/월간 전리품 요약, 보고서 문구 생성| gpt-5-mini | gpt-4o-mini | 보고서 품질을 위해 mini 계열 유지.|
|짧은 챗봇 응답 후속(간단 안내, 알림 텍스트)| gpt-4o-mini | gpt-5-mini | 비용 절감을 위해 경량 모델 우선.|
|데이터 요약(ConversationSummaries)| gpt-4o-mini | gpt-5-mini | 토큰 수가 많을 수 있어 저렴한 모델 우선.|
|시뮬레이션/테스트용 Mock 응답| 로컬 룰 기반 / 고정 스텁 | - | 비용 없는 대체 사용.|

> 모델 계획은 `DEFAULT_CHAT_MODEL`, `LLM_MODEL_PLAN` (app.py)에서 참고합니다.

## 2. 비용 모니터링 전략
- `app.py`에서 OpenAI 응답의 `usage` 필드를 추출해 `logs/llm_usage.log`에 기록합니다.
- 로그 포맷 예시
  ```json
  {"timestamp": "2025-02-15T12:34:56", "model": "gpt-5-mini", "prompt_tokens": 512, "completion_tokens": 256, "total_tokens": 768}
  ```
- 주간 배치 작업에서 로그를 집계해 모델별 토큰 총량과 예상 비용(토큰당 단가 입력)을 계산합니다.
- 1회 호출당 토큰 한도를 설정(예: 3k tokens)하고 초과 시 경고 로그를 남깁니다.

## 3. 최적화 아이디어
- 대화 요약이나 보고서 생성 전, 토큰 길이를 미리 계산하여 필요 시 chunking.
- 정적 안내문/자주 쓰는 메시지는 프롬프트 대신 템플릿 캐시를 사용해 LLM 호출을 줄입니다.
- 장기 보존을 위해 월별 토큰 총량을 Analytics 파이프라인(`docs/ANALYTICS_PLAN.md`)에 추가.

## 4. 장애 대비
- OpenAI API 장애 또는 비용 초과 시, `LLM_MODEL_PLAN`의 fallback을 사용하거나 `GOALER_USE_MOCK=true`로 mock 모드를 전환.
- 에러 발생 시에도 로그에 “error” 필드를 남겨 재시도/분석이 가능하도록 합니다.
