import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api/client";
import type { ChatSession } from "../lib/api/types";

const chatKey = ["chat", "session"] as const;

export function useChatSession() {
  const query = useQuery<ChatSession>({
    queryKey: chatKey,
    queryFn: api.getChatSession,
  });
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: api.sendChatMessage,
    onSuccess: (data) => {
      queryClient.setQueryData(chatKey, data);
    },
  });

  return {
    session: query.data,
    isLoading: query.isLoading,
    error: query.error,
    sendMessage: mutation.mutateAsync,
    isSending: mutation.isPending,
  };
}
