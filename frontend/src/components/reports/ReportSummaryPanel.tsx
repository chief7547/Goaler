"use client";

import type { ReportSummary } from "../../lib/api/types";
import { triggerFx } from "../FxContext";
import { FX_PRIORITY } from "../../stores/fxStore";
import { typography } from "../../theme/tokens";

interface ReportSummaryPanelProps {
  report: ReportSummary;
}

export const ReportSummaryPanel: React.FC<ReportSummaryPanelProps> = ({ report }) => {
  return (
    <div className="space-y-8">
      <section className="grid gap-4 lg:grid-cols-2">
        {report.highlights.map((highlight) => {
          const priority =
            FX_PRIORITY[highlight.fx as keyof typeof FX_PRIORITY] ?? FX_PRIORITY.quest_complete;
          return (
            <button
              key={highlight.id}
              type="button"
              className="rounded-3xl border border-white/10 bg-white/5 p-4 text-left transition hover:border-white/20"
              onClick={() => triggerFx({ id: highlight.fx, priority, duration: 900 })}
            >
            <p className="text-xs uppercase tracking-[0.3em] text-[var(--text-secondary)]">하이라이트</p>
            <h3 className="mt-2 text-lg font-semibold" style={{ fontFamily: typography.heading.fontFamily }}>
              {highlight.title}
            </h3>
            <p className="mt-2 text-sm text-[var(--text-secondary)]">{highlight.description}</p>
            </button>
          );
        })}
      </section>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold" style={{ fontFamily: typography.heading.fontFamily }}>
          분석 지표
        </h2>
        <div className="space-y-3 rounded-3xl border border-white/10 bg-white/5 p-4">
          {report.metrics.map((metric) => (
            <div key={metric.metricId} className="rounded-2xl bg-black/20 p-4">
              <div className="flex items-center justify-between text-sm">
                <span>{metric.name}</span>
                <span>{metric.unit}</span>
              </div>
              <div className="mt-3 grid gap-2 md:grid-cols-4">
                {metric.values.map((value) => (
                  <div key={value.label} className="rounded-xl bg-black/30 p-3 text-sm text-[var(--text-secondary)]">
                    <p className="text-xs uppercase tracking-[0.2em]">{value.label}</p>
                    <p className="mt-2 text-lg font-semibold" style={{ fontFamily: typography.heading.fontFamily }}>
                      {value.value}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        {report.story.map((item) => (
          <article key={item.heading} className="rounded-3xl border border-white/10 bg-white/5 p-4">
            <h3 className="text-lg font-semibold" style={{ fontFamily: typography.heading.fontFamily }}>
              {item.heading}
            </h3>
            <p className="mt-2 text-sm text-[var(--text-secondary)]">{item.body}</p>
          </article>
        ))}
      </section>
    </div>
  );
};
