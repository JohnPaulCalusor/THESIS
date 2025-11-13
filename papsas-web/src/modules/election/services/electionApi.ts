import { http } from "../../lib/http";
export type Position = { id: number; title: string; enabled?: boolean; sort?: number };
type RawPositionRow = {
  position_id?: number;
  positionId?: number;
  position?: { id?: number; title?: string };
  position_title?: string;
  positionTitle?: string;
};

function unwrap<T = unknown>(data: unknown): T[] {
  if (Array.isArray(data)) return data as T[];
  const container = data as { results?: unknown; items?: unknown };
  if (Array.isArray(container.results)) return container.results as T[];
  if (Array.isArray(container.items)) return container.items as T[];
  return [];
}

export async function listPositions(electionId: number): Promise<Position[]> {
  try {
    const { data } = await http.get(`elections/${electionId}/positions`);
    const rows = unwrap<Position>(data);
    return rows.map((r) => ({
      id: r.id,
      title: r.title,
      enabled: r.enabled ?? true,
      sort: r.sort ?? 0,
    }));
  } catch {
    // ignore and try the next endpoint
  }
  try {
    const { data } = await http.get("positions", { params: { election: electionId } });
    const rows = unwrap<Position>(data);
    return rows.map((r) => ({ id: r.id, title: r.title, enabled: r.enabled ?? true, sort: r.sort ?? 0 }));
  } catch {
    // ignore and try candidacy fallback
  }

  // Fallback: derive from candidacies
  try {
    const { data } = await http.get(`elections/${electionId}/candidacies`);
    const rows = unwrap<RawPositionRow>(data);
    const map = new Map<number, string>();
    for (const r of rows) {
      const pid = r.position_id ?? r.positionId ?? r.position?.id;
      const title = r.position_title ?? r.positionTitle ?? r.position?.title;
      if (pid != null && !map.has(pid)) map.set(pid, title ?? String(pid));
    }
    return Array.from(map, ([id, title]) => ({ id, title }));
  } catch {
    return [];
  }
}

export async function createPosition(electionId: number, p: { title: string; enabled?: boolean; sort?: number }): Promise<Position> {
  const body = { title: p.title, enabled: p.enabled ?? true, sort: p.sort ?? 0 };
  const { data } = await http.post(`elections/${electionId}/positions`, body);
  return { id: data.id, title: data.title, enabled: data.enabled, sort: data.sort };
}

export async function updatePosition(id: number, p: Partial<Position>): Promise<Position> {
  const body: Partial<Position> = {};
  if (p.title !== undefined) body.title = p.title;
  if (p.enabled !== undefined) body.enabled = p.enabled;
  if (p.sort !== undefined) body.sort = p.sort;
  const { data } = await http.patch(`positions/${id}`, body);
  return { id: data.id, title: data.title, enabled: data.enabled, sort: data.sort };
}

export async function deletePosition(id: number): Promise<void> {
  await http.delete(`positions/${id}`);
}

// >>> PAPSAS v1.3 BEGIN
// Add election-scoped helpers; do not alter existing axios client behavior.
export async function getCurrent() {
  const { data } = await http.get("elections/current");
  return data as { id: number; title?: string };
}

export async function getBallot(eid: number): Promise<unknown> {
  const { data } = await http.get(`elections/${eid}/ballot`);
  return data;
}

export type VoteChoice = { position_id?: number | null; candidacy_id: number };
export interface VoteRequestPayload {
  positions?: VoteChoice[];
  atLarge?: number[];
}

export async function postVote(eid: number, body: VoteRequestPayload) {
  const { data } = await http.post(`elections/${eid}/vote`, body);
  return data;
}

export async function getResults(eid: number) {
  const { data } = await http.get(`elections/${eid}/results`);
  return data;
}

// Soft re-export style to keep call-sites stable if they prefer electionApi.
export async function getAnalytics(eid: number) {
  const { data } = await http.get(`elections/${eid}/analytics`);
  return data;
}

export async function postExplain(eid: number, opts: Record<string, unknown> = {}) {
  const { data } = await http.post(`elections/${eid}/explain`, opts);
  return data;
}
// <<< PAPSAS v1.3 END
