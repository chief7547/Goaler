import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api/client";
import type { Reminder, ReminderTestResponse } from "../lib/api/types";

const remindersKey = ["reminders"] as const;

export function useReminders() {
  const queryClient = useQueryClient();
  const listQuery = useQuery<Reminder[]>({
    queryKey: remindersKey,
    queryFn: api.listReminders,
  });

  const updateMutation = useMutation({
    mutationFn: api.updateReminder,
    onSuccess: (updated) => {
      queryClient.setQueryData(remindersKey, (prev?: Reminder[]) => {
        if (!prev) return [updated];
        const next = prev.map((item) => (item.reminderId === updated.reminderId ? updated : item));
        return next;
      });
    },
  });

  const testMutation = useMutation<ReminderTestResponse>({
    mutationFn: api.sendReminderTest,
  });

  return {
    reminders: listQuery.data ?? [],
    isLoading: listQuery.isLoading,
    error: listQuery.error,
    updateReminder: updateMutation.mutateAsync,
    isUpdating: updateMutation.isPending,
    testReminder: testMutation.mutateAsync,
    isTesting: testMutation.isPending,
  };
}
