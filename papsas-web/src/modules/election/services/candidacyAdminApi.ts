import { AxiosError } from "axios";
import { http } from "../../lib/http";

type Json = Record<string, unknown>;

export type CandidacyPostBody =
  | { member_id: number; position_id?: number | null }
  | { email: string; name?: string; position_id?: number | null };

export type CandidacyAdminDTO = {
  id: number;
  position_id: number | null;
  candidate_id?: number;
  candidate_name?: string;
  position_title?: string;
  status?: string;
  note?: string;
};

export async function createCandidacy(electionId: number, body: CandidacyPostBody) {
  const { data } = await http.post<CandidacyAdminDTO>(`elections/${electionId}/candidacies`, body);
  return data;
}

export async function patchCandidacy(
  electionId: number,
  candidacyId: number,
  body: Partial<CandidacyAdminDTO>
) {
  const { data } = await http.patch<CandidacyAdminDTO>(`elections/${electionId}/candidacies/${candidacyId}`, body);
  return data;
}

// >>> PAPSAS v1.3 BEGIN
// Ensure admin can list candidacies for the current election.
// Kept narrow and tolerant to backend payload variance.
export async function listCandidacies(electionId: number): Promise<CandidacyAdminDTO[]> {
  try {
    const { data } = await http.get<CandidacyAdminDTO[]>(`elections/${electionId}/candidacies`);
    if (Array.isArray(data)) return data;
    if (Array.isArray((data as Json)?.results)) return (data as Json).results as CandidacyAdminDTO[];
    if (Array.isArray((data as Json)?.items)) return (data as Json).items as CandidacyAdminDTO[];
    return [];
  } catch (e: unknown) {
    const ax = e as AxiosError<unknown>;
    throw ax;
  }
}
// Acceptance: Admin duplicate candidacy -> 409 toast "Already exists" is handled by caller via toast.apiError
// <<< PAPSAS v1.3 END
