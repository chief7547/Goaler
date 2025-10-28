import { ReportsPageContent } from "../../components/reports/ReportsPageContent";

export default function ReportsPage() {
  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold" style={{ fontFamily: "var(--font-heading)" }}>
          리포트 & 회고
        </h1>
        <p className="text-sm text-[var(--text-secondary)]">
          주간·월간 하이라이트를 확인하고, Stage 승급과 경고 이벤트를 되짚어 보세요.
        </p>
      </header>
      <ReportsPageContent />
    </div>
  );
}
