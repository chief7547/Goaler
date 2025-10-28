/* eslint-disable storybook/no-renderer-packages */
import type { Meta, StoryObj } from "@storybook/react";
import { QuestCard } from "../components/QuestCard";

const meta: Meta<typeof QuestCard> = {
  title: "Quest/QuestCard",
  component: QuestCard,
  args: {
    title: "15km LSD 달리기",
    description: "호흡을 일정하게 유지하면서 긴 거리를 경험하세요.",
    difficulty: "NORMAL",
    variationReason: "보스전 대비 체력 확보",
  },
};

export default meta;

type Story = StoryObj<typeof QuestCard>;

export const Normal: Story = {
  args: {
    theme: "game",
  },
};

export const Hard: Story = {
  args: {
    difficulty: "HARD",
  },
};

export const ProfessionalTheme: Story = {
  args: {
    theme: "pro",
  },
};
