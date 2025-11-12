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
  name?: string; // quick-create
  email?: string; // quick-create
  positionId?: number | null;
  credentials?: string;
  _status?: boolean;
};

export type CandidacyDTO = {
  id: number;
  position_id: number | null;
  candidate_id?: number;
  candidate_name?: string;
  position_title?: string;
  status?: string;
  email?: string;
};

type Json = Record<string, unknown>;

function unwrap<T>(data: unknown): T[] {
  if (Array.isArray(data)) return data as T[];
  if (typeof data === "object" && data !== null) {
    const obj = data as Json;
    if (Array.isArray(obj.results)) return obj.results as T[];
    if (Array.isArray(obj.items)) return obj.items as T[];
  }
  return [];
}

function normalize(row: Json): Candidacy {
  const id = (typeof row.id === "number" ? row.id : undefined) ??
    (typeof row.candidacyId === "number" ? row.candidacyId : undefined) ??
    (typeof row.candidacy_id === "number" ? row.candidacy_id : undefined) ??
    (typeof row._id === "number" ? row._id : undefined);
  const positionId = (typeof row.positionId === "number" ? row.positionId : undefined) ??
    (typeof row.position_id === "number" ? row.position_id : undefined) ??
    (typeof row.position === "object" && row.position !== null && typeof (row.position as Json).id === "number" ? (row.position as Json).id : null) ??
    null;
  const positionTitle =
    typeof row.positionTitle === "string" ? row.positionTitle :
    typeof row.position_title === "string" ? row.position_title :
    typeof row.position?.title === "string" ? (row.position as Json).title :
    (positionId != null ? String(positionId) : undefined);
  const name =
    typeof row.name === "string" ? row.name :
    typeof row.candidate_name === "string" ? row.candidate_name :
    ((Array.isArray(row.first_name) ? row.first_name : [row.first_name]).filter(Boolean).join(" ") ||
      typeof row.candidate?.name === "string" ? (row.candidate as Json).name as string : "-");
  const email = typeof row.email === "string" ? row.email :
    typeof row.candidate?.email === "string" ? (row.candidate as Json).email : undefined;
  const credentials = typeof row.credentials === "string" ? row.credentials :
    typeof row.bio === "string" ? row.bio :
    typeof row.platform === "string" ? row.platform : "";
  return { id: id ?? 0, name, email, positionId, positionTitle, credentials, _status: Boolean(row._status ?? row.status ?? true) };
}

const base = (electionId: number) => `elections/${electionId}/candidacies`;

// ---- helpers: retry without '_status' if backend rejects it ----
function needsStatusRetry(err: unknown): boolean {
  const ax = err as { response?: { data?: Json }; message?: string };
  const code = ax.response?.data?.code;
  const msg = (ax.response?.data?.message || ax.message || "").toString();
  return (
    code === "VALIDATION_ERROR" &&
    (/unexpected keyword arguments.*_status/i.test(msg) || /got unexpected keyword.*_status/i.test(msg))
  );
}

async function postWithStatusFallback(url: string, body: Record<string, unknown>) {
  try {
    return await http.post(url, body);
  } catch (err: unknown) {
    if (("_status" in body) && needsStatusRetry(err)) {
      const rest = { ...body };
      delete rest._status;
      return await http.post(url, rest);
    }
    throw err;
  }
}

async function patchWithStatusFallback(url: string, body: Record<string, unknown>) {
  try {
    return await http.patch(url, body);
  } catch (err: unknown) {
    if (("_status" in body) && needsStatusRetry(err)) {
      const rest = { ...body };
      delete rest._status;
      return await http.patch(url, rest);
    }
    throw err;
  }
}

export async function listCandidacies(electionId: number): Promise<Candidacy[]> {
  const { data } = await http.get<CandidacyDTO[]>(base(electionId));
  const arr = unwrap<Json>(data);
  if (arr.length) return arr.map((row) => normalize(row));
  const also = unwrap<Json>(data);
  return also.map((row) => normalize(row));
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
      return normalize(data as Json);
    } catch (err: unknown) {
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
  const body: Record<string, unknown> = {};
  if (patch.memberId !== undefined) body.candidateUserId = patch.memberId;
  if (patch.positionId !== undefined) body.positionId = patch.positionId;
  if (patch.credentials !== undefined) body.credentials = patch.credentials;
  if (patch.name !== undefined) body.name = patch.name;
  if (patch.email !== undefined) body.email = patch.email;
  const { data } = await patchWithStatusFallback(`candidacies/${id}`, body);
  return normalize(data);
}

export async function deleteCandidacy(_electionId: number, id: number): Promise<void> {
  await http.delete(`candidacies/${id}`);
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
    tryEndpoint(`users?search=${enc}`),
    tryEndpoint(`users?query=${enc}`),
    tryEndpoint(`users/search?q=${enc}`),
    tryEndpoint(`members?search=${enc}`),
    tryEndpoint(`members?query=${enc}`),
    tryEndpoint(`members/search?q=${enc}`),
    tryEndpoint(`auth/users?search=${enc}`),
  ]);
  const seen = new Set<number>();
  return results.filter(m => (typeof m.id === "number" && !seen.has(m.id) && seen.add(m.id)));
}
