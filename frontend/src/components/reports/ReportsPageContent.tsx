"use client";

import { useState } from "react";
import { useReport } from "../../hooks/useReports";
import { ReportSummaryPanel } from "./ReportSummaryPanel";

const periods: Array<{ label: string; value: "weekly" | "monthly" }> = [
  { label: "주간", value: "weekly" },
  { label: "월간", value: "monthly" },
];

export const ReportsPageContent: React.FC = () => {
  const [period, setPeriod] = useState<"weekly" | "monthly">("weekly");
  const reportQuery = useReport(period);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        {periods.map((item) => (
          <button
            key={item.value}
            type="button"
            onClick={() => setPeriod(item.value)}
            className="rounded-full px-4 py-2 text-sm font-semibold"
            style={{
              background: period === item.value ? "rgba(255,255,255,0.15)" : "transparent",
              border: period === item.value ? "1px solid rgba(255,255,255,0.4)" : "1px solid rgba(255,255,255,0.2)",
            }}
          >
            {item.label}
          </button>
        ))}
      </div>
      {reportQuery.isLoading && <p className="text-sm text-[var(--text-secondary)]">리포트를 불러오는 중입니다…</p>}
      {reportQuery.error && <p className="text-sm text-red-300">리포트 데이터를 가져오지 못했습니다.</p>}
      {reportQuery.data && <ReportSummaryPanel report={reportQuery.data} />}
    </div>
  );
};
