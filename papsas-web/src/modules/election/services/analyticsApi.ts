import { http } from "../../lib/http";
import type { AnalyticsDTO, ExplainDTO } from "../types";

type RawAnalyticsPosition = {
  id?: number;
  positionId?: number;
  position_id?: number;
  title?: string;
  positionTitle?: string;
  position_title?: string;
  totals?: RawAnalyticsCandidate[];
  candidates?: RawAnalyticsCandidate[];
};
type RawAnalyticsCandidate = {
  candidacy_id?: number;
  candidateId?: number;
  candidate_id?: number;
  candidate_name?: string;
  name?: string;
  count?: number;
  votes?: number;
  share?: number;
  position_id?: number;
  positionId?: number;
  position_title?: string;
};
type RawAnalytics = {
  election?: { id: number; title?: string };
  summary?: { total_votes?: number };
  total_votes?: number;
  ballots_cast?: number;
  selections_total?: number;
  meta?: { totalVotes?: number };
  positions?: RawAnalyticsPosition[];
  by_position?: RawAnalyticsPosition[];
  by_candidate?: RawAnalyticsCandidate[];
};

type NormalizedCandidate = {
  candidate_id: number;
  name: string;
  count: number;
  share?: number;
};

function normalizeCandidateTotals(list?: RawAnalyticsCandidate[]): NormalizedCandidate[] {
  return (list ?? []).map((cand) => ({
    candidate_id: Number(cand.candidacy_id ?? cand.candidate_id ?? cand.candidateId ?? 0),
    name:
      cand.candidate_name ??
      cand.name ??
      `#${cand.candidacy_id ?? cand.candidate_id ?? cand.candidateId ?? ""}`,
    count: Number(cand.count ?? cand.votes ?? 0),
    share: typeof cand.share === "number" ? cand.share : undefined,
  }));
}

function finalizeTotals(totals: NormalizedCandidate[]): AnalyticsDTO["positions"][number]["totals"] {
  const sum = totals.reduce((acc, t) => acc + t.count, 0);
  return totals
    .map((t) => ({
      ...t,
      share:
        typeof t.share === "number"
          ? t.share
          : sum > 0
          ? Number((t.count / sum).toFixed(3))
          : 0,
    }))
    .sort((a, b) => b.count - a.count);
}

function normalizeAnalytics(raw: RawAnalytics, electionId: number): AnalyticsDTO {
  const positionsById = new Map<number, { id: number; title: string; totals: NormalizedCandidate[] }>();

  const ensurePosition = (positionId: number, title?: string) => {
    const id = positionId || 0;
    let entry = positionsById.get(id);
    if (!entry) {
      entry = { id, title: title ?? `Position #${id}`, totals: [] };
      positionsById.set(id, entry);
    } else if (title) {
      entry.title = title;
    }
    return entry;
  };

  if (Array.isArray(raw.positions) && raw.positions.length) {
    raw.positions.forEach((pos) => {
      const positionId = Number(pos.id ?? pos.position_id ?? pos.positionId ?? 0);
      const title =
        pos.title ??
        pos.position_title ??
        pos.positionTitle ??
        `Position #${positionId || 0}`;
      const totals = normalizeCandidateTotals(pos.totals ?? pos.candidates);
      const entry = ensurePosition(positionId, title);
      entry.totals = totals;
    });
  } else {
    (raw.by_position ?? []).forEach((pos) => {
      const positionId = Number(pos.position_id ?? pos.positionId ?? pos.id ?? 0);
      const title =
        pos.position_title ??
        pos.positionTitle ??
        pos.title ??
        `Position #${positionId || 0}`;
      ensurePosition(positionId, title);
    });
    (raw.by_candidate ?? []).forEach((cand) => {
      const positionId = Number(cand.position_id ?? cand.positionId ?? 0);
      const entry = ensurePosition(positionId);
      entry.totals.push(...normalizeCandidateTotals([cand]));
    });
  }

  const positions = Array.from(positionsById.values()).map((entry) => ({
    id: entry.id,
    title: entry.title,
    totals: finalizeTotals(entry.totals),
  }));

  const totalVotes =
    raw.meta?.totalVotes ??
    raw.summary?.total_votes ??
    raw.total_votes ??
    raw.ballots_cast ??
    positions.reduce((acc, pos) => acc + pos.totals.reduce((sum, t) => sum + t.count, 0), 0);

  const electionPayload = raw.election ?? { id: electionId, title: undefined };
  return {
    election: electionPayload,
    positions,
    meta: {
      totalVotes,
    },
  };
}

export async function getAnalytics(eid: number) {
  const { data } = await http.get<RawAnalytics>(`elections/${eid}/analytics`);
  return normalizeAnalytics(data, eid);
}

export async function postExplain(
  eid: number,
  opts: Record<string, unknown> = {}
) {
  const { data } = await http.post(`elections/${eid}/explain`, opts);
  if (data && typeof data.short === "string" && typeof data.long === "string")
    return data as ExplainDTO;
  const t = typeof data?.text === "string" ? data.text : "";
  return { short: t, long: t, text: t } as ExplainDTO;
}
