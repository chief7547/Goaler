import {
  type GoalSummary,
  type GoalDetail,
  type ChatSession,
  type ReportSummary,
  type Reminder,
  type ReminderTestResponse,
} from "./types";

const BASE_URL = "/api/v1";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    ...init,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody?.message ?? `API error (${response.status})`);
  }

  return (await response.json()) as T;
}

export const api = {
  listGoals: () => apiFetch<GoalSummary[]>(`/goals`),
  getGoalDetail: (goalId: string) => apiFetch<GoalDetail>(`/goals/${goalId}`),
  getChatSession: () => apiFetch<ChatSession>(`/chat/context`),
  sendChatMessage: (content: string) =>
    apiFetch<ChatSession>(`/chat/messages`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),
  getReports: (period: "weekly" | "monthly") => apiFetch<ReportSummary>(`/reports/${period}`),
  listReminders: () => apiFetch<Reminder[]>(`/reminders`),
  updateReminder: (payload: Reminder) =>
    apiFetch<Reminder>(`/reminders`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  sendReminderTest: () =>
    apiFetch<ReminderTestResponse>(`/reminders/test`, {
      method: "POST",
    }),
};
