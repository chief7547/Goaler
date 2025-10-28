"use client";

import { useMemo, useState } from "react";
import { HeroCard } from "../HeroCard";
import { ChecklistItem, type ChecklistState } from "../ChecklistItem";
import { QuestCard } from "../QuestCard";
import { triggerFx } from "../FxContext";
import { FX_PRIORITY } from "../../stores/fxStore";

type ChecklistEntry = {
  id: string;
  title: string;
  subtitle?: string;
  state: ChecklistState;
};

const initialChecklist: ChecklistEntry[] = [
  {
    id: "stretch",
    title: "활주로 스트레칭",
    subtitle: "10분 동안 관절을 풀어주세요",
    state: "completed" as const,
  },
  {
    id: "core",
    title: "코어 루틴",
    subtitle: "플랭크 3세트 · 45초",
    state: "pending" as const,
  },
  {
    id: "hydration",
    title: "포션 준비",
    subtitle: "전투 30분 전 수분 보충",
    state: "pending" as const,
  },
];

const sampleQuests = [
  {
    id: "quest-1",
    title: "15km LSD 달리기",
    description: "호흡을 일정하게 유지하면서 긴 거리를 경험하세요.",
    difficulty: "NORMAL" as const,
    reason: "보스전에 필요한 지구력 확보",
  },
  {
    id: "quest-2",
    title: "저강도 회복 러닝",
    description: "페이스 6:30으로 30분 동안 가볍게 달립니다.",
    difficulty: "EASY" as const,
    reason: "근육 피로 회복",
  },
];

export const DashboardScreen: React.FC = () => {
  const [checklist, setChecklist] = useState<ChecklistEntry[]>(initialChecklist);
  const [completedQuests, setCompletedQuests] = useState<Record<string, boolean>>({});
  const completedCount = useMemo(
    () => checklist.filter((item) => item.state === "completed").length,
    [checklist]
  );

  const handleChecklistToggle = (id: string, nextState: ChecklistState) => {
    setChecklist((prev) =>
      prev.map((item) => (item.id === id ? { ...item, state: nextState } : item))
    );
  };

  return (
    <div className="space-y-12">
      <section className="grid gap-6 lg:grid-cols-[minmax(0,_2fr)_minmax(0,_1fr)]">
        <HeroCard
          stageLabel="Stage 1 · Energy"
          goalTitle="하프 마라톤 완주"
          progress={{ completed: completedCount, total: checklist.length }}
          energyStatus={completedCount >= 2 ? "READY_FOR_BOSS" : "KEEPING_PACE"}
          nextActionLabel="오늘의 추천 퀘스트 보기"
          onActionClick={() => {
            triggerFx({ id: "stage_upgrade", priority: FX_PRIORITY.stage_upgrade, duration: 1600 });
          }}
        />
        <div className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold" style={{ fontFamily: "var(--font-heading)" }}>
              체크리스트
            </h2>
            <span className="text-sm text-[var(--text-secondary)]">
              {completedCount} / {checklist.length} 완료
            </span>
          </div>
          <div className="mt-6 space-y-4">
            {checklist.map((item) => (
              <ChecklistItem
                key={item.id}
                title={item.title}
                subtitle={item.subtitle}
                state={item.state}
                onToggle={(next) => handleChecklistToggle(item.id, next)}
              />
            ))}
          </div>
        </div>
      </section>

      <section>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold" style={{ fontFamily: "var(--font-heading)" }}>
            오늘의 추천 퀘스트
          </h2>
          <button
            type="button"
            className="rounded-full border border-white/20 bg-white/5 px-3 py-1 text-xs text-[var(--text-secondary)] hover:border-white/40"
            onClick={() =>
              triggerFx({ id: "loot_record", priority: FX_PRIORITY.loot_record, duration: 600 })
            }
          >
            변주 이유 보기
          </button>
        </div>
        <div className="mt-6 flex flex-wrap gap-6">
          {sampleQuests.map((quest) => (
            <QuestCard
              key={quest.id}
              title={quest.title}
              description={quest.description}
              difficulty={quest.difficulty}
              variationReason={quest.reason}
              onComplete={() =>
                setCompletedQuests((prev) => ({ ...prev, [quest.id]: true }))
              }
              onHold={() =>
                triggerFx({ id: "boss_adjust", priority: FX_PRIORITY.boss_adjust, duration: 720 })
              }
              onSkip={() =>
                triggerFx({ id: "energy_warning", priority: FX_PRIORITY.energy_warning, duration: 620 })
              }
            />
          ))}
        </div>
        {Object.values(completedQuests).some(Boolean) && (
          <p className="mt-4 text-sm text-[var(--text-secondary)]">
            완료한 퀘스트는 리포트 탭에서 전리품으로 정리됩니다.
          </p>
        )}
      </section>
    </div>
  );
};
