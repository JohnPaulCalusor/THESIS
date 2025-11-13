/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useCallback, useEffect, useMemo, useState } from "react";
import http from "../../lib/http";

export type Election = { id: number; title: string };
type ElectionError = {
  response?: { status?: number; data?: { message?: string } };
  status?: number;
  message?: string;
};
type Ctx = {
  election: Election | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
};

export const ElectionContext = createContext<Ctx | null>(null);

export const ElectionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [election, setElection] = useState<Election | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setErr] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setErr(null);
    try {
      const { data } = await http.get<Election>("elections/current");
      setElection({ id: data.id, title: data.title });
    } catch (error) {
      const err = error as ElectionError;
      const status = err.response?.status ?? err.status;
      if (status === 404) {
        setElection(null); // no active election
      } else {
        setErr(err.response?.data?.message || err.message || "Failed to load current election");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  const value = useMemo(() => ({ election, loading, error: error, refresh }), [election, loading, error, refresh]);
  return <ElectionContext.Provider value={value}>{children}</ElectionContext.Provider>;
};
