import { http, HttpResponse } from "msw";
import type {
  ChatSession,
  GoalDetail,
  GoalSummary,
  Reminder,
  ReportSummary,
} from "../lib/api/types";

type EnergyStatus = "READY_FOR_BOSS" | "KEEPING_PACE" | "NEEDS_POTION";

type QuestLogPayload = {
  goalId: string;
  outcome: string;
  moodNote?: string | null;
  energyStatus: EnergyStatus;
  lootType: string;
};

type ReminderUpsertPayload = Reminder;

type ChatMessagePayload = {
  content: string;
};

const goals: GoalSummary[] = [
  {
    goalId: "g-123",
    title: "하프 마라톤 완주",
    stage: "STAGE_1_ENERGY",
    progress: { completedSteps: 3, totalSteps: 5 },
    energyStatus: "KEEPING_PACE",
    nextAction: {
      questId: "q-321",
      title: "15km LSD 달리기",
      due: "2025-02-22",
    },
    themePreference: "GAME",
  },
];

const goalDetails: Record<string, GoalDetail> = {
  "g-123": {
    ...goals[0],
    motivation: "건강과 성취감을 동시에 얻기 위해",
    bossStages: [
      {
        bossId: "b-1",
        title: "체력 기반 다지기",
        status: "IN_PROGRESS",
        targetWeek: 6,
        weeklyPlan: [
          { title: "지구력 주간 루틴", week: 3 },
          { title: "페이스 조절 훈련", week: 4 },
        ],
        dailyTasks: [
          { questId: "quest-1", title: "15km LSD 달리기", difficulty: "HARD", reason: "보스전 대비" },
          { questId: "quest-2", title: "저강도 회복 러닝", difficulty: "EASY", reason: "근육 회복" },
        ],
      },
      {
        bossId: "b-2",
        title: "레이스 시뮬레이션",
        status: "READY",
        targetWeek: 10,
        weeklyPlan: [{ title: "하프 마라톤 페이스 점검", week: 9 }],
        dailyTasks: [],
      },
    ],
    metrics: [
      {
        metricId: "distance_week",
        name: "주간 총 거리",
        unit: "km",
        targetValue: 45,
        currentValue: 41,
      },
      {
        metricId: "long_run_pace",
        name: "LSD 평균 페이스",
        unit: "분/km",
        targetValue: 5.4,
        currentValue: 5.6,
      },
    ],
    lootLog: [
      {
        logId: "loot-1",
        type: "ACHIEVEMENT",
        note: "콤보 5일 달성",
        createdAt: new Date(Date.now() - 86400000).toISOString(),
      },
      {
        logId: "loot-2",
        type: "INSIGHT",
        note: "새벽 러닝이 컨디션 유지에 도움",
        createdAt: new Date().toISOString(),
      },
    ],
    reminders: [
      {
        reminderId: "r-1",
        goalId: "g-123",
        channel: "slack",
        frequency: "daily",
        time: "07:00",
        timezone: "Asia/Seoul",
        active: true,
        lastSentAt: "2025-02-19T22:00:00Z",
      },
    ],
  },
};

const reminders: Reminder[] = [...goalDetails["g-123"].reminders];

const chatSession: ChatSession = {
  context: {
    goalTitle: goals[0].title,
    stageLabel: "Stage 1 · Energy",
    energyStatus: goals[0].energyStatus,
    streakCount: 5,
    recentLoot: [
      { type: "ACHIEVEMENT", label: "주간 거리 40km 달성" },
      { type: "INSIGHT", label: "페이스 조절 성공" },
    ],
  },
  messages: [
    {
      messageId: "m-1",
      role: "assistant",
      content: "어제 전리품을 기록했어요. 오늘은 어떤 퀘스트가 끌리나요?",
      createdAt: new Date(Date.now() - 3600000).toISOString(),
      suggestions: [
        { id: "suggest-recovery", label: "회복 러닝 준비" },
        { id: "suggest-potion", label: "포션 루틴 기록" },
      ],
    },
    {
      messageId: "m-2",
      role: "user",
      content: "어제 15km 런을 마쳤고, 오늘은 회복 위주로 가고 싶어요.",
      createdAt: new Date(Date.now() - 1800000).toISOString(),
    },
  ],
};

const reportByPeriod: Record<"weekly" | "monthly", ReportSummary> = {
  weekly: {
    period: "weekly",
    highlights: [
      {
        id: "highlight-1",
        title: "Stage 1 에너지 안정화",
        description: "연속 5일 루틴을 지켜 콤보 보너스를 획득했습니다.",
        fx: "stage_upgrade",
      },
      {
        id: "highlight-2",
        title: "퀘스트 달성률 80%",
        description: "체력 보강 퀘스트 4개 중 3개 성공",
        fx: "quest_complete",
      },
    ],
    metrics: [
      {
        metricId: "distance",
        name: "주간 총 달린 거리",
        unit: "km",
        values: [
          { label: "Week 1", value: 32 },
          { label: "Week 2", value: 38 },
          { label: "Week 3", value: 41 },
        ],
      },
    ],
    story: [
      {
        heading: "몰입",
        body: "회복 루틴을 지켜 에너지 경고 없이 주간 루프를 마쳤습니다.",
      },
      {
        heading: "다음 단계",
        body: "보스 타임라인 2단계 진입 전 페이스 조절 훈련을 강화하세요.",
      },
    ],
  },
  monthly: {
    period: "monthly",
    highlights: [
      {
        id: "highlight-month-1",
        title: "Stage 1 달성",
        description: "첫 달 목표인 에너지 안정화에 성공했습니다.",
        fx: "stage_upgrade",
      },
    ],
    metrics: [
      {
        metricId: "distance",
        name: "월간 누적 거리",
        unit: "km",
        values: [
          { label: "Week 1", value: 32 },
          { label: "Week 2", value: 38 },
          { label: "Week 3", value: 41 },
          { label: "Week 4", value: 44 },
        ],
      },
    ],
    story: [
      {
        heading: "승급",
        body: "Stage 0.5에서 Stage 1로 성장했습니다. 전리품 기록을 계속 축적해보세요.",
      },
    ],
  },
};

export const handlers = [
  http.get("/api/v1/goals", () => HttpResponse.json(goals)),
  http.get("/api/v1/goals/:goalId", ({ params }) => {
    const detail = goalDetails[String(params.goalId)];
    if (!detail) {
      return HttpResponse.json(
        { code: "RESOURCE_NOT_FOUND", message: "Goal not found" },
        { status: 404 }
      );
    }
    return HttpResponse.json(detail);
  }),
  http.get("/api/v1/reminders", () => HttpResponse.json(reminders)),
  http.post("/api/v1/reminders/test", () =>
    HttpResponse.json({ ok: true, referenceId: `rem-test-${Date.now()}` })
  ),
  http.post("/api/v1/reminders", async ({ request }) => {
    const body = (await request.json()) as ReminderUpsertPayload;
    const index = reminders.findIndex((reminder) => reminder.reminderId === body.reminderId);
    if (index >= 0) {
      reminders[index] = body;
    } else {
      reminders.push(body);
    }
    return HttpResponse.json(body);
  }),
  http.get("/api/v1/chat/context", () => HttpResponse.json(chatSession)),
  http.post("/api/v1/chat/messages", async ({ request }) => {
    const body = (await request.json()) as ChatMessagePayload;
    const now = new Date();
    chatSession.messages.push({
      messageId: `user-${now.getTime()}`,
      role: "user",
      content: body.content,
      createdAt: now.toISOString(),
    });
    chatSession.messages.push({
      messageId: `coach-${now.getTime()}`,
      role: "assistant",
      content: "기록해둘게요! 회복 러닝 후 컨디션을 챗에 남겨주세요.",
      createdAt: new Date(now.getTime() + 1000).toISOString(),
      suggestions: [
        { id: "suggest-checklist", label: "체크리스트 업데이트" },
        { id: "suggest-loot", label: "전리품 기록" },
      ],
    });
    return HttpResponse.json(chatSession);
  }),
  http.post("/api/v1/quests/:questId/logs", async ({ request, params }) => {
    const body = (await request.json()) as QuestLogPayload;
    const timestamp = new Date().toISOString();
    return HttpResponse.json({
      logId: `log-${timestamp}`,
      questId: params.questId,
      goalId: body.goalId,
      outcome: body.outcome,
      sanitizedMoodNote: body.moodNote
        ? String(body.moodNote).replace(/([0-9]{3,4}-?[0-9]{4})/g, "[민감정보]")
        : null,
      energyStatus: body.energyStatus,
      lootType: body.lootType,
      createdAt: timestamp,
    });
  }),
  http.get("/api/v1/reports/:period", ({ params }) => {
    const period = String(params.period) as "weekly" | "monthly";
    const report = reportByPeriod[period];
    if (!report) {
      return HttpResponse.json({ code: "RESOURCE_NOT_FOUND", message: "Report not found" }, { status: 404 });
    }
    return HttpResponse.json(report);
  }),
];
