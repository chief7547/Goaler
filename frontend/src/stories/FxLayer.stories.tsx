import { useEffect } from "react";
import type { ReactNode } from "react";

import { FxLayer } from "../components/FxLayer";
import { FxProvider, triggerFx } from "../components/FxContext";
import { FX_PRIORITY, useFxStore } from "../stores/fxStore";

type StoryComponentFn = () => ReactNode;

const meta = {
  title: "FxLayer/Examples",
  component: FxLayer,
  decorators: [
    (StoryComponent: StoryComponentFn) => (
      <FxProvider>
        <div style={{ position: "relative", minHeight: 360, background: "#0B1026", borderRadius: 24 }}>
          <StoryComponent />
        </div>
      </FxProvider>
    ),
  ],
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;

const useResetFx = () => {
  useEffect(() => {
    useFxStore.setState({ queue: [], prefersReducedMotion: false });
    return () => {
      useFxStore.setState({ queue: [], prefersReducedMotion: false });
      delete document.body.dataset.theme;
    };
  }, []);
};

export const StageUpgrade = {
  render: () => {
    useResetFx();
    useEffect(() => {
      triggerFx({ id: "stage_upgrade", priority: FX_PRIORITY.stage_upgrade, duration: 1600 });
    }, []);
    return <FxLayer />;
  },
};

export const QuestComplete = {
  render: () => {
    useResetFx();
    useEffect(() => {
      triggerFx({ id: "quest_complete", priority: FX_PRIORITY.quest_complete, duration: 600 });
    }, []);
    return <FxLayer />;
  },
};

export const EnergyWarningReduced = {
  render: () => {
    useResetFx();
    useEffect(() => {
      useFxStore.getState().setReducedMotion(true);
      triggerFx({
        id: "energy_warning",
        priority: FX_PRIORITY.energy_warning,
        duration: 620,
        meta: { message: "Energy Low" },
      });
    }, []);
    return <FxLayer />;
  },
};

export const ProfessionalTheme = {
  render: () => {
    useResetFx();
    useEffect(() => {
      document.body.dataset.theme = "pro";
      triggerFx({ id: "stage_upgrade", priority: FX_PRIORITY.stage_upgrade, duration: 1600 });
      triggerFx({ id: "quest_complete", priority: FX_PRIORITY.quest_complete, duration: 600 });
      triggerFx({ id: "loot_record", priority: FX_PRIORITY.loot_record, duration: 1000 });
    }, []);
    return <FxLayer />;
  },
  parameters: {
    backgrounds: {
      default: "Professional",
      values: [{ name: "Professional", value: "#0F172A" }],
    },
  },
};
