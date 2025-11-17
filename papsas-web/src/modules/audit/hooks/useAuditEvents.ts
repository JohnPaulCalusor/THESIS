import { useCallback, useEffect, useMemo, useState } from "react";
import http from "../../lib/http";

export type AuditEvent = {
  id: number;
  ts: string;
  actor_username: string;
  action: string;
  status: string;
  scope_election_id: number | null;
  target_type: string;
  target_id: string;
  ip: string | null;
  user_agent: string;
  method: string;
  path: string;
  payload_hash: string;
  meta: Record<string, unknown>;
};

export type AuditEventsResponse = {
  count: number;
  page: number;
  page_size: number;
  results: AuditEvent[];
};

export type AuditFilters = {
  action?: string;
  status?: "" | "success" | "error";
  election?: number | null;
  since?: string;
  until?: string;
};

export type UseAuditEventsArgs = {
  page: number;
  pageSize: number;
  filters: AuditFilters;
};

export type UseAuditEventsResult = {
  events: AuditEvent[];
  count: number;
  page: number;
  pageSize: number;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
};

function toIso(value?: string): string | undefined {
  if (!value) return undefined;
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return undefined;
  return parsed.toISOString();
}

export function useAuditEvents({ page, pageSize, filters }: UseAuditEventsArgs): UseAuditEventsResult {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [count, setCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  const params = useMemo(() => {
    const builder: Record<string, string> = {
      page: String(page),
      page_size: String(pageSize),
    };
    if (filters.action?.trim()) builder.action = filters.action.trim();
    if (filters.status) builder.status = filters.status;
    if (filters.election != null && !Number.isNaN(filters.election)) {
      builder.election = String(filters.election);
    }
    const since = toIso(filters.since);
    const until = toIso(filters.until);
    if (since) builder.since = since;
    if (until) builder.until = until;
    return builder;
  }, [page, pageSize, filters]);

  useEffect(() => {
    const controller = new AbortController();
    setIsLoading(true);
    setError(null);
    http
      .get<AuditEventsResponse>("audit/events", { params, signal: controller.signal })
      .then((res) => {
        setEvents(res.data.results);
        setCount(res.data.count);
      })
      .catch((err: unknown) => {
        if (controller.signal.aborted) return;
        const ax = err as { response?: { status?: number; data?: { message?: string } }; message?: string };
        const status = ax.response?.status;
        const msg = ax.response?.data?.message || ax.message || "Failed to load audit events.";
        if (status === 401 || status === 403) {
          setError(`Unauthorized: ${msg}`);
        } else {
          setError(msg);
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      });

    return () => {
      controller.abort();
    };
  }, [params, reloadKey]);

  const refetch = useCallback(() => {
    setReloadKey((n) => n + 1);
  }, []);

  return { events, count, page, pageSize, isLoading, error, refetch };
}
