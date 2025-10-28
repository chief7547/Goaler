"use client";

import type { GoalDetail } from "../../lib/api/types";
import { colors, typography } from "../../theme/tokens";
import { useThemeVariant } from "../../theme/ThemeProvider";
import { BossTimeline } from "./BossTimeline";

interface GoalDetailPanelProps {
  detail: GoalDetail;
}

export const GoalDetailPanel: React.FC<GoalDetailPanelProps> = ({ detail }) => {
  const { theme } = useThemeVariant();

  return (
    <div className="space-y-8">
      <section className="rounded-3xl border border-white/10 bg-white/5 p-6">
        <header className="space-y-3">
          <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-secondary)]">목표 개요</p>
          <h1 className="text-2xl font-semibold" style={{ fontFamily: typography.titleMd.fontFamily[theme] }}>
            {detail.title}
          </h1>
          <p className="text-sm text-[var(--text-secondary)]">{detail.motivation}</p>
          <div className="flex flex-wrap gap-2 text-xs text-[var(--text-secondary)]">
            <span className="rounded-full bg-white/10 px-3 py-1">
              Stage {detail.stage.replace("STAGE_", "").replaceAll("_", " ")}
            </span>
            <span className="rounded-full bg-white/10 px-3 py-1">진행률 {detail.progress.completedSteps}/{detail.progress.totalSteps}</span>
          </div>
        </header>
      </section>

      <section className="space-y-4">
        <header className="flex items-center justify-between">
          <h2 className="text-lg font-semibold" style={{ fontFamily: typography.heading.fontFamily }}>
            보스 타임라인
          </h2>
          <span className="text-xs text-[var(--text-secondary)]">다음 보스 목표 주차: {detail.bossStages[0]?.targetWeek ?? "-"}주차</span>
        </header>
        <BossTimeline stages={detail.bossStages} />
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="space-y-3 rounded-3xl border border-white/10 bg-white/5 p-4">
          <h3 className="text-lg font-semibold" style={{ fontFamily: typography.heading.fontFamily }}>
            핵심 지표
          </h3>
          <ul className="space-y-2 text-sm text-[var(--text-secondary)]">
            {detail.metrics.map((metric) => {
              const progressRatio = Math.min(1, metric.currentValue / metric.targetValue);
              return (
                <li key={metric.metricId} className="rounded-xl bg-black/20 p-3">
                  <div className="flex items-center justify-between">
                    <span>{metric.name}</span>
                    <span>
                      {metric.currentValue}/{metric.targetValue} {metric.unit}
                    </span>
                  </div>
                  <div className="mt-2 h-2 rounded-full bg-black/40">
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${progressRatio * 100}%`, background: colors.primary[theme] }}
                    />
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
        <div className="space-y-3 rounded-3xl border border-white/10 bg-white/5 p-4">
          <h3 className="text-lg font-semibold" style={{ fontFamily: typography.heading.fontFamily }}>
            전리품 로그
          </h3>
          <ul className="space-y-2 text-sm text-[var(--text-secondary)]">
            {detail.lootLog.map((loot) => (
              <li key={loot.logId} className="rounded-xl bg-black/20 p-3">
                <div className="flex items-center justify-between">
                  <span>{loot.note}</span>
                  <span>{new Date(loot.createdAt).toLocaleDateString("ko-KR")}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  );
};
