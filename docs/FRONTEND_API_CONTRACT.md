# Frontend API Contract (Draft)

프런트엔드와 백엔드가 합의해야 하는 REST API 계약 초안입니다. 실제 구현 시 스키마 변경이 필요하면 본 문서를 갱신하세요.

## 공통 규칙
- Base URL: `/api/v1`
- 인증: Phase 1은 단일 사용자, Phase 2부터 OAuth Access Token 헤더(`Authorization: Bearer <token>`)
- 날짜/시간: ISO 8601 (UTC), 예: `2025-02-21T09:30:00Z`
- 에러 포맷
```json
{
  "code": "RESOURCE_NOT_FOUND",
  "message": "Goal not found",
  "details": { "goalId": "..." }
}
```

## 엔드포인트 요약
| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/goals` | 목표 목록 (대시보드) |
| GET | `/goals/{goalId}` | 목표 상세 (보스/주간/일일 퀘스트) |
| POST | `/goals` (Phase 2) | 목표 생성 (챗봇 외 경로) |
| GET | `/goals/{goalId}/quests/today` | 오늘 추천 퀘스트 |
| POST | `/quests/{questId}/logs` | 퀘스트 실행 결과 기록 |
| GET | `/reminders` | 알림 설정 조회 |
| POST | `/reminders` | 알림 생성/업데이트 |
| POST | `/reminders/test` | Slack 테스트 메시지 발송 |
| GET | `/reports/{period}` | 리포트 조회 (monthly/weekly) |
| GET | `/chat/context` | 챗봇 초기 컨텍스트 (목표/전리품 상태) |
| POST | `/chat/messages` | 챗봇 대화 요청 (LLM Function Calling) |
| GET | `/stage` | 현재 사용자 Stage/에너지 상태 |

## 1. GET `/goals`
**Query:** `?status=in_progress|completed|all` (default `in_progress`)

**Response:**
```json
[
  {
    "goalId": "g-123",
    "title": "하프 마라톤 완주",
    "stage": "STAGE_1_ENERGY",
    "progress": {
      "completedSteps": 3,
      "totalSteps": 5
    },
    "energyStatus": "KEEPING_PACE",
    "nextAction": {
      "questId": "q-321",
      "title": "15km LSD 달리기",
      "due": "2025-02-22"
    },
    "themePreference": "GAME"
  }
]
```

## 2. GET `/goals/{goalId}`
**Response:**
```json
{
  "goalId": "g-123",
  "title": "하프 마라톤 완주",
  "stage": "STAGE_1_ENERGY",
  "motivation": "건강과 성취감",
  "bossStages": [
    {
      "bossId": "b-1",
      "title": "중간 기록 측정",
      "status": "READY",
      "targetWeek": 6,
      "weeklyPlan": [
        { "title": "페이스 조절 훈련", "week": 5 },
        { "title": "보강 운동", "week": 6 }
      ],
      "dailyTasks": [
        {
          "questId": "q-321",
          "title": "15km LSD 달리기",
          "difficulty": "HARD",
          "reason": "다음 보스전을 위한 체력 확보"
        }
      ]
    }
  ],
  "metrics": [
    {
      "metricId": "m-1",
      "name": "주당 총 달린 거리",
      "unit": "km",
      "targetValue": 40,
      "currentValue": 28
    }
  ],
  "lootLog": [
    {
      "logId": "log-1",
      "type": "ACHIEVEMENT",
      "note": "페이스 조절에 성공!",
      "createdAt": "2025-02-18T09:00:00Z"
    }
  ],
  "reminders": [
    {
      "reminderId": "r-1",
      "channel": "slack",
      "frequency": "daily",
      "time": "07:00",
      "active": true
    }
  ]
}
```

## 3. POST `/quests/{questId}/logs`
**Request:**
```json
{
  "goalId": "g-123",
  "occurredAt": "2025-02-21T09:30:00Z",
  "outcome": "COMPLETED",
  "energyStatus": "READY_FOR_BOSS",
  "lootType": "ACHIEVEMENT",
  "moodNote": "이메일 test@example.com 과 전화 010-1234-5678",
  "perceivedDifficulty": "JUST_RIGHT"
}
```
**Response:**
```json
{
  "logId": "log-999",
  "questId": "q-321",
  "goalId": "g-123",
  "outcome": "COMPLETED",
  "sanitizedMoodNote": "이메일 [민감정보] 과 전화 [민감정보]",
  "energyStatus": "READY_FOR_BOSS",
  "lootType": "ACHIEVEMENT",
  "createdAt": "2025-02-21T09:30:01Z"
}
```

## 4. GET `/reminders`
**Response:**
```json
[
  {
    "reminderId": "r-1",
    "goalId": "g-123",
    "channel": "slack",
    "frequency": "daily",
    "time": "07:00",
    "timezone": "Asia/Seoul",
    "active": true,
    "lastSentAt": "2025-02-19T22:00:00Z"
  }
]
```

## 5. POST `/reminders`
**Request:**
```json
{
  "goalId": "g-123",
  "channel": "slack",
  "frequency": "daily",
  "time": "07:00",
  "timezone": "Asia/Seoul",
  "active": true
}
```
**Response:** `201 Created` + `Location: /reminders/r-1`

## 6. POST `/reminders/test`
**Request:**
```json
{
  "channel": "slack",
  "webhookUrl": "https://hooks.slack.com/services/..."
}
```
**Response:**
```json
{
  "status": "SUCCESS",
  "sentAt": "2025-02-21T00:00:32Z"
}
```

## 7. GET `/reports/{period}`
- `period` = `monthly` | `weekly`
- Query: `?goalId=g-123`

**Response:**
```json
{
  "period": "monthly",
  "start": "2025-02-01T00:00:00Z",
  "end": "2025-02-29T23:59:59Z",
  "heroStory": "이번 달에는 하프 마라톤 준비를 위한 핵심 루틴을 잘 쌓았습니다...",
  "metrics": {
    "loot": {
      "ACHIEVEMENT": 8,
      "INSIGHT": 4,
      "EMOTION": 3
    },
    "questsCompleted": 24,
    "energyStatus": {
      "READY_FOR_BOSS": 6,
      "KEEPING_PACE": 15,
      "NEEDS_POTION": 3
    }
  },
  "nextWeekSuggestions": [
    { "type": "ATTACK", "headline": "이번 주엔 공격 모드로 10km 페이스 업!" },
    { "type": "SUPPORT", "headline": "회복 루틴으로 휴식도 잊지 마세요" }
  ]
}
```

## 8. POST `/chat/messages`
**Request:**
```json
{
  "conversationId": "conv-123",
  "message": "오늘 퀘스트 다 끝냈어",
  "metadata": {
    "theme": "GAME",
    "stage": "STAGE_0_5_LOOT"
  }
}
```
**Response:**
```json
{
  "conversationId": "conv-123",
  "messages": [
    {
      "id": "msg-1",
      "role": "assistant",
      "content": "축하해요! 오늘 퀘스트가 모두 완료되었어요. 전리품 칩을 남겨볼까요?",
      "fx": ["fx_quest_complete"],
      "suggestedActions": [
        { "label": "전리품 남기기", "payload": {"type": "OPEN_LOOT_DIALOG"} },
        { "label": "휴식 루틴", "payload": {"type": "OPEN_POTION"} }
      ]
    }
  ],
  "context": {
    "stage": "STAGE_0_5_LOOT",
    "energyStatus": "READY_FOR_BOSS"
  }
}
```

## 9. GET `/stage`
**Response:**
```json
{
  "stage": "STAGE_1_ENERGY",
  "unlockedFeatures": {
    "loot": true,
    "energy": true,
    "boss": false
  },
  "comboStreak": 3,
  "needsBossAdjustment": false
}
```

---

**TODO / 오픈 이슈**
1. OAuth 도입 시 인증 실패 코드 정의
2. WebSocket 스트리밍을 도입할 경우 `/chat/messages` 응답 구조 확장 필요
3. 보고서 API의 `nextWeekSuggestions`는 추후 LLM 결정 로직과 동기화 필요
