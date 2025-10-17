# LLM Usage & Cost Management Guide

## 1. 작업별 권장 모델
| 작업 | 기본 모델 | 대체 모델 | 비고 |
| --- | --- | --- | --- |
| 실시간 코칭/일일 대화 | gpt-5-mini | gpt-4o-mini | 템플릿(`docs/RESPONSE_TEMPLATES.md`)을 우선 사용하고 부족한 부분만 LLM으로 보완 |
| 주간/월간 전리품 요약, 보고서 문구 | gpt-5-mini | gpt-4o-mini | 보고서 품질 유지, 토큰 회수 기반 검토 |
| 짧은 안내/알림 텍스트 | gpt-4o-mini | gpt-5-mini | 비용 절감을 위해 경량 모델 우선, 템플릿 우선 |
| 대화 요약(Conversation summaries) | gpt-4o-mini | gpt-5-mini | 토큰 길이에 따라 분할 호출 고려 |
| 시뮬레이션/테스트 | 로컬 룰 기반/고정 스텁 | - | 비용 없는 대체 사용 |

## 2. 비용 모니터링
- `app.py`에서 OpenAI 응답의 `usage` 필드를 `logs/llm_usage.log`에 기록
- 로그 포맷 예: `{ "timestamp": "2025-02-15T12:34:56", "model": "gpt-5-mini", "prompt_tokens": 512, "completion_tokens": 256, "total_tokens": 768 }`
- 주간 스크립트로 토큰 합계 및 모델별 비용 집계, 임계치 초과 시 Slack 알림
- 호출당 토큰 한도(예: 3000 tokens) 설정 및 초과 시 경고 로그 남기기

## 3. 최적화 전략
- 응답 템플릿/룰 기반 응답을 충분히 확보하여 LLM 호출 빈도를 축소
- 대화 로그 요약 전 텍스트 길이를 점검하고 필요 시 chunking
- 장기적으로는 캐시된 LLM 결과(예: 보스전 설명) 재사용

## 4. 장애 및 Fallback
- OpenAI 장애/비용 초과 시 `LLM_MODEL_PLAN`의 fallback 모델 사용 또는 `GOALER_USE_MOCK=true`
- 오류 발생 시 usage 로그에 `error` 필드를 추가하여 재시도/디버깅 가능하게 유지
