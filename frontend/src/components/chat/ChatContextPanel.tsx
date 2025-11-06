"use client";

import type { ChatContext } from "../../lib/api/types";
import { colors, typography } from "../../theme/tokens";
import { useThemeVariant } from "../../theme/ThemeProvider";

interface ChatContextPanelProps {
  context: ChatContext;
}

export const ChatContextPanel: React.FC<ChatContextPanelProps> = ({ context }) => {
  const { theme } = useThemeVariant();

  return (
    <aside className="space-y-4 rounded-3xl border border-white/10 bg-white/5 p-4" style={{ minWidth: 280 }}>
      <header>
        <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-secondary)]">현재 보스전</p>
        <h2
          className="mt-2 text-lg font-semibold"
          style={{ fontFamily: typography.heading.fontFamily, color: colors.text.primary[theme] }}
        >
          {context.goalTitle}
        </h2>
        <div className="mt-2 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-xs text-[var(--text-secondary)]">
          <span>{context.stageLabel}</span>
          <span>연속 {context.streakCount}일</span>
        </div>
      </header>
      <section className="space-y-2">
        <p className="text-xs uppercase tracking-[0.2em] text-[var(--text-secondary)]">전리품 하이라이트</p>
        <div className="flex flex-wrap gap-2">
          {context.recentLoot.map((loot) => (
            <span
              key={loot.label}
              className="rounded-full px-3 py-1 text-xs font-semibold"
              style={{
                background:
                  loot.type === "ACHIEVEMENT"
                    ? colors.loot.achievement
                    : loot.type === "INSIGHT"
                    ? colors.loot.insight
                    : colors.loot.emotion,
                color: colors.background.surface[theme],
              }}
            >
              {loot.label}
            </span>
          ))}
        </div>
      </section>
      <section className="space-y-2">
        <p className="text-xs uppercase tracking-[0.2em] text-[var(--text-secondary)]">에너지 상태</p>
        <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
          <span
            className="h-3 w-3 rounded-full"
            style={{
              background:
                context.energyStatus === "READY_FOR_BOSS"
                  ? colors.success[theme]
                  : context.energyStatus === "KEEPING_PACE"
                  ? colors.accent.cyan[theme]
                  : colors.warning[theme],
            }}
          />
          <span>
            {context.energyStatus === "READY_FOR_BOSS"
              ? "보스전에 돌입할 에너지!"
              : context.energyStatus === "KEEPING_PACE"
              ? "안정적인 페이스 유지 중"
              : "회복 루틴이 필요해요"}
          </span>
        </div>
      </section>
    </aside>
  );
};
