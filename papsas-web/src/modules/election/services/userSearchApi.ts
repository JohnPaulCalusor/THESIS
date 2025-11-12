// >>> PAPSAS v1.3 BEGIN
import { http } from "../../lib/http";
import type { AxiosError } from "axios";

export type UserLite = { id: number; name?: string; email?: string; username?: string };

// Tolerant user search. Primary: GET /users?query=
// If 404/mismatch, return [] so UI can fall back to manual member_id.
export async function searchUsers(query: string): Promise<UserLite[]> {
  const q = (query || "").trim();
  if (!q) return [];
  try {
    const { data } = await http.get("users", { params: { query: q } });
    const arr: unknown[] = Array.isArray(data)
      ? data
      : Array.isArray((data as Record<string, unknown>)?.results)
        ? ((data as Record<string, unknown>).results as unknown[])
        : Array.isArray((data as Record<string, unknown>)?.items)
          ? ((data as Record<string, unknown>).items as unknown[])
          : [];
    return arr.map((u) => ({
      id: Number((u as Record<string, unknown>).id),
      name:
        (u as Record<string, unknown>).name ||
        (u as Record<string, unknown>).full_name ||
        (u as Record<string, unknown>).display_name ||
        (u as Record<string, unknown>).username,
      email: (u as Record<string, unknown>).email || (u as Record<string, unknown>).user_email,
      username: (u as Record<string, unknown>).username,
    }));
  } catch (e: unknown) {
    const ax = e as AxiosError<unknown>;
    const status = ax.response?.status;
    if (status === 404) return [];
    return [];
  }
}
// <<< PAPSAS v1.3 END
