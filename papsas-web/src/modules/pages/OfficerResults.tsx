// src/modules/pages/OfficerResults.tsx
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useToast } from "../ui/Toast";
import { useAuth } from "../auth/AuthProvider";
import { isAdminUser } from "../auth/roles";
import http from "../lib/http";
import { downloadCsv } from "../lib/csv";
import { getAnalytics, postExplain } from "../election/services/analyticsApi";
import type { AnalyticsDTO, ExplainDTO } from "../election/types";
import { useElection } from "../election/hooks/useElection";
import {
  ResponsiveContainer,
  BarChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Bar,
} from "recharts";

import "./OfficerResults.css";

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
  positions?: {
    id: number;
    title: string;
    totals: { candidate_id: number; name?: string; count: number }[];
  }[];
};

type Tot = {
  candidate_id: number;
  name?: string;
  count: number;
  share?: number;
};
type Pos = { id: number; title?: string; totals: Tot[] };
type Position = { id: number; title: string; totals: Tot[] };
type Results = {
  election: { id: number; title?: string };
  positions: Position[];
};

/* ---------- page ---------- */
export default function OfficerResults() {
  const { election } = useElection();
  const { user } = useAuth();
  const [data, setData] = useState<Results | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<{
    code: number;
    msg: string;
    body?: string;
  } | null>(null);
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);
  const pollRef = useRef<number | null>(null);
  const toast = useToast();

  const canViewInsights =
    Boolean(user) &&
    (isAdminUser(user) ||
      (user?.groups || []).some(
        (g) => String(g).toLowerCase() === "officer"
      ));

  const [panel, setPanel] = useState<{
    kind: "analytics" | "explain";
    payload: AnalyticsDTO | ExplainDTO;
  } | null>(null);

  const effectiveId = election?.id?.toString();

  const fetchOnce = useCallback(async () => {
    setErr(null);
    try {
      if (!effectiveId) throw new Error("No election id");
      const res = await http.get<ApiJson>(`elections/${effectiveId}/results`);
      const normalized = normalize(res.data, Number(effectiveId));
      setData(normalized);
      setUpdatedAt(new Date());
    } catch (e: unknown) {
      const ax = e as { response?: { status?: number; data?: unknown } };
      const code = ax.response?.status ?? 0;
      const body =
        typeof ax.response?.data === "string" ? ax.response?.data : "";
      setErr({
        code,
        msg:
          code === 401
            ? "Your session expired. Please sign in again."
            : code === 403
            ? "Officers only."
            : code === 404
            ? "Results endpoint not found."
            : code === 500
            ? "Server error while loading results."
            : "Failed to load results.",
        body,
      });
    } finally {
      setLoading(false);
    }
  }, [effectiveId]);

  useEffect(() => {
    let cancel = false;
    setLoading(true);
    fetchOnce();

    const intervalMs = import.meta.env.DEV ? 5000 : 10000;
    pollRef.current = window.setInterval(() => {
      if (!cancel) fetchOnce();
    }, intervalMs);

    return () => {
      cancel = true;
      if (pollRef.current) window.clearInterval(pollRef.current);
    };
  }, [fetchOnce]);

  useEffect(() => {
    if (!canViewInsights) {
      setPanel(null);
    }
  }, [canViewInsights]);

  async function downloadCSV(electionId: number): Promise<boolean> {
    try {
      const paths = [
        `elections/${electionId}/results/export.csv`,
        `results/${electionId}/export.csv`,
      ];

      for (const p of paths) {
        const path = p.replace(/^\/+/, "").replace(/^api\//i, "");
        const {
          data: blob,
          headers,
          status,
        } = await http.get(path, { responseType: "blob" as const });
        const ct = (headers?.["content-type"] as string) || "";
        if (status >= 200 && status < 300 && ct.includes("text/csv")) {
          const a = document.createElement("a");
          a.href = URL.createObjectURL(blob);
          a.download = `results-election-${electionId}-${new Date()
            .toISOString()
            .slice(0, 16)
            .replace(/[-:T]/g, "")}.csv`;
          a.click();
          return true;
        }
      }
    } catch {
      // ignore; fallback to client CSV
    }
    return false;
  }

  const onDownloadCsv = useCallback(async () => {
    if (!data) return;
    try {
      if (!effectiveId) return;
      const ok = await downloadCSV(Number(effectiveId));
      if (ok) return;
    } catch {
      // fallback to client CSV
    }
    const csv = makeClientCsv(data);
    try {
      const now = new Date();
      const ts = `${now.getFullYear()}${String(
        now.getMonth() + 1
      ).padStart(2, "0")}${String(now.getDate()).padStart(2, "0")}-${String(
        now.getHours()
      ).padStart(2, "0")}${String(now.getMinutes()).padStart(2, "0")}`;
      downloadCsv(`results-election-${effectiveId}-${ts}.csv`, csv);
    } catch {
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
      saveBlob(blob, `results-election-${effectiveId}.csv`);
    }
  }, [data, effectiveId]);

  const onAnalytics = useCallback(async () => {
    if (!canViewInsights) return;
    try {
      if (!effectiveId) return;
      const res = await getAnalytics(Number(effectiveId));
      setPanel({ kind: "analytics", payload: res });
    } catch (e: unknown) {
      toast.apiError(e, "Failed to load analytics");
    }
  }, [effectiveId, toast, canViewInsights]);

  const onExplain = useCallback(async () => {
    if (!canViewInsights) return;
    try {
      if (!effectiveId) return;
      const res = await postExplain(Number(effectiveId), { style: "short" });
      setPanel({ kind: "explain", payload: res });
    } catch (e: unknown) {
      toast.apiError(e, "Failed to load explanation");
    }
  }, [effectiveId, toast, canViewInsights]);

  if (!effectiveId) return <Loader text="No active election." />;
  if (loading) return <Loader text="Loading results…" />;

  if (err) {
    return (
      <div className="officer-results-page">
        <div className="officer-results-container">
          <div
            className="card"
            style={{
              borderColor: "rgba(248,113,113,.4)",
              background: "rgba(248,113,113,.1)",
            }}
          >
            <h2 className="text-lg font-semibold">
              Failed to load results (HTTP {err.code || 0})
            </h2>
            <p className="mt-1">{err.msg}</p>
            <div className="mt-3 flex gap-2">
              <button
                onClick={() => {
                  setLoading(true);
                  fetchOnce();
                }}
                className="btn btn-primary"
              >
                Retry
              </button>
            </div>
            {import.meta.env.DEV && err.body && (
              <details className="mt-3">
                <summary className="cursor-pointer">Show server debug</summary>
                <pre className="mt-2 text-xs whitespace-pre-wrap">
                  {err.body}
                </pre>
              </details>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (!data) return <Loader text="No data." />;

  return (
    <div className="officer-results-page">
      <div className="officer-results-container">
        {/* Header / title + actions */}
        <div className="officer-results-header">
          <div>
          <h1 className="text-2xl font-semibold">Election Results</h1>
          <p className="subtle text-sm">
            {(data.election?.title ?? `Election #${effectiveId}`)} — Live tally
          </p>

            {updatedAt && (
              <p className="officer-results-updated">
                Updated {updatedAt.toLocaleTimeString()}
              </p>
            )}
          </div>
          <div className="officer-results-actions">
            <button onClick={fetchOnce} className="btn btn-secondary">
              Refresh
            </button>
            <button onClick={onDownloadCsv} className="btn btn-primary">
              Download CSV
            </button>
            {canViewInsights && (
              <>
                <button onClick={onAnalytics} className="btn btn-secondary">
                  Analytics
                </button>
                <button onClick={onExplain} className="btn btn-secondary">
                  Explain
                </button>
              </>
            )}
          </div>
        </div>

        {/* Insights panel (Analytics / Explain) */}
        {panel && canViewInsights && (
          <div className="officer-results-panel card mb-6">
            <div className="officer-results-panel-header">
              <h3 className="officer-results-panel-title">
                {panel.kind === "analytics" ? "Analytics" : "Explanation"}
              </h3>
              <button
                className="officer-results-panel-close"
                onClick={() => setPanel(null)}
              >
                Close
              </button>
            </div>

            {panel.kind === "analytics" ? (
              <AnalyticsTable payload={panel.payload as AnalyticsDTO} />
            ) : (
              <ExplainPanel payload={panel.payload as ExplainDTO} />
            )}
          </div>
        )}

        {/* Position charts */}
        <div className="officer-results-positions">
          {data.positions.map((p) => (
            <PositionChart key={p.id} position={p} />
          ))}
        </div>
      </div>
    </div>
  );
}

/* ---------- helpers ---------- */

function normalize(raw: ApiJson, electionId: number): Results {
  if (Array.isArray(raw?.positions)) {
    const positions = (raw.positions || []).map((p) => ({
      id: Number(p.id),
      title: p.title || `Position #${p.id}`,
      totals: (p.totals || []).map((t) => ({
        candidate_id: Number(t.candidate_id),
        name: t.name || `#${t.candidate_id}`,
        count: Number(t.count || 0),
      })),
    }));
    return {
      election:
        raw.election || {
          id: electionId,
          title: `Election #${electionId}`,
        },
      positions,
    };
  }

  const totals = (raw?.results || []).map((r) => ({
    candidate_id: Number(
      r.candidacyId ?? r.candidateId ?? r.candidate_id ?? 0
    ),
    name:
      r.name ||
      `#${r.candidacyId ?? r.candidateId ?? r.candidate_id ?? ""}`,
    count: Number(r.votes ?? r.count ?? 0),
  }));
  return {
    election:
      raw?.election || {
        id: electionId,
        title: `Election #${electionId}`,
      },
    positions: [
      {
        id: electionId,
        title: raw?.election?.title || `Election #${electionId}`,
        totals,
      },
    ],
  };
}

/**
 * Normalize AnalyticsDTO from either:
 *   - old shape: { positions: [{ id, title, totals: [{ candidate_id, name, count, share }] }] }
 *   - new shape: { by_position: [...], by_candidate: [...] }
 */
function normalizeAnalyticsPayload(payload: any): Pos[] {
  if (!payload) return [];

  // Old / already-normalized shape
  if (Array.isArray(payload.positions)) {
    return (payload.positions as any[]).map((p) => ({
      id: Number(p.id),
      title: p.title ?? `Position #${p.id}`,
      totals: (p.totals || []).map((t: any) => ({
        candidate_id: Number(t.candidate_id),
        name: t.name ?? `#${t.candidate_id}`,
        count: Number(t.count ?? 0),
        share:
          typeof t.share === "number"
            ? t.share
            : undefined,
      })),
    }));
  }

  const byPos = Array.isArray(payload.by_position)
    ? payload.by_position
    : [];
  const byCand = Array.isArray(payload.by_candidate)
    ? payload.by_candidate
    : [];

  const map = new Map<number, Pos>();

  // Prefill from by_position so we get titles & totals (overall per position)
  for (const p of byPos) {
    const id = Number(p.position_id ?? p.id);
    if (!Number.isFinite(id)) continue;
    const title = p.title ?? `Position #${id}`;
    if (!map.has(id)) {
      map.set(id, { id, title, totals: [] });
    } else {
      const existing = map.get(id)!;
      if (!existing.title && title) existing.title = title;
    }
  }

  // Add candidate-level rows from by_candidate
  for (const row of byCand) {
    const posId = Number(row.position_id);
    if (!Number.isFinite(posId)) continue;
    const candidateId = Number(
      row.candidate_id ?? row.candidacy_id ?? row.id
    );
    const count = Number(row.count ?? row.votes ?? 0);

    const existing =
      map.get(posId) ||
      {
        id: posId,
        title: `Position #${posId}`,
        totals: [] as Tot[],
      };

    existing.totals.push({
      candidate_id: candidateId,
      name: row.name ?? `#${candidateId}`,
      count,
    });

    map.set(posId, existing);
  }

  // Compute share per position
  for (const pos of map.values()) {
    const total = pos.totals.reduce((sum, t) => sum + t.count, 0);
    if (total > 0) {
      pos.totals = pos.totals.map((t) => ({
        ...t,
        share: t.count / total,
      }));
    }
  }

  return Array.from(map.values()).sort((a, b) => a.id - b.id);
}

/* ----- analytics subcomponents ----- */

function AnalyticsTable({ payload }: { payload: AnalyticsDTO }) {
  const a: any = payload;
  const positions: Pos[] = normalizeAnalyticsPayload(a);

  const totalVotes = a.total_votes ?? a.meta?.totalVotes ?? null;
  const positionsCount = positions.length;
  const shares: number[] = positions.flatMap((p) =>
    (p.totals || []).map((t) => Number(t.share ?? 0))
  );
  const topShare =
    shares.length > 0 ? Math.round(Math.max(...shares) * 100) : null;

  return (
    <>
      <div className="overflow-auto officer-results-table-wrap">
        <table className="officer-results-table min-w-full text-sm">
          <thead className="bg-gray-50">
            <tr className="[&>th]:px-3 [&>th]:py-2 text-left">
              <th>Position</th>
              <th>Candidate</th>
              <th>Votes</th>
              <th>Share</th>
            </tr>
          </thead>
          <tbody>
            {positions.flatMap((pos) =>
              (pos.totals || []).map((t, idx) => (
                <tr
                  key={`${pos.id}-${idx}`}
                  className="border-t [&>td]:px-3 [&>td]:py-2"
                >
                  <td>{pos.title}</td>
                  <td>{t.name || `#${t.candidate_id}`}</td>
                  <td>{t.count}</td>
                  <td>{Math.round((t.share ?? 0) * 100)}%</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* summary lines – stacked vertically */}
      <div className="officer-results-summary">
        {totalVotes != null && (
          <div>
            <span className="officer-results-summary-label">
              Total votes:
            </span>{" "}
            <span>{totalVotes}</span>
          </div>
        )}
        {positionsCount != null && (
          <div>
            <span className="officer-results-summary-label">
              Positions:
            </span>{" "}
            <span>{positionsCount}</span>
          </div>
        )}
        {topShare != null && (
          <div>
            <span className="officer-results-summary-label">
              Top share:
            </span>{" "}
            <span>{topShare}%</span>
          </div>
        )}
      </div>
    </>
  );
}


function ExplainPanel({ payload }: { payload: ExplainDTO }) {
  const p = payload as any;
  const short: string = p?.short ?? p?.text ?? "";
  const long: string = p?.long ?? p?.text ?? "";

  // Split sentences where we see ". " followed by a capital letter
  // (e.g. "... (3/3). Director: ..."), to avoid breaking inside emails.
  const lines: string[] = short
    ? short
        .split(/\. (?=[A-Z])/)
        .map((s) => s.trim())
        .filter((s) => s.length > 0)
        .map((s) => (s.endsWith(".") ? s : s + "."))
    : [];

  return (
    <div className="text-sm officer-results-explain">
      {lines.length > 0 && (
        <div className="officer-results-explain-lines">
          {lines.map((line, idx) => {
            // Bold the position part before the first colon
            const match = line.match(/^([^:]+):(.*)$/);
            const positionLabel = match ? match[1].trim() : null;
            const restText = match ? match[2].trim() : line;

            return (
              <div key={idx} className="officer-results-explain-line">
                {positionLabel ? (
                  <>
                    <strong>{positionLabel}:</strong>{" "}
                    {restText}
                  </>
                ) : (
                  line
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Fallback: if no short text but a long explanation exists, show it straight */}
      {lines.length === 0 && long && (
        <pre className="officer-results-explain-long whitespace-pre-wrap text-xs mt-3">
          {long}
        </pre>
      )}

      {!short && !long && <div className="subtle">(no data)</div>}
    </div>
  );
}




/* ----- charts & CSV helpers ----- */

function PositionChart({ position }: { position: Position }) {
  const rows = useMemo(
    () =>
      (position.totals || []).map((t) => ({
        name: t.name,
        count: t.count,
      })),
    [position]
  );

  if (rows.length === 0) {
    return (
      <div className="card">
        <h3 className="officer-results-position-title mb-3">
          {position.title}
        </h3>
        <div className="no-votes">No votes yet.</div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="officer-results-position-header">
        <h3 className="officer-results-position-title">
          {position.title}
        </h3>
        <button
          className="officer-results-position-csv"
          onClick={() => {
            const csv = [
              ["Position", "Candidate", "Votes"],
              ...(position.totals || []).map((t) => [
                position.title,
                t.name,
                String(t.count),
              ]),
            ]
              .map((r) =>
                r
                  .map((v) => {
                    const s = String(v ?? "").replace(/"/g, '""');
                    return /[",\n]/.test(s) ? `"${s}"` : s;
                  })
                  .join(",")
              )
              .join("\r\n");
            try {
              const now = new Date();
              const ts = `${now.getFullYear()}${String(
                now.getMonth() + 1
              ).padStart(2, "0")}${String(now.getDate()).padStart(
                2,
                "0"
              )}-${String(now.getHours()).padStart(2, "0")}${String(
                now.getMinutes()
              ).padStart(2, "0")}`;
              downloadCsv(
                `results-position-${position.id}-${ts}.csv`,
                csv
              );
            } catch {
              const blob = new Blob([csv], {
                type: "text/csv;charset=utf-8",
              });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = `results-position-${position.id}.csv`;
              a.click();
              URL.revokeObjectURL(url);
            }
          }}
        >
          CSV
        </button>
      </div>

      <div style={{ width: "100%", minHeight: 280 }}>
        <ResponsiveContainer width="100%" aspect={2}>
          <BarChart
            data={rows}
            margin={{ top: 8, right: 16, left: 0, bottom: 8 }}
          >
            <CartesianGrid stroke="#e5e7eb" strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fill: "var(--muted-text)" }} />
            <YAxis
              tick={{ fill: "var(--muted-text)" }}
              allowDecimals={false}
            />
            <Tooltip />
            <Bar dataKey="count" fill="var(--brand)" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function makeClientCsv(data: Results) {
  const lines: string[] = [];
  lines.push("Position, Candidate, Votes");
  for (const p of data.positions) {
    for (const t of p.totals)
      lines.push(
        [csvq(p.title), csvq(t.name), String(t.count)].join(",")
      );
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
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function Loader({ text }: { text: string }) {
  return (
    <div className="officer-results-loader">
      <div className="animate-pulse subtle">{text}</div>
    </div>
  );
}
