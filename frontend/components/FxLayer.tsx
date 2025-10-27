import { useEffect } from "react";
import { useFxLayer } from "./FxContext";

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
      {queue.map((fx) => (
        <div
          key={fx.id}
          data-fx={fx.id}
          style={{ position: "absolute", inset: 0 }}
        />
      ))}
    </div>
  );
};
