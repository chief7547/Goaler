import { beforeEach, describe, expect, it } from "vitest";

import { FX_PRIORITY, useFxStore } from "./fxStore";

describe("useFxStore", () => {
  beforeEach(() => {
    useFxStore.setState({ queue: [], prefersReducedMotion: false });
  });

  it("deduplicates FX by id and respects priority ordering", () => {
    const pushFx = useFxStore.getState().pushFx;

    pushFx({ id: "quest_complete", priority: FX_PRIORITY.quest_complete, duration: 500 });
    pushFx({ id: "stage_upgrade", priority: FX_PRIORITY.stage_upgrade, duration: 1500 });
    pushFx({ id: "quest_complete", priority: FX_PRIORITY.quest_complete, duration: 500 });

    const queue = useFxStore.getState().queue;

    expect(queue).toHaveLength(2);
    expect(queue[0].id).toBe("stage_upgrade");
    expect(queue[1].id).toBe("quest_complete");
  });

  it("limits simultaneous FX to three items keeping the highest priority ones", () => {
    const pushFx = useFxStore.getState().pushFx;

    pushFx({ id: "fx-1", priority: 3, duration: 300 });
    pushFx({ id: "fx-2", priority: 3, duration: 300 });
    pushFx({ id: "stage_upgrade", priority: 1, duration: 1500 });
    pushFx({ id: "boss_adjust", priority: 2, duration: 800 });

    const queue = useFxStore.getState().queue;

    expect(queue).toHaveLength(3);
    const ids = queue.map((item) => item.id);
    expect(ids[0]).toBe("stage_upgrade");
    expect(ids[1]).toBe("boss_adjust");
    expect(ids.includes("fx-1") || ids.includes("fx-2")).toBe(true);
  });

  it("maps FX ids to reduced variants when prefersReducedMotion is true", () => {
    const store = useFxStore.getState();
    store.setReducedMotion(true);

    store.pushFx({ id: "quest_complete", priority: FX_PRIORITY.quest_complete, duration: 500 });

    const queue = useFxStore.getState().queue;
    expect(queue[0].id).toBe("quest_complete_reduced");
    expect(useFxStore.getState().prefersReducedMotion).toBe(true);
  });
});
