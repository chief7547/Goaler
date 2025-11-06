"use client";

import clsx from "clsx";
import type { ChatMessage } from "../../lib/api/types";
import { colors, typography } from "../../theme/tokens";
import { useThemeVariant } from "../../theme/ThemeProvider";

interface ChatMessageBubbleProps {
  message: ChatMessage;
}

export const ChatMessageBubble: React.FC<ChatMessageBubbleProps> = ({ message }) => {
  const { theme } = useThemeVariant();
  const isUser = message.role === "user";
  const bubbleColor = isUser ? colors.primary[theme] : colors.background.card[theme];
  const textColor = isUser ? colors.background.surface[theme] : colors.text.primary[theme];

  return (
    <div
      className={clsx("flex w-full", isUser ? "justify-end" : "justify-start")}
      data-role={message.role}
    >
      <div
        className={clsx(
          "max-w-[80%] rounded-3xl px-4 py-3 shadow-lg",
          isUser ? "rounded-br-sm" : "rounded-bl-sm"
        )}
        style={{
          background: bubbleColor,
          color: textColor,
          fontFamily: typography.body.fontFamily,
          lineHeight: typography.body.lineHeight,
        }}
      >
        <p className="whitespace-pre-line text-sm" style={{ margin: 0 }}>
          {message.content}
        </p>
        <div className="mt-2 flex flex-wrap gap-2 text-xs opacity-70">
          <time>{new Date(message.createdAt).toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit" })}</time>
          {message.role === "assistant" && <span>코치</span>}
        </div>
        {message.suggestions && message.suggestions.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {message.suggestions.map((suggestion) => (
              <span
                key={suggestion.id}
                className="rounded-full border px-3 py-1 text-xs"
                style={{
                  borderColor: isUser ? "rgba(255,255,255,0.6)" : colors.accent.cyan[theme],
                  color: isUser ? "rgba(255,255,255,0.85)" : colors.accent.cyan[theme],
                }}
              >
                {suggestion.label}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
