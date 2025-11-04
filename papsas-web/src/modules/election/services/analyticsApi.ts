import { http } from "../../lib/http";
import type { AnalyticsDTO, ExplainDTO } from "../types";

export async function getAnalytics(eid: number) {
  const { data } = await http.get(`/api/elections/${eid}/analytics`);
  return data as AnalyticsDTO;
}

export async function postExplain(eid: number, opts: any = {}) {
  const { data } = await http.post(`/api/elections/${eid}/explain`, opts);
  if (data && typeof data.short === "string" && typeof data.long === "string") return data as ExplainDTO;
  const t = typeof data?.text === "string" ? data.text : "";
  return { short: t, long: t, text: t } as ExplainDTO;
}
