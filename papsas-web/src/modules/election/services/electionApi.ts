import { http } from "../../lib/http";

export type ElectionDTO = { id: number; title?: string | null };
export type PositionDTO = { id: number; title: string; enabled?: boolean; sort?: number };
export type Position = PositionDTO;
export type VoteChoice = { position_id: number; candidacy_id: number };
export type VoteRequestPayload = { positions: VoteChoice[] } | { atLarge: number[] };
type Json = Record<string, unknown>;

function unwrap<T>(data: unknown): T[] {
  if (Array.isArray(data)) return data as T[];
  if (typeof data === "object" && data !== null) {
    const obj = data as Record<string, unknown>;
    if (Array.isArray(obj.results)) return obj.results as T[];
    if (Array.isArray(obj.items)) return obj.items as T[];
  }
  return [];
}

export async function listPositions(electionId: number): Promise<Position[]> {
  const normalize = (row: PositionDTO | Record<string, unknown>) => ({
    id: (row as Record<string, unknown>).id as number,
    title: (row as Record<string, unknown>).title as string ?? ((row as Record<string, unknown>).name as string) ?? "Unknown",
    enabled: (row as Record<string, unknown>).enabled as boolean | undefined ?? true,
    sort: (row as Record<string, unknown>).sort as number | undefined ?? 0,
  });

  try {
    const { data } = await http.get<unknown>(`elections/${electionId}/positions`);
    const rows = unwrap<PositionDTO>(data);
    if (rows.length) return rows.map(normalize);
  } catch {
    /* noop */
  }

  try {
    const { data } = await http.get<unknown>("positions", { params: { election: electionId } });
    const rows = unwrap<PositionDTO>(data);
    if (rows.length) return rows.map(normalize);
  } catch {
    /* noop */
  }

  try {
    const { data } = await http.get<unknown>(`elections/${electionId}/candidacies`);
    const rows = unwrap<Json>(data);
    const map = new Map<number, string>();
    for (const r of rows) {
      if (typeof r !== "object" || r === null) continue;
      const inner = r as Record<string, unknown>;
      const pid = (inner.position_id as number | undefined) ?? (inner.positionId as number | undefined) ?? ((inner.position as Record<string, unknown>)?.id as number | undefined);
      const title =
        (inner.position_title as string | undefined) ??
        (inner.positionTitle as string | undefined) ??
        ((inner.position as Record<string, unknown>)?.title as string | undefined);
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
  const body: Record<string, unknown> = {};
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
export async function getCurrent(): Promise<ElectionDTO> {
  const { data } = await http.get<ElectionDTO>("elections/current");
  return data;
}

export async function getBallot(eid: number): Promise<unknown> {
  const { data } = await http.get<unknown>(`elections/${eid}/ballot`);
  return data;
}

export async function postVote(eid: number, body: VoteRequestPayload): Promise<unknown> {
  const { data } = await http.post<unknown>(`elections/${eid}/vote`, body);
  return data;
}

export async function getResults(eid: number): Promise<unknown> {
  const { data } = await http.get<unknown>(`elections/${eid}/results`);
  return data;
}

// Soft re-export style to keep call-sites stable if they prefer electionApi.
export async function getAnalytics(eid: number): Promise<unknown> {
  const { data } = await http.get<unknown>(`elections/${eid}/analytics`);
  return data;
}

export async function postExplain(eid: number, opts: Record<string, unknown> = {}): Promise<unknown> {
  const { data } = await http.post<unknown>(`elections/${eid}/explain`, opts);
  return data;
}
// <<< PAPSAS v1.3 END
