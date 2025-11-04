// src/modules/auth/AuthProvider.tsx
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { http, setTokens, clearTokens, hasAccess, initTokensFromStorage } from "../lib/http";

type User = { id: number; username: string; email?: string; is_staff?: boolean; groups?: string[]; role?: string };
type AuthCtx = {
  isAuthed: boolean;
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  intendedPath: string | null;
  setIntendedPath: (p: string | null) => void;
};
const Ctx = createContext<AuthCtx>(null!);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthed, setIsAuthed] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [intendedPath, setIntendedPath] = useState<string | null>(null);

  async function whoAmI(): Promise<User | null> {
    const candidates = [
      "/api/auth/me",
      "/api/users/me",
      "/api/auth/user",
      "/api/auth/profile",
      "/api/me",
    ];
    for (const url of candidates) {
      try {
        const { data } = await http.get(url);
        if (data) return data as User;
      } catch {
        // try next
      }
    }
    // Fallback: decode token from our LS_KEY store
    try {
      const raw = localStorage.getItem("papsas.auth");
      const access = raw ? (JSON.parse(raw)?.access as string | undefined) : undefined;
      if (!access) return null;
      const [, payload] = access.split(".");
      const json = JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")));
      const uid = json?.user_id || json?.uid || json?.sub;
      const username = json?.username || undefined;
      if (uid) {
        const userTry = [
          `/api/users/${uid}`,
          `/api/auth/users/${uid}`,
          `/api/accounts/${uid}`,
        ];
        for (const url of userTry) {
          try {
            const { data } = await http.get(url);
            if (data) return data as User;
          } catch {}
        }
        return { id: Number(uid), username: username || "unknown" } as User;
      }
    } catch {
      // ignore
    }
    return null;
  }

  useEffect(() => {
    initTokensFromStorage();              // load tokens if present
    (async () => {
      try {
        if (hasAccess()) {
          setIsAuthed(true);
          const me = await whoAmI();
          setUser(me);
        } else {
          setIsAuthed(false);
          setUser(null);
        }
      } catch {
        setIsAuthed(false);
        setUser(null);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  async function login(username: string, password: string) {
    const { data } = await http.post("/api/auth/login/", { username, password });
    setTokens(data.access, data.refresh); // persist both tokens
    setIsAuthed(true);
    try {
      const me = await whoAmI();
      setUser(me);
    } catch {
      setUser(null);
    }
  }

  function logout() {
    clearTokens();
    setIsAuthed(false);
    setUser(null);
    // simplest path reset
    window.location.assign("/login");
  }

  return (
    <Ctx.Provider value={{ isAuthed, user, loading, login, logout, intendedPath, setIntendedPath }}>
      {children}
    </Ctx.Provider>
  );
}
export const useAuth = () => useContext(Ctx);
