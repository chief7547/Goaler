import { GoalsPageContent } from "../../components/goals/GoalsPageContent";

export default function GoalsPage() {
  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold" style={{ fontFamily: "var(--font-heading)" }}>
          목표 & 보스 타임라인
        </h1>
        <p className="text-sm text-[var(--text-secondary)]">
          주간 계획과 일일 퀘스트를 연결해 보스전을 준비하세요. 진행 상황에 따라 FX가 자동으로 트리거됩니다.
        </p>
      </header>
      <GoalsPageContent />
    </div>
  );
}
