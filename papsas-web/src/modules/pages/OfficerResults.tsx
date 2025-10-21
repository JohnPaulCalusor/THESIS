// src/modules/pages/OfficerResults.tsx
import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import Topbar from "../components/Topbar";
import { http } from "../lib/http";
import { ResponsiveContainer, BarChart, XAxis, YAxis, CartesianGrid, Tooltip, Bar } from "recharts";

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
  positions?: { id: number; title: string; totals: { candidate_id: number; name?: string; count: number }[] }[];
};

type Tot = { candidate_id: number; name: string; count: number };
type Position = { id: number; title: string; totals: Tot[] };
type Results = { election: { id: number; title?: string }; positions: Position[] };

/* ---------- page ---------- */
export default function OfficerResults() {
  const { id } = useParams();
  const [data, setData] = useState<Results | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<{ code: number; msg: string; body?: string } | null>(null);

  useEffect(() => {
    let cancel = false;
    (async () => {
      setLoading(true);
      setErr(null);
      try {
        const res = await http.get(`/api/elections/${id}/results`);
        if (cancel) return;
        const normalized = normalize(res.data, Number(id));
        setData(normalized);
      } catch (e: any) {
        if (cancel) return;
        const code = e?.response?.status ?? 0;
        const body = typeof e?.response?.data === "string" ? e.response.data : "";
        setErr({
          code,
          msg:
            code === 401 ? "Your session expired. Please sign in again."
          : code === 403 ? "Officers only."
          : code === 500 ? "Server error while loading results."
          : "Failed to load results.",
          body,
        });
      } finally {
        if (!cancel) setLoading(false);
      }
    })();
    return () => { cancel = true; };
  }, [id]);

  const downloadCsv = useCallback(async () => {
    if (!data) return;
    // 1) Try server CSV first
    try {
      const resp = await http.get(`/api/elections/${id}/results.csv`, { responseType: "blob" });
      const blob = new Blob([resp.data], { type: "text/csv;charset=utf-8" });
      saveBlob(blob, `results-election-${id}.csv`);
      return;
    } catch {
      // fall through to client CSV
    }
    // 2) Client-generated CSV (fallback)
    const csv = makeClientCsv(data);
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    saveBlob(blob, `results-election-${id}.csv`);
  }, [data, id]);

  if (loading) return <Loader text="Loading results…" />;

  if (err) {
    return (
      <div className="page">
        <Topbar />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="card" style={{ borderColor: "rgba(248,113,113,.4)", background: "rgba(248,113,113,.1)" }}>
            <h2 className="text-lg font-semibold">Failed to load results (HTTP {err.code || 0})</h2>
            <p className="mt-1"> {err.msg} </p>
            <button onClick={() => window.location.reload()} className="btn btn-primary mt-3">Retry</button>
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
    <div className="page">
      <Topbar />
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="mb-4 flex items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold">{data.election?.title ?? `Election #${id}`}</h1>
            <p className="subtle text-sm">Live tally</p>
          </div>
          <button onClick={downloadCsv} className="btn btn-primary">Download CSV</button>
        </div>

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
  const rows = useMemo(() => (position.totals || []).map(t => ({ name: t.name, count: t.count })), [position]);

  return (
    <div className="card">
      <h3 className="text-lg font-medium mb-3">{position.title}</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={rows} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
            <CartesianGrid stroke="#e5e7eb" strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fill: 'var(--muted)' }} />
            <YAxis tick={{ fill: 'var(--muted)' }} allowDecimals={false} />
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

/* tiny UI bit */
function Loader({ text }: { text: string }) {
  return (
    <div className="page grid place-items-center">
      <div className="animate-pulse subtle">{text}</div>
    </div>
  );
}
