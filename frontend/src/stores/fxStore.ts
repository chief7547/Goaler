import { create } from "zustand";

export type FxId =
  | "stage_upgrade"
  | "quest_complete"
  | "energy_warning"
  | "boss_adjust"
  | "loot_record"
  | `${string}`;

export type FxPayload = {
  id: FxId;
  priority: 1 | 2 | 3;
  duration: number;
  meta?: Record<string, unknown>;
};

interface FxState {
  queue: FxPayload[];
  prefersReducedMotion: boolean;
  pushFx: (fx: FxPayload) => void;
  popFx: (id: FxId) => void;
  setReducedMotion: (flag: boolean) => void;
}

const MAX_SIMULTANEOUS_FX = 3;

export const useFxStore = create<FxState>((set, get) => ({
  queue: [],
  prefersReducedMotion: false,
  pushFx: (fx) => {
    const { queue, prefersReducedMotion } = get();
    if (queue.some((item) => item.id === fx.id)) {
      return;
    }
    const transformed: FxPayload = prefersReducedMotion
      ? { ...fx, id: `${fx.id}_reduced` as FxId }
      : fx;

    const nextQueue = [...queue, transformed].sort((a, b) => a.priority - b.priority);
    if (nextQueue.length > MAX_SIMULTANEOUS_FX) {
      nextQueue.pop();
    }
    set({ queue: nextQueue });
  },
  popFx: (id) =>
    set((state) => ({
      queue: state.queue.filter((fx) => fx.id !== id),
    })),
  setReducedMotion: (flag) => set({ prefersReducedMotion: flag }),
}));

export const FX_PRIORITY = {
  stage_upgrade: 1 as const,
  boss_adjust: 2 as const,
  quest_complete: 3 as const,
  energy_warning: 3 as const,
  loot_record: 3 as const,
};

export type FxPriorityKey = keyof typeof FX_PRIORITY;
