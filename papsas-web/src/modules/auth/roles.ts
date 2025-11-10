export type AnyUser = {
  id?: number; username?: string; email?: string;
  role?: string | null; groups?: string[];
  is_staff?: boolean; is_superuser?: boolean;
};
const toSet = (arr?: string[]) => new Set((arr||[]).map(s => String(s||"").toLowerCase()));
export function isAdminUser(u?: AnyUser|null): boolean {
  if (!u) return false;
  const g = toSet(u.groups);
  const role = String(u.role||"").toLowerCase();
  return Boolean(u.is_superuser || u.is_staff || role === "admin" || g.has("admin"));
}
