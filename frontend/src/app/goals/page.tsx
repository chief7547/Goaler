export default function GoalsPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold" style={{ fontFamily: "var(--font-heading)" }}>
        목표 & 보스 타임라인
      </h1>
      <p className="text-sm text-[var(--text-secondary)]">
        보스 단계, 주간 계획, 일일 퀘스트를 연결하는 상세 화면은 `docs/FRONTEND_DESIGN.md` 4.3절을 따라
        구성합니다. Zustand 스토어와 React Query 조합으로 목표 상세 데이터를 주입하면 됩니다.
      </p>
    </div>
  );
}
