"use client";

import { FormEvent, useState } from "react";
import { colors, typography } from "../../theme/tokens";
import { useThemeVariant } from "../../theme/ThemeProvider";

interface ChatComposerProps {
  onSend: (message: string) => Promise<void>;
  disabled?: boolean;
}

export const ChatComposer: React.FC<ChatComposerProps> = ({ onSend, disabled = false }) => {
  const { theme } = useThemeVariant();
  const [value, setValue] = useState("");

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!value.trim()) return;
    await onSend(value.trim());
    setValue("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-3xl border border-white/10 bg-white/5 p-4"
      style={{ backdropFilter: "blur(12px)" }}
    >
      <textarea
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="오늘 코치와 나누고 싶은 이야기를 적어보세요"
        className="h-24 w-full resize-none rounded-2xl border border-white/10 bg-transparent p-4 text-sm outline-none"
        style={{
          color: colors.text.primary[theme],
          fontFamily: typography.body.fontFamily,
        }}
        disabled={disabled}
      />
      <div className="mt-3 flex items-center justify-between text-xs text-[var(--text-secondary)]">
        <span>엔터로 전송 · Shift+Enter 줄바꿈</span>
        <button
          type="submit"
          className="rounded-full px-4 py-2 text-sm font-semibold uppercase tracking-[0.2em]"
          style={{
            background: colors.primary[theme],
            color: colors.background.surface[theme],
            opacity: disabled ? 0.5 : 1,
          }}
          disabled={disabled}
        >
          전송
        </button>
      </div>
    </form>
  );
};
