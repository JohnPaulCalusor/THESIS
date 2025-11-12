// src/modules/auth/AuthProvider.tsx
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { http, setTokens, clearTokens, hasAccess, initTokensFromStorage } from "../lib/http";
import type { Me } from "./roles";

type AuthCtx = {
  isAuthed: boolean;
  me: Me | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  intendedPath: string | null;
  setIntendedPath: (p: string | null) => void;
};
const Ctx = createContext<AuthCtx>(null!);

async function fetchMe(): Promise<Me | null> {
  try {
    const { data } = await http.get("/api/auth/me");
    if (!data) return null;
    const groups = Array.isArray(data.groups) ? data.groups.map(String) : [];
    return {
      username: String(data.username ?? ""),
      email: String(data.email ?? ""),
      first_name: String(data.first_name ?? ""),
      last_name: String(data.last_name ?? ""),
      groups,
    };
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthed, setIsAuthed] = useState(false);
  const [me, setMe] = useState<Me | null>(null);
  const [loading, setLoading] = useState(true);
  const [intendedPath, setIntendedPath] = useState<string | null>(null);

  useEffect(() => {
    initTokensFromStorage();
    (async () => {
      if (!hasAccess()) {
        setIsAuthed(false);
        setMe(null);
        setLoading(false);
        return;
      }
      try {
        const freshMe = await fetchMe();
        setMe(freshMe);
        setIsAuthed(Boolean(freshMe));
      } catch {
        setIsAuthed(false);
        setMe(null);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  async function login(username: string, password: string) {
    const { data } = await http.post("/api/auth/login/", { username, password });
    setTokens(data.access, data.refresh);
    const freshMe = await fetchMe();
    setMe(freshMe);
    setIsAuthed(Boolean(freshMe));
  }

  function logout() {
    clearTokens();
    setIsAuthed(false);
    setMe(null);
    window.location.assign("/login");
  }

  return (
    <Ctx.Provider value={{ isAuthed, me, loading, login, logout, intendedPath, setIntendedPath }}>
      {children}
    </Ctx.Provider>
  );
}

export const useAuth = () => useContext(Ctx);
