"use client";

import { useCallback } from "react";
import { useChatSession } from "../../hooks/useChatData";
import { ChatMessageBubble } from "./ChatMessageBubble";
import { ChatComposer } from "./ChatComposer";
import { ChatContextPanel } from "./ChatContextPanel";
import { triggerFx } from "../FxContext";
import { FX_PRIORITY } from "../../stores/fxStore";

export const ChatPageContent: React.FC = () => {
  const { session, isLoading, error, sendMessage, isSending } = useChatSession();

  const handleSend = useCallback(
    async (content: string) => {
      triggerFx({ id: "loot_record", priority: FX_PRIORITY.loot_record, duration: 680 });
      await sendMessage(content);
    },
    [sendMessage]
  );

  if (isLoading) {
    return <p className="text-sm text-[var(--text-secondary)]">코치 데이터를 불러오는 중...</p>;
  }

  if (error) {
    return <p className="text-sm text-red-300">챗 데이터를 불러오지 못했습니다: {(error as Error).message}</p>;
  }

  if (!session) {
    return null;
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,_3fr)_minmax(280px,_1fr)]">
      <div className="flex h-full flex-col gap-4">
        <div className="flex-1 space-y-4 overflow-y-auto rounded-3xl border border-white/10 bg-white/5 p-6">
          {session.messages.map((message) => (
            <ChatMessageBubble key={message.messageId} message={message} />
          ))}
        </div>
        <ChatComposer onSend={handleSend} disabled={isSending} />
      </div>
      <ChatContextPanel context={session.context} />
    </div>
  );
};
