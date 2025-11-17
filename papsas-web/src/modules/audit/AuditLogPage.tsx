import { useMemo, useState } from "react";
import { useAuth } from "../auth/AuthProvider";
import { isAdminUser } from "../auth/roles";
import { AuditFilterBar, type AuditFilterDraft } from "./components/AuditFilterBar";
import { AuditTable } from "./components/AuditTable";
import { useAuditEvents } from "./hooks/useAuditEvents";
import http from "../lib/http";

const defaultDraft: AuditFilterDraft = {
  action: "",
  status: "",
  election: "",
  since: "",
  until: "",
};

function toIso(value?: string): string | undefined {
  if (!value) return undefined;
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return undefined;
  return parsed.toISOString();
}

export default function AuditLogPage() {
  const { user, loading } = useAuth();
  const [draftFilters, setDraftFilters] = useState<AuditFilterDraft>(defaultDraft);
  const [appliedFilters, setAppliedFilters] = useState<Record<string, string | number | undefined>>({});
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const filters = useMemo(() => ({
    action: appliedFilters.action as string | undefined,
    status: appliedFilters.status as "" | "success" | "error" | undefined,
    election: typeof appliedFilters.election === "number" ? appliedFilters.election : undefined,
    since: appliedFilters.since as string | undefined,
    until: appliedFilters.until as string | undefined,
  }), [appliedFilters]);

  const { events, count, isLoading, error } = useAuditEvents({ page, pageSize, filters });

  const totalPages = Math.max(1, Math.ceil(count / pageSize));

  const handleApply = () => {
    setPage(1);
    setAppliedFilters({
      action: draftFilters.action.trim() || undefined,
      status: draftFilters.status || undefined,
      election: draftFilters.election ? Number(draftFilters.election) || undefined : undefined,
      since: draftFilters.since || undefined,
      until: draftFilters.until || undefined,
    });
  };

  const handleReset = () => {
    setDraftFilters(defaultDraft);
    setPage(1);
    setAppliedFilters({});
  };

  const exportHref = useMemo(() => {
    const params = new URLSearchParams();
    if (filters.action) params.set("action", filters.action);
    if (filters.status) params.set("status", filters.status);
    if (filters.election != null) params.set("election", String(filters.election));
    const since = toIso(filters.since);
    const until = toIso(filters.until);
    if (since) params.set("since", since);
    if (until) params.set("until", until);

    const base = (http.defaults.baseURL ?? "").replace(/\/$/, "");
    const query = params.toString();
    return `${base}/audit/events/export.csv${query ? `?${query}` : ""}`;
  }, [filters]);

  if (loading) {
    return <div className="text-sm text-gray-500">Loading audit log…</div>;
  }

  if (!user || !isAdminUser(user)) {
    return (
      <div className="rounded border bg-white p-4 text-sm text-red-600">
        You do not have permission to view the system audit log.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">System Audit Log</h1>
        <p className="text-sm text-gray-600">
          Admin-only view of key security and system events. Use filters to narrow by time, action, or election.
        </p>
      </div>
      <AuditFilterBar
        draft={draftFilters}
        onChange={setDraftFilters}
        onApply={handleApply}
        onReset={handleReset}
      />

      <div className="flex flex-col gap-2 rounded border bg-white p-4 shadow-sm md:flex-row md:items-center md:justify-between">
        <div className="text-sm text-gray-600">
          Showing page {page} of {totalPages} — {count} total events
        </div>
        <div className="flex gap-2 text-sm">
          <button
            className="px-3 py-1 rounded border bg-white text-gray-700 disabled:cursor-not-allowed disabled:opacity-50"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
          >
            Prev
          </button>
          <button
            className="px-3 py-1 rounded border bg-white text-gray-700 disabled:cursor-not-allowed disabled:opacity-50"
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
          >
            Next
          </button>
          <a
            className="px-3 py-1 rounded bg-gray-900 text-white"
            href={exportHref}
          >
            Export CSV
          </a>
        </div>
      </div>
      <div className="text-xs text-gray-500">
        Exports events matching the current filters as CSV.
      </div>
      <AuditTable events={events} isLoading={isLoading} error={error} />
    </div>
  );
}
