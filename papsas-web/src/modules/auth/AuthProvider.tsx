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

async function tryGet<T=any>(url: string): Promise<T | null> {
  try {
    const { data } = await http.get(url);
    return data as T;
  } catch { return null; }
}

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [intendedPath, setIntendedPath] = useState<string | null>(null);

  const whoAmI = useCallback(async () => {
    // Try a few common endpoints, first success wins
    const urls = ["users/me", "auth/me", "me", "auth/user", "auth/profile"];
    for (const u of urls) {
      const data = await tryGet<any>(u);
      if (data) {
        // normalize some common shapes
        const norm: User = {
          id: data.id ?? data.user_id ?? data.pk,
          username: data.username ?? data.user?.username,
          email: data.email ?? data.user?.email,
          role: data.role ?? data.user?.role ?? null,
          groups: data.groups ?? data.user?.groups ?? [],
          is_staff: data.is_staff ?? data.user?.is_staff,
          is_superuser: data.is_superuser ?? data.user?.is_superuser,
        };
        setUser(norm);
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
      const access = data?.access ?? data?.token ?? data?.access_token;
      const refresh = data?.refresh ?? data?.refresh_token;
      if (!access) throw new Error("Login did not return access token");
      setTokens({ access, refresh });
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
