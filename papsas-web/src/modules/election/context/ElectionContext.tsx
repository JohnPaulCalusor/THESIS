import React, { createContext, useCallback, useEffect, useMemo, useState } from "react";
import { http } from "../../lib/http";

export type Election = { id: number; title: string };
type Ctx = {
  election: Election | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
};

export const ElectionContext = createContext<Ctx | null>(null);

async function fetchJson<T>(url: string): Promise<T> {
  try {
    const { data } = await http.get(url);
    return data as T;
  } catch (e: any) {
    const status = e?.response?.status;
    const msg = e?.response?.data && typeof e.response.data === "string" ? e.response.data : e?.message;
    const err = new Error(msg || (status ? `HTTP ${status}` : "Request failed"));
    // @ts-expect-error attach status for callers
    err.status = status;
    throw err;
  }
}

export const ElectionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [election, setElection] = useState<Election | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setErr] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setErr(null);
    try {
      const data = await fetchJson<Election>("/api/elections/current");
      setElection({ id: data.id, title: data.title });
    } catch (e: any) {
      if (e?.status === 404) {
        setElection(null); // no active election
      } else {
        setErr(e?.message || "Failed to load current election");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  const value = useMemo(() => ({ election, loading, error: error, refresh }), [election, loading, error, refresh]);
  return <ElectionContext.Provider value={value}>{children}</ElectionContext.Provider>;
};
