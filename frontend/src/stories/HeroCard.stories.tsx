/* eslint-disable storybook/no-renderer-packages */
import type { Meta, StoryObj } from "@storybook/react";
import { HeroCard } from "../components/HeroCard";

const meta: Meta<typeof HeroCard> = {
  title: "HeroCard",
  component: HeroCard,
  args: {
    stageLabel: "Stage 1 · Energy",
    goalTitle: "하프 마라톤 완주",
    progress: { completed: 3, total: 5 },
    energyStatus: "KEEPING_PACE",
    nextActionLabel: "오늘의 추천 퀘스트",
  },
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;

type Story = StoryObj<typeof HeroCard>;

export const GameDefault: Story = {
  args: {
    theme: "game",
  },
};

export const GameWarning: Story = {
  args: {
    theme: "game",
    energyStatus: "NEEDS_POTION",
  },
};

export const Professional: Story = {
  args: {
    theme: "pro",
    energyStatus: "KEEPING_PACE",
  },
};
