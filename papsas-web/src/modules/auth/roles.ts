// Role helpers (works with legacy "me" and new "user" shapes)

export type Me = {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  groups: string[];
};

export function hasGroup(me: Me | null | undefined, group: string): boolean {
  const want = String(group || "").toLowerCase();
  const gs = (me?.groups || []).map(s => String(s || "").toLowerCase());
  return gs.includes(want);
}

export const isAdmin   = (me: Me | null | undefined) => hasGroup(me, "admin");
export const isOfficer = (me: Me | null | undefined) => hasGroup(me, "officer");

// New AuthProvider "user" shape
export type AnyUser = {
  role?: string | null;
  groups?: string[];
  is_staff?: boolean;
  is_superuser?: boolean;
};

export function isAdminUser(u?: AnyUser | null): boolean {
  if (!u) return false;
  const gs = new Set((u.groups || []).map(s => String(s || "").toLowerCase()));
  const role = String(u.role || "").toLowerCase();
  return Boolean(u.is_superuser || u.is_staff || role === "admin" || gs.has("admin"));
}
