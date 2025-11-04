import { http } from "../../lib/http";
export type Position = { id: number; title: string; enabled?: boolean; sort?: number };

function unwrap<T = any>(data: any): T[] {
  if (Array.isArray(data)) return data as T[];
  if (data?.results && Array.isArray(data.results)) return data.results as T[];
  if (data?.items && Array.isArray(data.items)) return data.items as T[];
  return [];
}

export async function listPositions(electionId: number): Promise<Position[]> {
  try {
    const { data } = await http.get(`/api/elections/${electionId}/positions`);
    const rows = unwrap<Position>(data);
    return rows.map((r: any) => ({
      id: r.id,
      title: r.title ?? r.name,
      enabled: r.enabled ?? true,
      sort: r.sort ?? 0,
    }));
  } catch {}
  try {
    const { data } = await http.get(`/api/positions`, { params: { election: electionId } });
    const rows = unwrap<Position>(data);
    return rows.map((r: any) => ({ id: r.id, title: r.title ?? r.name, enabled: r.enabled ?? true, sort: r.sort ?? 0 }));
  } catch {}

  // Fallback: derive from candidacies
  try {
    const { data } = await http.get(`/api/elections/${electionId}/candidacies`);
    const rows = unwrap<any>(data);
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
  const { data } = await http.post(`/api/elections/${electionId}/positions`, body);
  return { id: data.id, title: data.title, enabled: data.enabled, sort: data.sort };
}

export async function updatePosition(id: number, p: Partial<Position>): Promise<Position> {
  const body: any = {};
  if (p.title !== undefined) body.title = p.title;
  if (p.enabled !== undefined) body.enabled = p.enabled;
  if (p.sort !== undefined) body.sort = p.sort;
  const { data } = await http.patch(`/api/positions/${id}`, body);
  return { id: data.id, title: data.title, enabled: data.enabled, sort: data.sort };
}

export async function deletePosition(id: number): Promise<void> {
  await http.delete(`/api/positions/${id}`);
}

// >>> PAPSAS v1.3 BEGIN
// Add election-scoped helpers; do not alter existing axios client behavior.
export async function getCurrent() {
  const { data } = await http.get(`/api/elections/current`);
  return data as { id: number; title?: string };
}

export async function getBallot(eid: number) {
  const { data } = await http.get(`/api/elections/${eid}/ballot`);
  return data as any;
}

export async function postVote(eid: number, body: { candidacyId: number }) {
  const { data } = await http.post(`/api/elections/${eid}/vote`, body);
  return data as any;
}

export async function getResults(eid: number) {
  const { data } = await http.get(`/api/elections/${eid}/results`);
  return data as any;
}

// Soft re-export style to keep call-sites stable if they prefer electionApi.
export async function getAnalytics(eid: number) {
  const { data } = await http.get(`/api/elections/${eid}/analytics`);
  return data as any;
}

export async function postExplain(eid: number, opts: any = {}) {
  const { data } = await http.post(`/api/elections/${eid}/explain`, opts);
  return data as any;
}
// <<< PAPSAS v1.3 END
