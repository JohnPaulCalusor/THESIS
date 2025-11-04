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
