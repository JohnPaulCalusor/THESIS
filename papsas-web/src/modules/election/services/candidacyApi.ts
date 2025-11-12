import { http } from "../../lib/http";

export type Candidacy = {
  id: number;
  name: string;
  email?: string;
  positionId: number | null;
  positionTitle?: string;
  credentials?: string;
  _status: boolean; // true = enabled/active
};

export type CandidacyCreate = {
  memberId?: number; // existing user id
  name?: string;     // quick-create
  email?: string;    // quick-create
  positionId?: number | null;
  credentials?: string;
  _status?: boolean;
};

function unwrap<T = any>(data: any): T[] {
  if (Array.isArray(data)) return data as T[];
  if (data?.results && Array.isArray(data.results)) return data.results as T[];
  if (data?.items && Array.isArray(data.items)) return data.items as T[];
  return [];
}

function normalize(row: any): Candidacy {
  const id = row.id ?? row.candidacyId ?? row.candidacy_id;
  const positionId = row.positionId ?? row.position_id ?? row.position?.id ?? null;
  const positionTitle =
    row.positionTitle ??
    row.position_title ??
    row.position_name ??
    row.position?.title ??
    (positionId != null ? String(positionId) : undefined);
  const name =
    row.name ??
    row.candidate_name ??
    (([row.first_name, row.last_name].filter(Boolean).join(" ")) || row.candidate?.name || "—");
  const email = row.email ?? row.candidate?.email;
  const credentials = row.credentials ?? row.bio ?? row.platform ?? "";
  return { id, name, email, positionId, positionTitle, credentials, _status } as Candidacy;
}

const base = (electionId: number) => `/api/elections/${electionId}/candidacies`;

// ---- helpers: retry without '_status' if backend rejects it ----
function needsStatusRetry(err: any): boolean {
  const code = err?.response?.data?.code;
  const msg = (err?.response?.data?.message || err?.message || "").toString();
  return (
    code === "VALIDATION_ERROR" &&
    (/unexpected keyword arguments.*_status/i.test(msg) || /got unexpected keyword.*_status/i.test(msg))
  );
}

async function postWithStatusFallback(url: string, body: any) {
  try {
    return await http.post(url, body);
  } catch (err: any) {
    if (("_status" in (body || {})) && needsStatusRetry(err)) {
      const rest = { ...(body || {}) };
      delete rest._status;
      return await http.post(url, rest);
    }
    throw err;
  }
}

async function patchWithStatusFallback(url: string, body: any) {
  try {
    return await http.patch(url, body);
  } catch (err: any) {
    if (("_status" in (body || {})) && needsStatusRetry(err)) {
      const rest = { ...(body || {}) };
      delete rest._status;
      return await http.patch(url, rest);
    }
    throw err;
  }
}

export async function listCandidacies(electionId: number): Promise<Candidacy[]> {
  const { data } = await http.get(base(electionId));
  return unwrap<any>(data).map(normalize);
}

export async function createCandidacy(
  electionId: number,
  payload: CandidacyCreate
): Promise<Candidacy> {
  if (payload.memberId) {
    const body = {
      candidateUserId: payload.memberId,
      positionId: payload.positionId ?? null,
      credentials: payload.credentials ?? "",
      _status: payload._status ?? true,
    };
    const { data } = await postWithStatusFallback(base(electionId), body);
    return normalize(data);
  } else {
    const body = {
      name: payload.name ?? "",
      email: payload.email ?? "",
      positionId: payload.positionId ?? null,
      credentials: payload.credentials ?? "",
      _status: payload._status ?? true,
    };
    try {
      const { data } = await postWithStatusFallback(`${base(electionId)}/quick`, body);
      if (data?.candidacy_id) {
        const list = await listCandidacies(electionId);
        const found = list.find((x) => x.id === data.candidacy_id);
        if (found) return found;
      }
      return normalize(data);
    } catch (err: any) {
      const q = payload.email || payload.name || "";
      const matches = await searchMembers(q);
      const exact = matches.find(
        (m) => m.email && payload.email && m.email.toLowerCase() === payload.email.toLowerCase()
      );
      const candidate = exact || matches[0];
      if (candidate?.id) {
        const linkBody = {
          candidateUserId: candidate.id,
          positionId: payload.positionId ?? null,
          credentials: payload.credentials ?? "",
          _status: payload._status ?? true,
        };
        const { data } = await postWithStatusFallback(base(electionId), linkBody);
        return normalize(data);
      }
      throw err;
    }
  }
}

export async function updateCandidacy(
  _electionId: number,
  id: number,
  patch: CandidacyCreate
): Promise<Candidacy> {
  const body: any = {};
  if (patch.memberId !== undefined) body.candidateUserId = patch.memberId;
  if (patch.positionId !== undefined) body.positionId = patch.positionId;
  if (patch.credentials !== undefined) body.credentials = patch.credentials;
  if (patch.name !== undefined) body.name = patch.name;
  if (patch.email !== undefined) body.email = patch.email;
  const { data } = await patchWithStatusFallback(`/api/candidacies/${id}`, body);
  return normalize(data);
}

export async function deleteCandidacy(_electionId: number, id: number): Promise<void> {
  await http.delete(`/api/candidacies/${id}`);
}

// Optional: member search
export type Member = { id: number; name?: string; email?: string };
export async function searchMembers(q: string): Promise<Member[]> {
  if (!q?.trim()) return [];
  const results: Member[] = [];
  const enc = encodeURIComponent(q);
  const tryEndpoint = async (url: string) => {
    try {
      const { data } = await http.get(url);
      const arr = Array.isArray(data) ? data : (data?.results || data?.items || []);
      for (const m of arr) {
        results.push({ id: m.id, name: m.name || m.full_name || m.username || m.display_name, email: m.email || m.user_email });
      }
    } catch {
      /* ignore */
    }
  };
  await Promise.all([
    tryEndpoint(`/api/users?search=${enc}`),
    tryEndpoint(`/api/users?query=${enc}`),
    tryEndpoint(`/api/users/search?q=${enc}`),
    tryEndpoint(`/api/members?search=${enc}`),
    tryEndpoint(`/api/members?query=${enc}`),
    tryEndpoint(`/api/members/search?q=${enc}`),
    tryEndpoint(`/api/auth/users?search=${enc}`),
  ]);
  const seen = new Set<number>();
  return results.filter(m => (typeof m.id === "number" && !seen.has(m.id) && seen.add(m.id)));
}
