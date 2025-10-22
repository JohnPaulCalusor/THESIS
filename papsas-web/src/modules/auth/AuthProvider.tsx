import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { http, setTokens, clearTokens, hasAccess, initTokensFromStorage } from "../lib/http";

type AuthCtx = {
  isAuthed: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  intendedPath: string | null;
  setIntendedPath: (p: string | null) => void;
};
const Ctx = createContext<AuthCtx>(null!);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthed, setIsAuthed] = useState(false);
  const [intendedPath, setIntendedPath] = useState<string | null>(null);

  useEffect(() => {
    initTokensFromStorage();          // <-- load tokens from localStorage
    if (hasAccess()) setIsAuthed(true);
  }, []);

  async function login(username: string, password: string) {
    const { data } = await http.post("/api/auth/login/", { username, password });
    setTokens(data.access, data.refresh);
    setIsAuthed(true);
  }
  function logout() { clearTokens(); setIsAuthed(false); }

  return (
    <Ctx.Provider value={{ isAuthed, login, logout, intendedPath, setIntendedPath }}>
      {children}
    </Ctx.Provider>
  );
}
export const useAuth = () => useContext(Ctx);
