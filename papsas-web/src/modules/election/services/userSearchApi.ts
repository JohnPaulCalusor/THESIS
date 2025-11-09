// >>> PAPSAS v1.3 BEGIN
import { http } from "../../lib/http";

export type UserLite = { id: number; name?: string; email?: string; username?: string };

// Tolerant user search. Primary: GET /users?query=
// If 404/mismatch, return [] so UI can fall back to manual member_id.
export async function searchUsers(query: string): Promise<UserLite[]> {
  const q = (query || "").trim();
  if (!q) return [];
  try {
    const { data } = await http.get("users", { params: { query: q } });
    const arr = Array.isArray(data) ? data : ((data as any)?.results || (data as any)?.items || []);
    return arr.map((u: any) => ({
      id: Number(u.id),
      name: u.name || u.full_name || u.display_name || u.username,
      email: u.email || u.user_email,
      username: u.username,
    }));
  } catch (e: any) {
    const status = e?.response?.status;
    if (status === 404) return [];
    // Be quiet on other errors; caller may show a generic toast
    return [];
  }
}
// <<< PAPSAS v1.3 END
