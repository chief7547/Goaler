/* eslint-disable storybook/no-renderer-packages */
import type { Meta, StoryObj } from "@storybook/react";
import { ReminderForm } from "../components/settings/ReminderForm";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { type ReactNode, useEffect } from "react";

const MockProvider = ({ children }: { children: ReactNode }) => {
  const queryClient = new QueryClient();
  queryClient.setQueryData(["reminders"], [
    {
      reminderId: "r-1",
      goalId: "g-123",
      channel: "slack",
      frequency: "daily",
      time: "07:00",
      timezone: "Asia/Seoul",
      active: true,
      lastSentAt: "2025-02-19T22:00:00Z",
    },
  ]);

  useEffect(() => {
    const originalFetch = global.fetch;
    global.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === "string" ? input : input.toString();
      if (url.includes("/reminders/test")) {
        return new Response(JSON.stringify({ ok: true, referenceId: "story-test" }), { status: 200 });
      }
      if (url.includes("/reminders")) {
        return new Response(init?.body ?? "{}", { status: 200 });
      }
      return originalFetch(input, init);
    };
    return () => {
      global.fetch = originalFetch;
    };
  }, []);

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
};

const meta: Meta<typeof ReminderForm> = {
  title: "Settings/ReminderForm",
  component: ReminderForm,
  decorators: [
    (Story) => (
      <MockProvider>
        <Story />
      </MockProvider>
    ),
  ],
};

export default meta;

type Story = StoryObj<typeof ReminderForm>;

export const Default: Story = {};
