"use client";

import { FormEvent, useMemo, useState } from "react";
import { useReminders } from "../../hooks/useReminders";
import { colors, typography } from "../../theme/tokens";
import { useThemeVariant } from "../../theme/ThemeProvider";

const frequencies = [
  { value: "daily", label: "매일" },
  { value: "weekly", label: "매주" },
  { value: "once", label: "한 번" },
];

export const ReminderForm: React.FC = () => {
  const { theme } = useThemeVariant();
  const { reminders, isLoading, error, updateReminder, isUpdating, testReminder, isTesting } = useReminders();
  const reminder = useMemo(() => reminders[0], [reminders]);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  if (isLoading) {
    return <p className="text-sm text-[var(--text-secondary)]">알림 데이터를 불러오는 중입니다…</p>;
  }

  if (error) {
    return <p className="text-sm text-red-300">알림 설정을 불러오지 못했습니다.</p>;
  }

  if (!reminder) {
    return <p className="text-sm text-[var(--text-secondary)]">설정된 알림이 없습니다. 챗에서 먼저 목표를 생성하세요.</p>;
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const updated = {
      ...reminder,
      frequency: formData.get("frequency") as typeof reminder.frequency,
      time: formData.get("time") as string,
      active: formData.get("active") === "on",
    };
    await updateReminder(updated);
    setStatusMessage("알림 설정이 저장되었습니다.");
  };

  const handleTestReminder = async () => {
    const response = await testReminder();
    setStatusMessage(`테스트가 발송되었습니다. ID: ${response.referenceId}`);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-3xl border border-white/10 bg-white/5 p-6">
      <header className="space-y-2">
        <h2 className="text-lg font-semibold" style={{ fontFamily: typography.heading.fontFamily }}>
          Slack 알림
        </h2>
        <p className="text-sm text-[var(--text-secondary)]">보스전 리마인더를 원하는 시간에 받아보세요.</p>
      </header>

      <label className="block text-sm">
        <span className="text-[var(--text-secondary)]">전송 시간</span>
        <input
          name="time"
          type="time"
          defaultValue={reminder.time}
          className="mt-1 w-full rounded-xl border border-white/15 bg-black/20 p-3 text-sm"
          style={{
            color: colors.text.primary[theme],
            fontFamily: typography.body.fontFamily,
          }}
        />
      </label>

      <label className="block text-sm">
        <span className="text-[var(--text-secondary)]">빈도</span>
        <select
          name="frequency"
          defaultValue={reminder.frequency}
          className="mt-1 w-full rounded-xl border border-white/15 bg-black/20 p-3 text-sm"
          style={{ color: colors.text.primary[theme] }}
        >
          {frequencies.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <label className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
        <input type="checkbox" name="active" defaultChecked={reminder.active} /> 활성화
      </label>

      <div className="flex flex-wrap gap-3">
        <button
          type="submit"
          className="rounded-full px-4 py-2 text-sm font-semibold"
          style={{
            background: colors.primary[theme],
            color: colors.background.surface[theme],
            opacity: isUpdating ? 0.6 : 1,
          }}
          disabled={isUpdating}
        >
          저장하기
        </button>
        <button
          type="button"
          className="rounded-full border border-white/20 px-4 py-2 text-sm"
          onClick={handleTestReminder}
          disabled={isTesting}
        >
          테스트 발송
        </button>
      </div>

      {statusMessage && <p className="text-sm text-[var(--text-secondary)]">{statusMessage}</p>}
    </form>
  );
};
