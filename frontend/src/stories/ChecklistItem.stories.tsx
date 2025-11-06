/* eslint-disable storybook/no-renderer-packages */
import type { Meta, StoryObj } from "@storybook/react";
import { ChecklistItem } from "../components/ChecklistItem";

const meta: Meta<typeof ChecklistItem> = {
  title: "Checklist/ChecklistItem",
  component: ChecklistItem,
  args: {
    title: "스트레칭 10분",
    subtitle: "몸풀기부터 시작",
    state: "pending",
  },
};

export default meta;

type Story = StoryObj<typeof ChecklistItem>;

export const Pending: Story = {};
export const Completed: Story = {
  args: {
    state: "completed",
  },
};
export const Deferred: Story = {
  args: {
    state: "deferred",
  },
};
