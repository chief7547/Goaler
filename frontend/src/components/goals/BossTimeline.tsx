"use client";

import { useThemeVariant } from "../../theme/ThemeProvider";
import { colors, typography } from "../../theme/tokens";
import type { BossStage } from "../../lib/api/types";

interface BossTimelineProps {
  stages: BossStage[];
}

const statusLabel: Record<BossStage["status"], string> = {
  READY: "대기 중",
  IN_PROGRESS: "진행 중",
  COMPLETED: "완료",
  ADJUSTMENT_NEEDED: "조정 필요",
};

export const BossTimeline: React.FC<BossTimelineProps> = ({ stages }) => {
  const { theme } = useThemeVariant();

  return (
    <div className="space-y-4">
      {stages.map((stage, index) => {
        const accentColor =
          stage.status === "COMPLETED"
            ? colors.success[theme]
            : stage.status === "ADJUSTMENT_NEEDED"
            ? colors.warning[theme]
            : colors.accent.cyan[theme];
        return (
          <div
            key={stage.bossId}
            className="rounded-3xl border border-white/10 bg-white/5 p-4"
            style={{ position: "relative", paddingLeft: 24 }}
          >
            <span
              className="absolute left-3 top-6 h-3 w-3 rounded-full"
              style={{ background: accentColor }}
            />
            <div className="ml-6">
              <div className="flex items-center justify-between gap-4">
                <h3
                  className="text-lg font-semibold"
                  style={{ fontFamily: typography.heading.fontFamily }}
                >
                  {index + 1}. {stage.title}
                </h3>
                <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-[var(--text-secondary)]">
                  {statusLabel[stage.status]}
                </span>
              </div>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">
                목표 주차: {stage.targetWeek}주차 · 일일 퀘스트 {stage.dailyTasks.length}개
              </p>
              <div className="mt-3 space-y-2 text-sm text-[var(--text-secondary)]">
                {stage.weeklyPlan.map((plan) => (
                  <div key={`${stage.bossId}-${plan.week}`} className="rounded-xl bg-black/20 px-3 py-2">
                    Week {plan.week}: {plan.title}
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
