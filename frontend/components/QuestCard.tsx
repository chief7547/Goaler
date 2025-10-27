import clsx from "clsx";
import { colors, typography, radius } from "../theme/tokens";
import { triggerFx } from "./FxContext";
import { FX_PRIORITY } from "../stores/fxStore";

type Difficulty = "EASY" | "NORMAL" | "HARD";

type ThemeVariant = "game" | "pro";

interface QuestCardProps {
  theme: ThemeVariant;
  title: string;
  description?: string;
  difficulty: Difficulty;
  variationReason?: string;
  onComplete?: () => void;
  onHold?: () => void;
  onSkip?: () => void;
}

const difficultyMap: Record<Difficulty, string> = {
  EASY: "#2CE5A7",
  NORMAL: "#6C5CE7",
  HARD: "#FF5C5C",
};

export const QuestCard: React.FC<QuestCardProps> = ({
  theme,
  title,
  description,
  difficulty,
  variationReason,
  onComplete,
  onHold,
  onSkip,
}) => {
  return (
    <div
      style={{
        background: colors.background.card[theme],
        color: colors.text.primary[theme],
        borderRadius: radius.lg,
        padding: 20,
        width: 320,
        minHeight: 220,
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        gap: 16,
      }}
    >
      <div>
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            padding: "4px 10px",
            borderRadius: 999,
            background: difficultyMap[difficulty],
            color: colors.background.surface[theme],
            fontSize: typography.small.fontSize,
            fontWeight: 600,
          }}
        >
          {difficulty === "EASY" ? "쉬움" : difficulty === "NORMAL" ? "보통" : "도전"}
        </div>
        <h3
          style={{
            margin: "16px 0 8px",
            fontFamily: typography.heading.fontFamily,
            fontSize: typography.heading.fontSize,
            lineHeight: typography.heading.lineHeight,
            fontWeight: typography.heading.fontWeight,
          }}
        >
          {title}
        </h3>
        {description && (
          <p
            style={{
              margin: 0,
              fontFamily: typography.body.fontFamily,
              fontSize: typography.body.fontSize,
              lineHeight: typography.body.lineHeight,
              opacity: 0.76,
            }}
          >
            {description}
          </p>
        )}
        {variationReason && (
          <div
            style={{
              marginTop: 12,
              fontSize: typography.small.fontSize,
              opacity: 0.6,
            }}
          >
            {variationReason}
          </div>
        )}
      </div>
      <div
        style={{
          display: "flex",
          gap: 12,
        }}
      >
        <button
          type="button"
          className={clsx("quest-card__button", "quest-card__button--complete")}
          style={{
            flex: 1,
            padding: "10px 12px",
            borderRadius: 16,
            border: "none",
            cursor: "pointer",
            background: colors.success[theme],
            color: colors.background.surface[theme],
            fontWeight: 600,
          }}
          onClick={() => {
            triggerFx({ id: "quest_complete", priority: FX_PRIORITY.quest_complete, duration: 520 });
            onComplete?.();
          }}
        >
          완료
        </button>
        <button
          type="button"
          className="quest-card__button"
          style={{
            flex: 1,
            padding: "10px 12px",
            borderRadius: 16,
            border: `1px solid rgba(255,255,255,0.12)`,
            background: "transparent",
            color: colors.text.primary[theme],
            cursor: "pointer",
          }}
          onClick={onHold}
        >
          보류
        </button>
        <button
          type="button"
          className="quest-card__button"
          style={{
            flex: 1,
            padding: "10px 12px",
            borderRadius: 16,
            border: `1px solid rgba(255,255,255,0.12)`,
            background: "transparent",
            color: colors.text.primary[theme],
            cursor: "pointer",
          }}
          onClick={onSkip}
        >
          건너뛰기
        </button>
      </div>
    </div>
  );
};
