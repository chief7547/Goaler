/* eslint-disable storybook/no-renderer-packages */
import type { Meta, StoryObj } from "@storybook/react";
import { BossTimeline } from "../components/goals/BossTimeline";

const sampleStages = [
  {
    bossId: "b-1",
    title: "체력 다지기",
    status: "IN_PROGRESS" as const,
    targetWeek: 6,
    weeklyPlan: [
      { title: "LSD 주간 루틴", week: 3 },
      { title: "페이스 조절 훈련", week: 4 },
    ],
    dailyTasks: [],
  },
  {
    bossId: "b-2",
    title: "레이스 시뮬레이션",
    status: "READY" as const,
    targetWeek: 8,
    weeklyPlan: [{ title: "하프 마라톤 페이스 점검", week: 8 }],
    dailyTasks: [],
  },
];

const meta: Meta<typeof BossTimeline> = {
  title: "Goals/BossTimeline",
  component: BossTimeline,
  args: {
    stages: sampleStages,
  },
};

export default meta;

type Story = StoryObj<typeof BossTimeline>;

export const Default: Story = {};
