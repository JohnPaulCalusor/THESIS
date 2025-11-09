import { http } from "../../lib/http";

export type CandidacyPostBody =
  | { member_id: number; position_id?: number | null }
  | { email: string; name?: string; position_id?: number | null };

export async function createCandidacy(electionId: number, body: CandidacyPostBody) {
  const { data } = await http.post(`elections/${electionId}/candidacies`, body);
  return data;
}

export async function patchCandidacy(
  electionId: number,
  candidacyId: number,
  body: Partial<{ position_id: number | null; candidacyStatus: boolean; credentials: string }>
) {
  const { data } = await http.patch(`elections/${electionId}/candidacies/${candidacyId}`, body);
  return data;
}

// >>> PAPSAS v1.3 BEGIN
// Ensure admin can list candidacies for the current election.
// Kept narrow and tolerant to backend payload variance.
export async function listCandidacies(electionId: number) {
  const { data } = await http.get(`elections/${electionId}/candidacies`);
  // Return the raw list; normalization happens at the consumer layer if needed
  if (Array.isArray(data)) return data;
  if (Array.isArray((data as any)?.results)) return (data as any).results;
  if (Array.isArray((data as any)?.items)) return (data as any).items;
  return [] as any[];
}
// Acceptance: Admin duplicate candidacy -> 409 toast "Already exists" is handled by caller via toast.apiError
// <<< PAPSAS v1.3 END
