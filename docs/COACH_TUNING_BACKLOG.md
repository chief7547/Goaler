# Coach Persona Tuning Backlog

Phase 3 구현 이후 추가로 다듬어야 할 페르소나/톤 관련 TODO입니다.

1. **시간대 정밀도 향상**
   - 사용자의 현지 타임존 정보를 user_preferences에 저장하고, `compose_coach_reply`에서 이를 반영해 아침/점심/저녁 분류를 보다 정확히 결정합니다.
2. **감정 신호 세분화**
   - 전리품 `mood_note`에 감정 키워드를 추출해 ToneContext에 `mood_label`을 추가하고, CoachResponder가 공감 메시지를 한 구절 이상 포함하도록 확장합니다.
3. **템플릿 다양성 추가**
   - `docs/RESPONSE_TEMPLATES.md`에 Stage별·보스전 상황별 추가 문구를 작성하고, CoachResponder가 최근 사용 템플릿을 캐싱하여 반복을 줄이는 로직을 구현합니다.
4. **LLM 보조 응답 로깅**
   - 하이브리드 fallback으로 LLM을 호출했을 때 토큰·비용을 `logs/llm_usage.log`에 기록해 모니터링하고, 템플릿 보완 필요성을 판단할 수 있도록 합니다.
