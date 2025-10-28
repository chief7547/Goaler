"use client";

import { ReminderForm } from "../../components/settings/ReminderForm";
import { useFxStore } from "../../stores/fxStore";

export default function SettingsPage() {
  const { prefersReducedMotion, setReducedMotion } = useFxStore();

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold" style={{ fontFamily: "var(--font-heading)" }}>
          설정 & 알림 제어
        </h1>
        <p className="text-sm text-[var(--text-secondary)]">
          Reduced Motion, Slack 알림 등 접근성과 몰입도를 스스로 조절하세요.
        </p>
      </header>

      <section className="rounded-3xl border border-white/10 bg-white/5 p-6">
        <h2 className="text-lg font-semibold" style={{ fontFamily: "var(--font-heading)" }}>
          모션 설정
        </h2>
        <p className="mt-2 text-sm text-[var(--text-secondary)]">
          모션이 어지럽다면 Reduced Motion을 켜주세요. 모든 FX가 완화된 연출로 대체됩니다.
        </p>
        <label className="mt-4 inline-flex items-center gap-3 text-sm">
          <input
            type="checkbox"
            checked={prefersReducedMotion}
            onChange={(event) => setReducedMotion(event.target.checked)}
          />
          Reduced Motion 활성화
        </label>
      </section>

      <ReminderForm />
    </div>
  );
}
