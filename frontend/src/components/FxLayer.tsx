"use client";

import { useEffect, type ReactNode } from "react";
import { useFxLayer } from "./FxContext";
import type { FxPayload } from "../stores/fxStore";

const renderFxNode = (fx: FxPayload): ReactNode => {
  const message = typeof fx.meta?.message === "string" ? fx.meta.message : undefined;

  switch (fx.id) {
    case "stage_upgrade":
      return <div className="fx-stage-upgrade" aria-hidden />;
    case "stage_upgrade_reduced":
      return <div className="fx-stage-upgrade-reduced" aria-hidden />;
    case "quest_complete":
      return <div className="fx-quest-complete" aria-hidden />;
    case "quest_complete_reduced":
      return <div className="fx-quest-complete-reduced">Quest Complete</div>;
    case "energy_warning":
      return (
        <div className="fx-energy-warning" role="status">
          {message ?? "ENERGY WARNING"}
        </div>
      );
    case "energy_warning_reduced":
      return (
        <div className="fx-energy-warning-reduced" role="status">
          {message ?? "ENERGY LOW"}
        </div>
      );
    case "boss_adjust":
      return <div className="fx-boss-adjust" aria-hidden />;
    case "boss_adjust_reduced":
      return <div className="fx-boss-adjust-reduced" aria-hidden />;
    case "loot_record":
      return (
        <div className="fx-loot-record" role="status">
          <span>성과 기록</span>
          <span>깨달음</span>
          <span>감정</span>
        </div>
      );
    case "loot_record_reduced":
      return <div className="fx-loot-record-reduced">Loot Logged</div>;
    default:
      return null;
  }
};

export const FxLayer: React.FC = () => {
  const { queue, popFx } = useFxLayer();

  useEffect(() => {
    const timers = queue.map((fx) =>
      setTimeout(() => popFx(fx.id), fx.duration)
    );
    return () => {
      timers.forEach(clearTimeout);
    };
  }, [queue, popFx]);

  if (queue.length === 0) {
    return null;
  }

  return (
    <div
      className="fx-layer"
      style={{
        position: "absolute",
        inset: 0,
        pointerEvents: "none",
        zIndex: 50,
      }}
    >
      {queue.map((fx) => {
        const content = renderFxNode(fx);
        if (!content) {
          return null;
        }
        return (
          <div
            key={`${fx.id}-${fx.duration}`}
            data-fx={fx.id}
            style={{ position: "absolute", inset: 0 }}
          >
            {content}
          </div>
        );
      })}
    </div>
  );
};
