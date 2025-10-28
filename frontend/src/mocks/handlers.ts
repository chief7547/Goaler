import { http, HttpResponse } from "msw";

type EnergyStatus = "READY_FOR_BOSS" | "KEEPING_PACE" | "NEEDS_POTION";

type GoalSummary = {
  goalId: string;
  title: string;
  stage: string;
  progress: {
    completedSteps: number;
    totalSteps: number;
  };
  energyStatus: EnergyStatus;
  nextAction: {
    questId: string;
    title: string;
    due: string;
  };
  themePreference: "GAME" | "PRO";
};

type Reminder = {
  reminderId: string;
  goalId: string;
  channel: "slack" | "email";
  frequency: string;
  time: string;
  timezone: string;
  active: boolean;
  lastSentAt: string | null;
};

const goals: GoalSummary[] = [
  {
    goalId: "g-123",
    title: "하프 마라톤 완주",
    stage: "STAGE_1_ENERGY",
    progress: {
      completedSteps: 3,
      totalSteps: 5,
    },
    energyStatus: "KEEPING_PACE",
    nextAction: {
      questId: "q-321",
      title: "15km LSD 달리기",
      due: "2025-02-22",
    },
    themePreference: "GAME",
  },
];

const reminders: Reminder[] = [
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
];

type QuestLogPayload = {
  goalId: string;
  outcome: string;
  moodNote?: string | null;
  energyStatus: EnergyStatus;
  lootType: string;
};

export const handlers = [
  http.get("/api/v1/goals", () => HttpResponse.json(goals)),
  http.get("/api/v1/goals/:goalId", ({ params }) => {
    const match = goals.find((goal) => goal.goalId === params.goalId);
    if (!match) {
      return HttpResponse.json(
        { code: "RESOURCE_NOT_FOUND", message: "Goal not found" },
        { status: 404 }
      );
    }
    return HttpResponse.json({
      ...match,
      bossStages: [],
      metrics: [],
      lootLog: [],
      reminders,
    });
  }),
  http.get("/api/v1/reminders", () => HttpResponse.json(reminders)),
  http.post("/api/v1/reminders/test", async () => {
    return HttpResponse.json({ ok: true, referenceId: "rem-test-1" });
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
];
