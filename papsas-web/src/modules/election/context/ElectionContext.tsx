import React, { createContext, useCallback, useEffect, useMemo, useState } from "react";
import http from "../../lib/http";

export type Election = { id: number; title?: string | null };
export type ElectionContextShape = {
  election: Election | null;
  refresh: () => Promise<void>;
  loading: boolean;
  error: string | null;
};

const Ctx = createContext<ElectionContextShape>({
  election: null,
  loading: false,
  refresh: async () => {},
  error: null,
});

export const ElectionContext = Ctx;

export const ElectionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [election, setElection] = useState<Election | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await http.get<Election>("elections/current");
      setElection({ id: data.id, title: data.title });
    } catch (e: unknown) {
      const status = (e as { status?: number })?.status;
      if (status === 404) {
        setElection(null);
      } else {
        setError("Failed to load election info.");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const value = useMemo<ElectionContextShape>(() => ({ election, loading, refresh, error }), [election, loading, refresh, error]);
  return <ElectionContext.Provider value={value}>{children}</ElectionContext.Provider>;
};
