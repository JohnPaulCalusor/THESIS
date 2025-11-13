// >>> PAPSAS v1.3 BEGIN
import { http } from "../../lib/http";

export type UserLite = { id: number; name?: string; email?: string; username?: string };

const toStringOrUndefined = (value: unknown): string | undefined => (typeof value === "string" ? value : undefined);

// Tolerant user search. Primary: GET /users?query=
// If 404/mismatch, return [] so UI can fall back to manual member_id.
export async function searchUsers(query: string): Promise<UserLite[]> {
  const q = (query || "").trim();
  if (!q) return [];
  try {
    const { data } = await http.get("users", { params: { query: q } });
    const container = data as { results?: unknown; items?: unknown };
    const arr: unknown[] = Array.isArray(data)
      ? data
      : Array.isArray(container.results)
        ? container.results
        : Array.isArray(container.items)
          ? container.items
          : [];
    return arr
      .filter((item): item is Record<string, unknown> => typeof item === "object" && item !== null)
      .map((u) => ({
        id: Number(u.id),
        name: toStringOrUndefined(u.name) || toStringOrUndefined(u.full_name) || toStringOrUndefined(u.display_name) || toStringOrUndefined(u.username),
        email: toStringOrUndefined(u.email) || toStringOrUndefined(u.user_email),
        username: toStringOrUndefined(u.username),
      }));
  } catch (e: unknown) {
    const status = (e as { response?: { status?: number } })?.response?.status;
    if (status === 404) return [];
    // Be quiet on other errors; caller may show a generic toast
    return [];
  }
}
// <<< PAPSAS v1.3 END
