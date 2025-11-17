// >>> PAPSAS v1.3 BEGIN
import { http } from "../../lib/http";
import type { AxiosError } from "axios";

type Json = Record<string, unknown>;
const asRecord = (value: unknown): Json | null =>
  typeof value === "object" && value !== null ? (value as Json) : null;
const asString = (value: unknown): string | undefined =>
  typeof value === "string" ? value : undefined;

export type UserLite = { id: number; name?: string; email?: string; username?: string };

// Tolerant user search. Primary: GET /users?query=
// If 404/mismatch, return [] so UI can fall back to manual member_id.
export async function searchUsers(query: string): Promise<UserLite[]> {
  const q = (query || "").trim();
  if (!q) return [];
  try {
    const { data } = await http.get("users", { params: { query: q } });
    const arr: unknown[] =
      Array.isArray(data)
        ? data
        : Array.isArray((data as Json)?.results)
          ? (data as Json).results as unknown[]
          : Array.isArray((data as Json)?.items)
            ? (data as Json).items as unknown[]
            : [];
    return arr
      .map((u) => {
        const record = asRecord(u);
        const idValue = record?.id ?? record?.user_id ?? record?.pk;
        return {
          id: Number(idValue ?? 0),
          name:
            asString(record?.name) ??
            asString(record?.full_name) ??
            asString(record?.display_name) ??
            asString(record?.username),
          email: asString(record?.email) ?? asString(record?.user_email),
          username: asString(record?.username),
        };
      })
      .filter((user) => Number.isFinite(user.id));
  } catch (e: unknown) {
    const ax = e as AxiosError<unknown>;
    const status = ax.response?.status;
    if (status === 404) return [];
    return [];
  }
}
// <<< PAPSAS v1.3 END
