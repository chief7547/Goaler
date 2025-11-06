import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api/client";
import type { ReportSummary } from "../lib/api/types";

type Period = "weekly" | "monthly";

export function useReport(period: Period) {
  return useQuery<ReportSummary>({
    queryKey: ["reports", period],
    queryFn: () => api.getReports(period),
  });
}
