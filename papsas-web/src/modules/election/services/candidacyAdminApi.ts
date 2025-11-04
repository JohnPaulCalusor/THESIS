import { http } from "../../lib/http";

export type CandidacyPostBody =
  | { member_id: number; position_id?: number | null }
  | { email: string; name?: string; position_id?: number | null };

export async function createCandidacy(electionId: number, body: CandidacyPostBody) {
  const { data } = await http.post(`/api/elections/${electionId}/candidacies`, body);
  return data;
}

export async function patchCandidacy(
  electionId: number,
  candidacyId: number,
  body: Partial<{ position_id: number | null; candidacyStatus: boolean; credentials: string }>
) {
  const { data } = await http.patch(`/api/elections/${electionId}/candidacies/${candidacyId}`, body);
  return data;
}

