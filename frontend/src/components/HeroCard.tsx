"use client";

import clsx from "clsx";
import { colors, typography, shadow, glow } from "../theme/tokens";
import { triggerFx } from "./FxContext";
import { FX_PRIORITY } from "../stores/fxStore";
import type { ThemeVariant } from "../theme/themeUtils";
import { useThemeVariant } from "../theme/ThemeProvider";
export type EnergyStatus = "READY_FOR_BOSS" | "KEEPING_PACE" | "NEEDS_POTION";

interface HeroCardProps {
  theme?: ThemeVariant;
  stageLabel: string;
  goalTitle: string;
  progress: { completed: number; total: number };
  energyStatus: EnergyStatus;
  nextActionLabel: string;
  onActionClick?: () => void;
}

export const HeroCard: React.FC<HeroCardProps> = ({
  theme,
  stageLabel,
  goalTitle,
  progress,
  energyStatus,
  nextActionLabel,
  onActionClick,
}) => {
  const { theme: currentTheme } = useThemeVariant();
  const resolvedTheme = theme ?? currentTheme;
  const progressPercent = Math.min(100, Math.round((progress.completed / Math.max(1, progress.total)) * 100));
  const isWarning = energyStatus === "NEEDS_POTION";

  const background = colors.background.card[resolvedTheme];

  const textPrimary = colors.text.primary[resolvedTheme];

  const surface = colors.background.surface[resolvedTheme];

  const accent = colors.primary[resolvedTheme];

  const warningColor = colors.warning[resolvedTheme];

  return (
    <div
      className="hero-card"
      style={{
        background,
        color: textPrimary,
        padding: 24,
        borderRadius: 24,
        boxShadow: resolvedTheme === "game" ? shadow.card.game : shadow.card.pro,
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div className="hero-card__stage" style={{ marginBottom: 16 }}>
        <span
          style={{
            display: "inline-block",
            padding: "6px 12px",
            borderRadius: 999,
            backgroundColor: accent,
            color: surface,
            fontFamily: typography.caption.fontFamily,
            fontWeight: 600,
            letterSpacing: 0.4,
          }}
        >
          {stageLabel}
        </span>
      </div>
      <h1
        style={{
          fontFamily: typography.titleLg.fontFamily[resolvedTheme],
          fontSize: typography.titleLg.fontSize,
          lineHeight: typography.titleLg.lineHeight,
          margin: 0,
        }}
      >
        {goalTitle}
      </h1>
      <div style={{ marginTop: 16 }}>
        <div style={{ fontSize: typography.body.fontSize, opacity: 0.72 }}>진행률</div>
        <div
          style={{
            marginTop: 8,
            height: 12,
            background: "rgba(255,255,255,0.12)",
            borderRadius: 999,
          }}
        >
          <div
            style={{
              width: `${progressPercent}%`,
              height: "100%",
              borderRadius: 999,
              background: accent,
              transition: "width 0.4s ease",
            }}
          />
        </div>
        <div style={{ marginTop: 8, fontSize: typography.small.fontSize }}>
          {progress.completed} / {progress.total} 단계 완료
        </div>
      </div>
      <div style={{ marginTop: 24 }}>
        <button
          type="button"
          className={clsx("hero-card__action", { "hero-card__action--warning": isWarning })}
          style={{
            padding: "12px 20px",
            borderRadius: 16,
            border: "none",
            fontFamily: typography.heading.fontFamily,
            fontWeight: typography.heading.fontWeight,
            fontSize: typography.heading.fontSize,
            background: isWarning ? warningColor : accent,
            color: surface,
            cursor: "pointer",
          }}
          onClick={() => {
            triggerFx({
              id: isWarning ? "energy_warning" : "quest_complete",
              priority: isWarning ? FX_PRIORITY.energy_warning : FX_PRIORITY.quest_complete,
              duration: 800,
            });
            onActionClick?.();
          }}
        >
          {nextActionLabel}
        </button>
      </div>
      {isWarning && (
        <div
          className="hero-card__warning"
          style={{
            position: "absolute",
            top: 16,
            right: 16,
            padding: "6px 10px",
            borderRadius: 999,
            color: surface,
            background: warningColor,
            fontSize: typography.caption.fontSize,
            fontWeight: 600,
          }}
        >
          에너지 충전 필요
        </div>
      )}
      <div
        className="hero-card__fx-layer"
        aria-hidden
        style={{
          position: "absolute",
          inset: 0,
          pointerEvents: "none",
          boxShadow: isWarning ? glow.danger : undefined,
        }}
      />
    </div>
  );
};
