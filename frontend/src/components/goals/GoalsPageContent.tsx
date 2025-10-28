"use client";

import { useMemo, useState } from "react";
import { useGoalsOverview, useGoalDetail } from "../../hooks/useGoalsData";
import { GoalDetailPanel } from "./GoalDetailPanel";

export const GoalsPageContent: React.FC = () => {
  const { data: goals, isLoading, error } = useGoalsOverview();
  const [selectedGoalId, setSelectedGoalId] = useState<string | null>(null);
  const activeGoalId = selectedGoalId ?? goals?.[0]?.goalId ?? null;

  const goalDetailQuery = useGoalDetail(activeGoalId);

  const sidebarGoals = useMemo(() => goals ?? [], [goals]);

  if (isLoading) {
    return <p className="text-sm text-[var(--text-secondary)]">목표 데이터를 불러오는 중입니다…</p>;
  }

  if (error) {
    return <p className="text-sm text-red-300">목표 데이터를 불러오지 못했습니다.</p>;
  }

  if (!goals || goals.length === 0) {
    return <p className="text-sm text-[var(--text-secondary)]">등록된 목표가 없습니다. 챗에서 목표를 생성해 주세요.</p>;
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(220px,_1fr)_minmax(0,_3fr)]">
      <aside className="space-y-3 rounded-3xl border border-white/10 bg-white/5 p-4">
        <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-secondary)]">목표 목록</p>
        <ul className="space-y-2 text-sm">
          {sidebarGoals.map((goal) => {
            const isActive = goal.goalId === activeGoalId;
            return (
              <li key={goal.goalId}>
                <button
                  type="button"
                  className="w-full rounded-2xl px-4 py-3 text-left transition"
                  style={{
                    background: isActive ? "rgba(255,255,255,0.1)" : "transparent",
                    border: isActive ? "1px solid rgba(255,255,255,0.2)" : "1px solid transparent",
                  }}
                  onClick={() => setSelectedGoalId(goal.goalId)}
                >
                  <p className="font-semibold" style={{ margin: 0 }}>
                    {goal.title}
                  </p>
                  <p className="mt-1 text-xs text-[var(--text-secondary)]">
                    Stage {goal.stage.replace("STAGE_", "")} · 진행률 {goal.progress.completedSteps}/{goal.progress.totalSteps}
                  </p>
                </button>
              </li>
            );
          })}
        </ul>
      </aside>

      <section>
        {goalDetailQuery.isLoading && (
          <p className="text-sm text-[var(--text-secondary)]">선택한 목표를 불러오는 중입니다…</p>
        )}
        {goalDetailQuery.error && (
          <p className="text-sm text-red-300">목표 상세 데이터를 불러오지 못했습니다.</p>
        )}
        {goalDetailQuery.data && <GoalDetailPanel detail={goalDetailQuery.data} />}
      </section>
    </div>
  );
};
