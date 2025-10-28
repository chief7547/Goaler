export type EnergyStatus = "READY_FOR_BOSS" | "KEEPING_PACE" | "NEEDS_POTION";

export interface GoalSummary {
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
  } | null;
  themePreference: "GAME" | "PRO";
}

export interface BossStage {
  bossId: string;
  title: string;
  status: "READY" | "IN_PROGRESS" | "COMPLETED" | "ADJUSTMENT_NEEDED";
  targetWeek: number;
  weeklyPlan: Array<{ title: string; week: number }>;
  dailyTasks: Array<QuestSummary>;
}

export interface QuestSummary {
  questId: string;
  title: string;
  difficulty: "EASY" | "NORMAL" | "HARD";
  reason?: string;
}

export interface QuestLog {
  logId: string;
  questId: string;
  goalId: string;
  outcome: "COMPLETED" | "SKIPPED" | "DEFERRED";
  sanitizedMoodNote?: string | null;
  energyStatus: EnergyStatus;
  lootType: "ACHIEVEMENT" | "INSIGHT" | "EMOTION";
  createdAt: string;
}

export interface Reminder {
  reminderId: string;
  goalId: string;
  channel: "slack" | "email";
  frequency: "daily" | "weekly" | "once";
  time: string;
  timezone: string;
  active: boolean;
  lastSentAt: string | null;
}

export interface GoalDetail extends GoalSummary {
  motivation: string;
  bossStages: BossStage[];
  metrics: Array<{
    metricId: string;
    name: string;
    unit: string;
    targetValue: number;
    currentValue: number;
  }>;
  lootLog: Array<{
    logId: string;
    type: "ACHIEVEMENT" | "INSIGHT" | "EMOTION";
    note: string;
    createdAt: string;
  }>;
  reminders: Reminder[];
}

export interface ChatMessage {
  messageId: string;
  role: "user" | "assistant" | "system";
  content: string;
  createdAt: string;
  suggestions?: Array<{ id: string; label: string }>;
}

export interface ChatContext {
  goalTitle: string;
  stageLabel: string;
  energyStatus: EnergyStatus;
  streakCount: number;
  recentLoot: Array<{ type: string; label: string }>;
}

export interface ChatSession {
  messages: ChatMessage[];
  context: ChatContext;
}

export interface ReportSummary {
  period: "weekly" | "monthly";
  highlights: Array<{ id: string; title: string; description: string; fx: "stage_upgrade" | "quest_complete" | "energy_warning" }>;
  metrics: Array<{
    metricId: string;
    name: string;
    unit: string;
    values: Array<{ label: string; value: number }>;
  }>;
  story: Array<{ heading: string; body: string }>;
}

export interface ReminderTestResponse {
  ok: boolean;
  referenceId: string;
}
