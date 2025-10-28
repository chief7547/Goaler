import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api/client";
import type { GoalSummary, GoalDetail } from "../lib/api/types";

export const goalsKeys = {
  all: ["goals"] as const,
  detail: (goalId: string | null) => ["goals", goalId] as const,
};

export function useGoalsOverview() {
  return useQuery<GoalSummary[]>({
    queryKey: goalsKeys.all,
    queryFn: api.listGoals,
  });
}

export function useGoalDetail(goalId: string | null) {
  return useQuery<GoalDetail>({
    queryKey: goalsKeys.detail(goalId ?? "unknown"),
    queryFn: () => {
      if (!goalId) {
        throw new Error("goalId is required");
      }
      return api.getGoalDetail(goalId);
    },
    enabled: Boolean(goalId),
  });
}
