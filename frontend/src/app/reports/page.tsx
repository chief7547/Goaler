export default function ReportsPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold" style={{ fontFamily: "var(--font-heading)" }}>
        리포트 & 회고
      </h1>
      <p className="text-sm text-[var(--text-secondary)]">
        리포트 화면은 <code>docs/FRONTEND_API_CONTRACT.md</code>의 <code>
        /reports/{"{"}period{"}"}</code> 계약과 <code>docs/FRONTEND_QA_PLAN.md</code>
        명세를 토대로 차트/스토리/분석 패널을 구현할 예정입니다. 현재는 골격만 남겨 두었습니다.
      </p>
    </div>
  );
}
