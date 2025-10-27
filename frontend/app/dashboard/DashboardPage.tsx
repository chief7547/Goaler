import { HeroCard } from "../../components/HeroCard";
import { QuestCard } from "../../components/QuestCard";
import { ChecklistItem } from "../../components/ChecklistItem";
import { FxProvider } from "../../components/FxContext";
import { FxLayer } from "../../components/FxLayer";

const sampleQuests = [
  {
    id: "q1",
    title: "15km LSD 달리기",
    description: "페이스 조절에 집중하세요",
    difficulty: "NORMAL" as const,
    reason: "보스전을 위한 체력 확보",
  },
  {
    id: "q2",
    title: "보강 운동 30분",
    description: "하체 위주 강화",
    difficulty: "EASY" as const,
    reason: "회복일",
  },
];

export const DashboardPage: React.FC = () => {
  return (
    <FxProvider>
      <div
        style={{
          position: "relative",
          padding: 32,
          background: "#0B1026",
          minHeight: "100vh",
          color: "#E5E9FF",
        }}
      >
        <FxLayer />
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
            gap: 24,
          }}
        >
          <HeroCard
            theme="game"
            stageLabel="Stage 1 · Energy"
            goalTitle="하프 마라톤 완주"
            progress={{ completed: 3, total: 5 }}
            energyStatus="KEEPING_PACE"
            nextActionLabel="오늘의 추천 퀘스트"
          />
          <div>
            <h2 style={{ marginBottom: 16 }}>오늘의 체크리스트</h2>
            <ChecklistItem theme="game" title="스트레칭 10분" subtitle="몸풀기부터 시작" state="completed" />
            <ChecklistItem theme="game" title="코어 운동" subtitle="플랭크 3세트" state="pending" />
          </div>
        </div>

        <section style={{ marginTop: 48 }}>
          <h2 style={{ marginBottom: 16 }}>추천 퀘스트</h2>
          <div style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
            {sampleQuests.map((quest) => (
              <QuestCard
                key={quest.id}
                theme="game"
                title={quest.title}
                description={quest.description}
                difficulty={quest.difficulty}
                variationReason={quest.reason}
              />
            ))}
          </div>
        </section>
      </div>
    </FxProvider>
  );
};

export default DashboardPage;
