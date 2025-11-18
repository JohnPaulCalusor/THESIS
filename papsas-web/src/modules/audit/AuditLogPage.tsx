// src/modules/audit/AuditLogPage.tsx
import { useMemo, useState } from "react";
import { useAuth } from "../auth/AuthProvider";
import { isAdminUser } from "../auth/roles";
import {
  AuditFilterBar,
  type AuditFilterDraft,
} from "./components/AuditFilterBar";
import { AuditTable } from "./components/AuditTable";
import { useAuditEvents } from "./hooks/useAuditEvents";
import http from "../lib/http";

import "./AuditLogPage.css";

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
  const [draftFilters, setDraftFilters] =
    useState<AuditFilterDraft>(defaultDraft);
  const [appliedFilters, setAppliedFilters] = useState<
    Record<string, string | number | undefined>
  >({});
  const [page, setPage] = useState(1);
  const [exporting, setExporting] = useState(false);
  const pageSize = 20;

  const filters = useMemo(
    () => ({
      action: appliedFilters.action as string | undefined,
      status: appliedFilters.status as "" | "success" | "error" | undefined,
      election:
        typeof appliedFilters.election === "number"
          ? appliedFilters.election
          : undefined,
      since: appliedFilters.since as string | undefined,
      until: appliedFilters.until as string | undefined,
    }),
    [appliedFilters]
  );

  const { events, count, isLoading, error } = useAuditEvents({
    page,
    pageSize,
    filters,
  });

  const totalPages = Math.max(1, Math.ceil(count / pageSize));

  const handleApply = () => {
    setPage(1);
    setAppliedFilters({
      action: draftFilters.action.trim() || undefined,
      status: draftFilters.status || undefined,
      election: draftFilters.election
        ? Number(draftFilters.election) || undefined
        : undefined,
      since: draftFilters.since || undefined,
      until: draftFilters.until || undefined,
    });
  };

  const handleReset = () => {
    setDraftFilters(defaultDraft);
    setPage(1);
    setAppliedFilters({});
  };

  // Build relative path used by axios (http) so it includes Authorization header
  const exportPath = useMemo(() => {
    const params = new URLSearchParams();
    if (filters.action) params.set("action", filters.action);
    if (filters.status) params.set("status", filters.status);
    if (filters.election != null)
      params.set("election", String(filters.election));
    const since = toIso(filters.since);
    const until = toIso(filters.until);
    if (since) params.set("since", since);
    if (until) params.set("until", until);

    const query = params.toString();
    return `/audit/events/export.csv${query ? `?${query}` : ""}`;
  }, [filters]);

  const handleExport = async () => {
    try {
      setExporting(true);
      const res = await http.get(exportPath, { responseType: "blob" });

      const blob = new Blob([res.data], {
        type: "text/csv;charset=utf-8;",
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;

      const ts = new Date()
        .toISOString()
        .slice(0, 19)
        .replace(/[:T]/g, "-");
      link.download = `audit-events-${ts}.csv`;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error(e);
      alert("Failed to export CSV. Please try again.");
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="audit-page">
        <div className="audit-page-container">
          <div className="audit-loading">Loading audit log…</div>
        </div>
      </div>
    );
  }

  if (!user || !isAdminUser(user)) {
    return (
      <div className="audit-page">
        <div className="audit-page-container">
          <div className="audit-unauthorized card">
            <h1 className="audit-title">System Audit Log</h1>
            <p className="audit-subtitle">
              You do not have permission to view the system audit log.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="audit-page">
      <div className="audit-page-container">
        {/* Header */}
        <header className="audit-header">
          <div>
            <h1 className="audit-title">System Audit Log</h1>
            <p className="audit-subtitle">
              Admin-only view of key security and system events. Use filters to
              narrow by time, action, or election.
            </p>
          </div>
          <span className="audit-badge">Admin only</span>
        </header>

        {/* Filters */}
        <AuditFilterBar
          draft={draftFilters}
          onChange={setDraftFilters}
          onApply={handleApply}
          onReset={handleReset}
        />

        {/* Summary / pagination / export */}
        <div className="card audit-summary-bar">
          <div className="audit-summary-text">
            Showing page <strong>{page}</strong> of{" "}
            <strong>{totalPages}</strong> — <strong>{count}</strong> total
            events
          </div>
          <div className="audit-summary-actions">
            <button
              className="audit-btn audit-btn--ghost"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              type="button"
            >
              Prev
            </button>
            <button
              className="audit-btn audit-btn--ghost"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              type="button"
            >
              Next
            </button>
            <button
              type="button"
              className="audit-btn audit-btn--primary"
              onClick={handleExport}
              disabled={exporting}
            >
              {exporting ? "Exporting…" : "Export CSV"}
            </button>
          </div>
        </div>

        <p className="audit-export-hint">
          Export includes only events that match the current filters.
        </p>

        {/* Table */}
        <AuditTable events={events} isLoading={isLoading} error={error} />
      </div>
    </div>
  );
}
