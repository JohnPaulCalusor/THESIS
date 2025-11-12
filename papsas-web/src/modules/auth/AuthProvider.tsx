import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import http, { getTokens, setTokens, clearTokens } from "../lib/http";

export type User = {
  id?: number;
  username?: string;
  email?: string;
  role?: string | null;
  groups?: string[];
  is_staff?: boolean;
  is_superuser?: boolean;
};

type AuthCtx = {
  user: User | null;
  loading: boolean;
  intendedPath: string | null;
  setIntendedPath: (p: string | null) => void;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
};

const Ctx = createContext<AuthCtx | null>(null);
export function useAuth(): AuthCtx {
  const v = useContext(Ctx);
  if (!v) throw new Error("AuthProvider missing");
  return v;
}

async function tryGet<T = unknown>(url: string): Promise<T | null> {
  try {
    const { data } = await http.get(url);
    return data as T;
  } catch {
    return null;
  }
}

type Loose = Record<string, unknown>;
function normalizeUser(data: unknown): User {
  const raw = (data ?? {}) as Loose & { user?: Loose };

  const userObj = (typeof raw.user === "object" && raw.user !== null) ? (raw.user as Loose) : undefined;

  const id =
    (typeof raw.id === "number" ? raw.id : undefined) ??
    (typeof raw["user_id"] === "number" ? (raw["user_id"] as number) : undefined) ??
    (typeof raw["pk"] === "number" ? (raw["pk"] as number) : undefined) ??
    (typeof userObj?.id === "number" ? (userObj.id as number) : undefined);

  const username =
    (typeof raw.username === "string" ? raw.username : undefined) ??
    (typeof userObj?.username === "string" ? (userObj.username as string) : undefined);

  const email =
    (typeof raw.email === "string" ? raw.email : undefined) ??
    (typeof userObj?.email === "string" ? (userObj.email as string) : undefined);

  const roleVal =
    (typeof raw.role === "string" ? raw.role : undefined) ??
    (typeof userObj?.role === "string" ? (userObj.role as string) : undefined) ??
    null;

  const groupsVal: string[] =
    Array.isArray(raw.groups) ? (raw.groups.filter(x => typeof x === "string") as string[]) :
    Array.isArray(userObj?.groups) ? ((userObj!.groups as unknown[]).filter(x => typeof x === "string") as string[]) :
    [];

  const is_staff =
    typeof raw["is_staff"] === "boolean" ? (raw["is_staff"] as boolean) :
    (typeof userObj?.["is_staff"] === "boolean" ? (userObj!["is_staff"] as boolean) : undefined);

  const is_superuser =
    typeof raw["is_superuser"] === "boolean" ? (raw["is_superuser"] as boolean) :
    (typeof userObj?.["is_superuser"] === "boolean" ? (userObj!["is_superuser"] as boolean) : undefined);

  return { id, username, email, role: roleVal, groups: groupsVal, is_staff, is_superuser };
}

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [intendedPath, setIntendedPath] = useState<string | null>(null);

  const whoAmI = useCallback(async () => {
    const urls = ["users/me", "auth/me", "me", "auth/user", "auth/profile"];
    for (const u of urls) {
      const data = await tryGet<unknown>(u);
      if (data) {
        setUser(normalizeUser(data));
        return true;
      }
    }
    setUser(null);
    return false;
  }, []);

  useEffect(() => {
    (async () => {
      const t = getTokens();
      if (t.access) {
        await whoAmI();
      } else {
        setUser(null);
      }
      setLoading(false);
    })();
  }, [whoAmI]);

  const login = useCallback(async (username: string, password: string) => {
    setLoading(true);
    try {
      const { data } = await http.post("auth/login", { username, password });
      const access = (data as Loose)?.["access"] ?? (data as Loose)?.["token"] ?? (data as Loose)?.["access_token"];
      const refresh = (data as Loose)?.["refresh"] ?? (data as Loose)?.["refresh_token"];
      if (!access || typeof access !== "string") throw new Error("Login did not return access token");
      setTokens({ access: String(access), refresh: typeof refresh === "string" ? refresh : undefined });
      await whoAmI();
    } finally {
      setLoading(false);
    }
  }, [whoAmI]);

  const logout = useCallback(() => {
    clearTokens();
    setUser(null);
  }, []);

  const value = useMemo<AuthCtx>(() => ({
    user, loading, intendedPath, setIntendedPath, login, logout
  }), [user, loading, intendedPath, login, logout]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}
