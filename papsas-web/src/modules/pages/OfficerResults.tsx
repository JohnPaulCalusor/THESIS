// src/modules/pages/OfficerResults.tsx
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useToast } from "../ui/Toast";
import http from "../lib/http";
import { downloadCsv } from "../lib/csv";
import { getAnalytics, postExplain } from "../election/services/analyticsApi";
import type { AnalyticsDTO, ExplainDTO } from "../election/types";
import { useElection } from "../election/hooks/useElection";
import {
  ResponsiveContainer, BarChart, XAxis, YAxis, CartesianGrid, Tooltip, Bar
} from "recharts";

/* ---------- types ---------- */
type ApiRow = {
  candidacyId?: number;
  candidateId?: number;
  candidate_id?: number;
  name?: string;
  votes?: number;
  count?: number;
};
type ApiJson = {
  election?: { id: number; title?: string };
  results?: ApiRow[];
  positions?: ApiPosition[];
};

type ApiTotal = {
  candidacy_id?: number;
  candidate_id?: number;
  candidate_name?: string;
  name?: string;
  count?: number;
  votes?: number;
};
type ApiPosition = {
  id?: number;
  position_id?: number;
  title?: string;
  position_title?: string;
  totals?: ApiTotal[];
  candidates?: ApiTotal[];
};
type AxiosErrorLike = { response?: { status?: number; data?: { message?: string } }; message?: string };

type Tot = { candidate_id: number; name: string; count: number };
type Position = { id: number; title: string; totals: Tot[] };
type Results = { election: { id: number; title?: string }; positions: Position[] };

/* ---------- small hooks ---------- */
function useMediaQuery(q: string) {
  const get = () => (typeof window !== "undefined" && "matchMedia" in window)
    ? window.matchMedia(q).matches : false;
  const [m, setM] = useState(get);
  useEffect(() => {
    const mq = window.matchMedia(q);
    const on = () => setM(mq.matches);
    if (typeof mq.addEventListener === "function") {
      mq.addEventListener("change", on);
    } else {
      mq.addListener(on);
    }
    return () => {
      if (typeof mq.removeEventListener === "function") {
        mq.removeEventListener("change", on);
      } else {
        mq.removeListener(on);
      }
    };
  }, [q]);
  return m;
}

/* ---------- page ---------- */
export default function OfficerResults() {
  const { election } = useElection();
  const [data, setData] = useState<Results | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<{ code: number; msg: string; body?: string } | null>(null);
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const pollRef = useRef<number | null>(null);
  const toast = useToast();
  const [analyticsData, setAnalyticsData] = useState<AnalyticsDTO | null>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [analyticsError, setAnalyticsError] = useState<string | null>(null);
  const [explainData, setExplainData] = useState<ExplainDTO | null>(null);
  const [explainLoading, setExplainLoading] = useState(false);
  const [showExplain, setShowExplain] = useState(false);

  const isMobile = useMediaQuery("(max-width: 640px)");
  const prefersReducedMotion = useMediaQuery("(prefers-reduced-motion: reduce)");
  const effectiveId = election?.id?.toString();

  const fetchOnce = useCallback(async () => {
    setErr(null);
    try {
      if (!effectiveId) throw new Error("No election id");
      const res = await http.get<ApiJson>(`elections/${effectiveId}/results`);
      const normalized = normalize(res.data, Number(effectiveId));
      setData(normalized);
      setUpdatedAt(new Date());
    } catch (e) {
      const errInfo = e as AxiosErrorLike;
      const code = errInfo?.response?.status ?? 0;
      const body = typeof errInfo?.response?.data === "string" ? errInfo.response.data : "";
      setErr({
        code,
        msg:
          code === 401 ? "Your session expired. Please sign in again."
        : code === 403 ? "Officers only."
        : code === 404 ? "Results endpoint not found."
        : code === 500 ? "Server error while loading results."
        : "Failed to load results.",
        body,
      });
    } finally {
      setLoading(false);
    }
  }, [effectiveId]);

  // polling helpers (pause when tab hidden)
  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      window.clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);
  const startPolling = useCallback(() => {
    stopPolling();
    const intervalMs = import.meta.env.DEV ? 5000 : 10000;
    pollRef.current = window.setInterval(() => { fetchOnce(); }, intervalMs);
  }, [fetchOnce, stopPolling]);

  useEffect(() => {
    let cancel = false;
    setLoading(true);
    fetchOnce().then(() => !cancel && startPolling());

    const onVis = () => {
      if (document.hidden) stopPolling();
      else { fetchOnce(); startPolling(); }
    };
    document.addEventListener("visibilitychange", onVis);

    return () => {
      cancel = true;
      document.removeEventListener("visibilitychange", onVis);
      stopPolling();
    };
  }, [fetchOnce, startPolling, stopPolling]);

  async function downloadCSV(electionId: number): Promise<boolean> {
    try {
      const paths = [
        `elections/${electionId}/results/export.csv`,
        `elections/${electionId}/results.csv`,
        `results/${electionId}/export.csv`,
      ];
      for (const p of paths) {
        const path = p.replace(/^\/+/, "").replace(/^api\//i, "");
        const { data: blob, headers, status } = await http.get(path, { responseType: "blob" as const });
        const ct = (headers?.["content-type"] as string) || "";
        if (status >= 200 && status < 300 && ct.includes("text/csv")) {
          const a = document.createElement("a");
          a.href = URL.createObjectURL(blob);
          a.download = `results-election-${electionId}-${new Date().toISOString().slice(0,16).replace(/[-:T]/g,"")}.csv`;
          a.click();
          return true;
        }
      }
    } catch {
      /* ignore; fallback to client CSV */
    }
    return false;
  }

  const onDownloadCsv = useCallback(async () => {
    if (!data || !effectiveId) return;
    try {
      const ok = await downloadCSV(Number(effectiveId));
      if (ok) return;
    } catch {
      // ignore remote CSV failures; fallback handles client generation
    }
    const csv = makeClientCsv(data);
    try {
      const now = new Date();
      const ts = `${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}-${String(now.getHours()).padStart(2,'0')}${String(now.getMinutes()).padStart(2,'0')}`;
      downloadCsv(`results-election-${effectiveId}-${ts}.csv`, csv);
    } catch {
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
      saveBlob(blob, `results-election-${effectiveId}.csv`);
    }
  }, [data, effectiveId]);

  const loadAnalytics = useCallback(
    async (opts?: { quiet?: boolean }) => {
      if (!effectiveId) return;
      setAnalyticsLoading(true);
      setAnalyticsError(null);
      try {
        const res = await getAnalytics(Number(effectiveId));
        setAnalyticsData(res);
        if (import.meta.env.DEV && !opts?.quiet) console.log("DEBUG analyticsData", res);
        if (!opts?.quiet) {
          toast.success("Analytics loaded");
        }
      } catch (e) {
        const errInfo = e as AxiosErrorLike;
        const message =
          errInfo?.response?.status === 403
            ? "Officers only."
            : errInfo?.response?.data?.message || errInfo?.message || "Failed to load analytics";
        setAnalyticsError(message);
        setAnalyticsData(null);
        if (!opts?.quiet) {
          toast.error(message);
        }
      } finally {
        setAnalyticsLoading(false);
      }
    },
    [effectiveId, toast]
  );
  const onAnalytics = useCallback(() => {
    void loadAnalytics();
  }, [loadAnalytics]);

  useEffect(() => {
    if (!effectiveId) return;
    void loadAnalytics({ quiet: true });
  }, [effectiveId, loadAnalytics]);

  const onExplain = useCallback(async () => {
    if (!effectiveId) return;
    setExplainLoading(true);
    try {
      const res = await postExplain(Number(effectiveId), { style: "short" });
      setExplainData(res);
      setShowExplain(true);
    } catch (e) {
      const errInfo = e as AxiosErrorLike;
      toast.error(errInfo?.response?.data?.message || errInfo?.message || "Failed to load explanation");
    } finally {
      setExplainLoading(false);
    }
  }, [effectiveId, toast]);

  const onManualRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await Promise.all([fetchOnce(), loadAnalytics({ quiet: true })]);
    } finally {
      setRefreshing(false);
    }
  }, [fetchOnce, loadAnalytics]);

  if (!effectiveId) return <Loader text="No active election." />;
  if (loading) return <Loader text="Loading results…" />;

  if (err) {
    return (
      <div className="page-results">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="card" style={{ borderColor: "rgba(248,113,113,.4)", background: "rgba(248,113,113,.1)" }}>
            <h2 className="text-lg font-semibold">Failed to load results (HTTP {err.code || 0})</h2>
            <p className="mt-1">{err.msg}</p>
            <div className="mt-3 flex gap-2">
              <button onClick={() => { setLoading(true); fetchOnce(); }} className="btn btn-primary">Retry</button>
            </div>
            {import.meta.env.DEV && err.body && (
              <details className="mt-3">
                <summary className="cursor-pointer">Show server debug</summary>
                <pre className="mt-2 text-xs whitespace-pre-wrap">{err.body}</pre>
              </details>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (!data) return <Loader text="No data." />;

  return (
    <div className="page-results">
      <div className="content-wrapper">
        {/* ---------- HEADER ---------- */}
        <div className="mb-4 sm:mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            {/* was text-[2rem] + brand-neutral */}
            <h2 className="text-[1.5rem] md:text-[1.75rem] font-extrabold tracking-tight text-[var(--brand)]">
              RESULTS
            </h2>
            {/* smaller timestamp */}
            <p className="mt-0.5 text-xs text-[var(--text-muted)]" aria-live="polite">
              Live tally • Updated {updatedAt?.toLocaleTimeString() ?? "-"}
            </p>
          </div>

        <div className="top-buttons">
          <button onClick={onManualRefresh} className="btn btn-secondary" aria-label="Refresh live results" disabled={refreshing}>
            {refreshing ? "Refreshing…" : "Refresh"}
          </button>
          <button onClick={onDownloadCsv} className="btn btn-download-csv" aria-label="Download CSV">Download CSV</button>
          <button onClick={onAnalytics} className="btn btn-secondary" disabled={analyticsLoading}>
            {analyticsLoading ? "Loading…" : "Analytics"}
          </button>
          <button onClick={onExplain} className="btn btn-secondary" disabled={explainLoading}>
            {explainLoading ? "Loading…" : "Explain"}
          </button>
        </div>
        {analyticsError && (
          <div className="callout callout-warn mb-4 text-sm">
            Analytics: {analyticsError}
          </div>
        )}
      </div>

        {analyticsData && analyticsData.positions.length > 0 ? (
          <div className="card mb-4 border border-dashed border-[var(--border)] bg-[var(--surface)]">
            <h3 className="text-lg font-semibold mb-2">Analytics overview</h3>
            <div className="flex flex-wrap gap-6 text-sm text-[var(--text-muted)]">
              <div>Total votes: {analyticsData.meta?.totalVotes ?? "—"}</div>
              <div>Positions: {analyticsData.positions.length}</div>
              <div>Top candidate: {analyticsData.positions[0]?.totals?.[0]?.name || "—"}</div>
            </div>
          </div>
        ) : analyticsData ? (
          <div className="callout callout-info mb-4">
            No analytics available yet. Once votes are cast, this section will show per-position totals.
          </div>
        ) : null}

        {explainData && showExplain && (
          <details open className="card mb-4">
            <summary className="cursor-pointer text-sm font-semibold">Explain narrative</summary>
            <p className="mt-2 text-sm text-[var(--text-muted)]">
              {explainData.long || explainData.text || explainData.short}
            </p>
          </details>
        )}

        {/* ---------- POSITION CARDS ---------- */}
        <div className="space-y-8">
          {data.positions.map((p) => (
            <PositionChart key={p.id} position={p} isMobile={isMobile} reduceMotion={prefersReducedMotion} />
          ))}
        </div>
      </div>
    </div>
  );
}

/* ---------- helpers ---------- */
function normalize(raw: ApiJson, electionId: number): Results {
  const sortTotals = (totals?: ApiTotal[]) =>
    (totals || [])
      .map((t) => {
        const candidateId = Number(t.candidacy_id ?? t.candidate_id ?? 0);
        return {
          candidate_id: candidateId,
          name: t.candidate_name ?? t.name ?? `#${candidateId}`,
          count: Number(t.count ?? t.votes ?? 0),
        };
      })
      .sort((a, b) => b.count - a.count);

  if (Array.isArray(raw?.positions)) {
    const positions = (raw.positions || []).map((p: ApiPosition) => {
      const id = Number(p.id ?? p.position_id ?? electionId);
      const title = p.title ?? p.position_title ?? `Position #${id}`;
      const totals = sortTotals(p.totals ?? p.candidates);
      return { id, title, totals };
    });
    return {
      election: raw.election || { id: electionId, title: `Election #${electionId}` },
      positions,
    };
  }

  const totals = (raw?.results || [])
    .map((r) => {
      const candidateId = Number(r.candidacyId ?? r.candidateId ?? r.candidate_id ?? 0);
      return {
        candidate_id: candidateId,
        name: r.name || `#${candidateId}`,
        count: Number(r.votes ?? r.count ?? 0),
      };
    })
    .sort((a, b) => b.count - a.count);

  return {
    election: raw?.election || { id: electionId, title: `Election #${electionId}` },
    positions: [
      { id: electionId, title: raw?.election?.title || `Election #${electionId}`, totals },
    ],
  };
}

function PositionChart({ position, isMobile, reduceMotion }: { position: Position; isMobile: boolean; reduceMotion: boolean; }) {

  const rows = useMemo(
    () => (position.totals || []).map(t => ({ name: t.name, count: t.count })),
    [position]
  );

  if (rows.length === 0) {
    return (
      <fieldset className="card">
        <legend className="text-lg font-bold text-[var(--text)]">{position.title}</legend>
        <div className="rounded-xl border border-[var(--border-soft)] p-8 text-center text-sm text-[var(--text-muted)] bg-[var(--card)]">
          No votes yet.
        </div>
      </fieldset>
    );
  }

  // Mobile: taller chart; Desktop: wider aspect
  const height = isMobile ? 280 : 360;

  return (
    <fieldset className="results-card">
      <legend className="flex items-center justify-between text-lg font-bold text-[var(--text)]">
        {position.title}
        <button
          className="text-sm font-medium underline text-[var(--brand)] hover:text-[var(--brand-600)]"
          onClick={() => {
            const csv = [
              ["Position", "Candidate", "Votes"],
              ...((position.totals || []).map(t => [position.title, t.name, String(t.count)])),
            ].map(r => r.map(v => {
              const s = String(v ?? "").replace(/"/g, '""');
              return /[",\n]/.test(s) ? `"${s}"` : s;
            }).join(",")).join("\r\n");
            try {
              const now = new Date();
              const ts = `${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}-${String(now.getHours()).padStart(2,'0')}${String(now.getMinutes()).padStart(2,'0')}`;
              downloadCsv(`results-position-${position.id}-${ts}.csv`, csv);
            } catch {
              const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url; a.download = `results-position-${position.id}.csv`; a.click();
              URL.revokeObjectURL(url);
            }
          }}
          aria-label={`Download CSV for ${position.title}`}
        >
          CSV
        </button>
      </legend>

      <div className="mt-4" style={{ width: "100%", minHeight: height }}>
        <ResponsiveContainer width="100%" height={height}>
          <BarChart data={rows} margin={{ top: 12, right: 20, left: 0, bottom: isMobile ? 8 : 12 }}>
            <CartesianGrid stroke="var(--border-soft)" strokeDasharray="4 4" />
            <XAxis
              dataKey="name"
              tick={{ fill: "var(--text-muted)", fontSize: isMobile ? 12 : 13 }}
              angle={isMobile ? -25 : -45}
              textAnchor="end"
              height={isMobile ? 60 : 100}
              interval={0}
            />
            <YAxis tick={{ fill: "var(--text-muted)", fontSize: isMobile ? 12 : 13 }} allowDecimals={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: "var(--card)",
                border: "1px solid var(--border)",
                borderRadius: "var(--r-md)",
                fontSize: "0.875rem",
              }}
            />
            <Bar
              dataKey="count"
              fill="var(--brand)"
              radius={[8, 8, 0, 0]}
              isAnimationActive={!reduceMotion}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </fieldset>
  );
}

function makeClientCsv(data: Results) {
  const lines: string[] = [];
  lines.push("Position,Candidate,Votes");
  for (const p of data.positions) {
    for (const t of p.totals) lines.push([csvq(p.title), csvq(t.name), String(t.count)].join(","));
  }
  return lines.join("\r\n");
}
function csvq(s?: string) {
  const v = (s ?? "").replace(/"/g, '""');
  return /[",\n]/.test(v) ? `"${v}"` : v;
}
function saveBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename;
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
}

function Loader({ text }: { text: string }) {
  return (
    <div className="page-results grid place-items-center min-h-screen">
      <div className="animate-pulse text-lg text-[var(--text-muted)]">{text}</div>
    </div>
  );
}
