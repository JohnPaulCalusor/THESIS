// src/modules/pages/OfficerResults.tsx
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useToast } from "../ui/Toast";
import { http } from "../lib/http";
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
  positions?: {
    id: number; title: string;
    totals: { candidate_id: number; name?: string; count: number }[];
  }[];
};

type Tot = { candidate_id: number; name: string; count: number };
type Position = { id: number; title: string; totals: Tot[] };
type Results = { election: { id: number; title?: string }; positions: Position[] };

/* ---------- page ---------- */
export default function OfficerResults() {
  const { election } = useElection();
  const [data, setData] = useState<Results | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<{ code: number; msg: string; body?: string } | null>(null);
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);
  const pollRef = useRef<number | null>(null);
  const toast = useToast();
  const [panel, setPanel] = useState<{ kind: "analytics" | "explain"; payload: any } | null>(null);

  const effectiveId = election?.id?.toString();

  const fetchOnce = useCallback(async () => {
    setErr(null);
    try {
      if (!effectiveId) throw new Error("No election id");
      const res = await http.get(`/api/elections/${effectiveId}/results`);
      const normalized = normalize(res.data, Number(effectiveId));
      setData(normalized);
      setUpdatedAt(new Date());
    } catch (e: any) {
      const code = e?.response?.status ?? 0;
      const body = typeof e?.response?.data === "string" ? e.response.data : "";
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

  useEffect(() => {
    let cancel = false;
    setLoading(true);
    fetchOnce();

    // Light polling so tallies feel live (every 5s in dev, 10s in prod)
    const intervalMs = import.meta.env.DEV ? 5000 : 10000;
    pollRef.current = window.setInterval(() => {
      if (!cancel) fetchOnce();
    }, intervalMs);

    return () => {
      cancel = true;
      if (pollRef.current) window.clearInterval(pollRef.current);
    };
  }, [fetchOnce]);

  const downloadCsv = useCallback(async () => {
    if (!data) return;
    try {
      if (!effectiveId) return;
      const resp = await http.get(`/api/elections/${effectiveId}/results.csv`, { responseType: "blob" });
      const blob = new Blob([resp.data], { type: "text/csv;charset=utf-8" });
      saveBlob(blob, `results-election-${effectiveId}.csv`);
      return;
    } catch {
      // fallback to client CSV
    }
    const csv = makeClientCsv(data);
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    saveBlob(blob, `results-election-${effectiveId}.csv`);
  }, [data, effectiveId]);

  const onAnalytics = useCallback(async () => {
    try {
      if (!effectiveId) return;
      const res = await http.get(`/api/elections/${effectiveId}/analytics`);
      setPanel({ kind: "analytics", payload: res.data });
    } catch (e: any) {
      toast.error(e?.response?.data?.message || e?.message || "Failed to load analytics");
    }
  }, [effectiveId, toast]);

  const onExplain = useCallback(async () => {
    try {
      if (!effectiveId) return;
      const res = await http.post(`/api/elections/${effectiveId}/explain`, { style: "short" });
      setPanel({ kind: "explain", payload: res.data });
    } catch (e: any) {
      toast.error(e?.response?.data?.message || e?.message || "Failed to load explanation");
    }
  }, [effectiveId, toast]);

  if (!effectiveId) return <Loader text="No active election." />;
  if (loading) return <Loader text="Loading results?" />;
  if (err) {
    return (
      <div>
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
    <div>
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="mb-4 flex items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold">{data.election?.title ?? `Election #${effectiveId}`}</h1>
            <p className="subtle text-sm">Live tally</p>
            {updatedAt && (
              <p className="text-xs text-[var(--muted)]">
                Updated {updatedAt.toLocaleTimeString()}
              </p>
            )}
          </div>
          <div className="flex gap-2">
            <button onClick={fetchOnce} className="btn btn-secondary">Refresh</button>
            <button onClick={downloadCsv} className="btn btn-primary">Download CSV</button>
            <button onClick={onAnalytics} className="btn btn-secondary">Analytics</button>
            <button onClick={onExplain} className="btn btn-secondary">Explain</button>
          </div>
        </div>

        {panel && (
          <div className="card mb-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-medium">{panel.kind === "analytics" ? "Analytics" : "Explain"}</h3>
              <button className="text-sm underline" onClick={() => setPanel(null)}>Close</button>
            </div>
            {panel.kind === "analytics" ? (
              <div className="overflow-auto">
                <table className="min-w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr className="[&>th]:px-3 [&>th]:py-2 text-left">
                      <th>Position</th>
                      <th>Candidate</th>
                      <th>Votes</th>
                      <th>Share</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(panel.payload?.positions || []).flatMap((p: any) => (
                      (p.totals || []).map((t: any, idx: number) => (
                        <tr key={`${p.id}-${idx}`} className="border-t [&>td]:px-3 [&>td]:py-2">
                          <td>{p.title}</td>
                          <td>{t.name || `#${t.candidate_id}`}</td>
                          <td>{t.count}</td>
                          <td>{Math.round((t.share || 0) * 100)}%</td>
                        </tr>
                      ))
                    ))}
                  </tbody>
                </table>
                {panel.payload?.meta?.totalVotes != null && (
                  <div className="text-xs subtle mt-2">Total votes: {panel.payload.meta.totalVotes}</div>
                )}
              </div>
            ) : (
              <pre className="whitespace-pre-wrap text-sm">{panel.payload?.text || "(no data)"}</pre>
            )}
          </div>
        )}

        <div className="space-y-8">
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
      totals: (p.totals || []).map(t => ({
        candidate_id: Number(t.candidate_id),
        name: t.name || `#${t.candidate_id}`,
        count: Number(t.count || 0),
      })),
    }));
    return {
      election: raw.election || { id: electionId, title: `Election #${electionId}` },
      positions,
    };
  }

  const totals = (raw?.results || []).map((r) => ({
    candidate_id: Number(r.candidacyId ?? r.candidateId ?? r.candidate_id ?? 0),
    name: r.name || `#${r.candidacyId ?? r.candidateId ?? r.candidate_id ?? ""}`,
    count: Number(r.votes ?? r.count ?? 0),
  }));
  return {
    election: raw?.election || { id: electionId, title: `Election #${electionId}` },
    positions: [
      { id: electionId, title: raw?.election?.title || `Election #${electionId}`, totals },
    ],
  };
}

function PositionChart({ position }: { position: Position }) {
  const rows = useMemo(
    () => (position.totals || []).map(t => ({ name: t.name, count: t.count })),
    [position]
  );

  if (rows.length === 0) {
    return (
      <div className="card">
        <h3 className="text-lg font-medium mb-3">{position.title}</h3>
        <div className="rounded-md border border-[var(--border)] p-6 text-sm text-[var(--muted)] bg-[var(--card)]">
          No votes yet.
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="text-lg font-medium mb-3">{position.title}</h3>
      <div style={{ width: "100%", minHeight: 280 }}>
        <ResponsiveContainer width="100%" aspect={2}>
          <BarChart data={rows} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
            <CartesianGrid stroke="#e5e7eb" strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fill: "var(--muted)" }} />
            <YAxis tick={{ fill: "var(--muted)" }} allowDecimals={false} />
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
    <div className="page grid place-items-center">
      <div className="animate-pulse subtle">{text}</div>
    </div>
  );
}









