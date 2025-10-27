import { colors, typography } from "../theme/tokens";
import { triggerFx } from "./FxContext";
import { FX_PRIORITY } from "../stores/fxStore";

type ThemeVariant = "game" | "pro";

type ChecklistState = "pending" | "completed" | "deferred" | "skipped";

interface ChecklistItemProps {
  theme: ThemeVariant;
  title: string;
  subtitle?: string;
  state?: ChecklistState;
  onToggle?: (next: ChecklistState) => void;
}

export const ChecklistItem: React.FC<ChecklistItemProps> = ({
  theme,
  title,
  subtitle,
  state = "pending",
  onToggle,
}) => {
  const isCompleted = state === "completed";

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 16,
        padding: "12px 16px",
        borderRadius: 16,
        background: isCompleted
          ? "rgba(44, 229, 167, 0.12)"
          : "rgba(255, 255, 255, 0.06)",
        color: colors.text.primary[theme],
      }}
    >
      <button
        type="button"
        aria-pressed={isCompleted}
        style={{
          width: 28,
          height: 28,
          borderRadius: 8,
          border: `2px solid ${colors.primary[theme]}`,
          background: isCompleted ? colors.success[theme] : "transparent",
          cursor: "pointer",
        }}
        onClick={() => {
          const next = isCompleted ? "pending" : "completed";
          if (next === "completed") {
            triggerFx({ id: "quest_complete", priority: FX_PRIORITY.quest_complete, duration: 520 });
          }
          onToggle?.(next);
        }}
      />
      <div style={{ flex: 1 }}>
        <div
          style={{
            fontFamily: typography.body.fontFamily,
            fontSize: typography.body.fontSize,
            fontWeight: 600,
          }}
        >
          {title}
        </div>
        {subtitle && (
          <div
            style={{
              marginTop: 4,
              fontSize: typography.small.fontSize,
              opacity: 0.7,
            }}
          >
            {subtitle}
          </div>
        )}
      </div>
    </div>
  );
};
