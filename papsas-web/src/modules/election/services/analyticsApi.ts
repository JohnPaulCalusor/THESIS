import { http } from "../../lib/http";
import type { AxiosError } from "axios";
import type { AnalyticsDTO, ExplainDTO } from "../types";

export async function getAnalytics(eid: number) {
  try {
    const { data } = await http.get<AnalyticsDTO>(`elections/${eid}/analytics`);
    return data;
  } catch (err: unknown) {
    const ax = err as AxiosError<unknown>;
    throw ax;
  }
}

export async function postExplain(eid: number, opts: Record<string, unknown> = {}) {
  try {
    const { data } = await http.post<ExplainDTO>(`elections/${eid}/explain`, opts);
    if (data && typeof data.short === "string" && typeof data.long === "string") return data;
    const t = typeof data?.text === "string" ? data.text : "";
    return { short: t, long: t, text: t };
  } catch (err: unknown) {
    const ax = err as AxiosError<unknown>;
    throw ax;
  }
}
