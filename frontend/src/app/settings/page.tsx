export default function SettingsPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold" style={{ fontFamily: "var(--font-heading)" }}>
        설정 & 알림 제어
      </h1>
      <p className="text-sm text-[var(--text-secondary)]">
        Slack 리마인더, 포커스 모드, Reduced Motion 토글 등은 `docs/FRONTEND_QA_PLAN.md`와
        `docs/FRONTEND_FX_GUIDE.md` 5절의 접근성 원칙을 준수해 구현할 예정입니다.
      </p>
    </div>
  );
}
