// src/modules/auth/roles.ts
export type Me = {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  groups: string[];
};

export function hasGroup(me: Me | null | undefined, group: string) {
  return Boolean(me?.groups?.includes(group));
}

export const isAdmin = (me: Me | null | undefined) => hasGroup(me, "admin");
export const isOfficer = (me: Me | null | undefined) => hasGroup(me, "officer");
