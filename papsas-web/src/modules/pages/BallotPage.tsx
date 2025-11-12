import React, { useEffect, useState } from "react";
import { http } from "../lib/http";
import { useElection } from "../election/hooks/useElection";
import { useToast } from "../ui/Toast";

type Choice = {
  candidacyId: number;
  candidateId: number;
  name: string;
  credentials?: string;
};

type Section = {
  id: number;
  title: string;
  winners: number;        // from API positions[].winners (nullable → 1)
  options: Choice[];
};

export default function BallotPage() {
  const { election } = useElection();
  const toast = useToast();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ code: number; msg: string } | null>(null);

  // At-large fallback
  const [choices, setChoices] = useState<Choice[]>([]);

  // Position mode
  const [sections, setSections] = useState<Section[]>([]);
  const [byPosition, setByPosition] = useState<Record<number, number | undefined>>({}); // position_id -> candidacyId

  // Common state
  const [selected, setSelected] = useState<number | null>(null); // at-large only
  const [submitting, setSubmitting] = useState(false);
  const [voted, setVoted] = useState(false); // freeze controls after success
  const [debug, setDebug] = useState<{ tried: Array<{ url: string; status: number }>; winner?: string; payload?: any }>({ tried: [] });

  const effectiveId = election?.id?.toString();
  const positionMode = sections.length > 0; // true when API returns positions[]

  useEffect(() => {
    let cancelled = false;

    (async () => {
      setLoading(true);
      setError(null);
      setSections([]);
      setChoices([]);
      setSelected(null);
      setByPosition({});
      if (!effectiveId) {
        setLoading(false);
        return;
      }

      const url = `elections/${effectiveId}/ballot`;
      try {
        const res = await http.get(url);
        if (cancelled) return;
        const payload = res.data || {};

        // Build sections from positions (position mode)
        const pos = Array.isArray(payload.positions) ? payload.positions : [];
        const secs: Section[] = pos
          .map((p: any) => ({
            id: Number(p.id),
            title: String(p.title ?? "Untitled"),
            winners: Math.max(1, Number((p as { winners?: number | null }).winners ?? 1) || 1),
            options: (
              (Array.isArray(p.options) && p.options.length ? p.options : (Array.isArray(p.choices) ? p.choices : [])) || []
            ) as Choice[],
          }))
          .filter((s: Section) => Array.isArray(s.options) && s.options.length > 0);

        setSections(secs);

        if (secs.length === 0) {
          // Fallback: at-large
          const list: Choice[] = Array.isArray(payload.choices)
            ? payload.choices
            : (Array.isArray(payload.atLarge) ? payload.atLarge : []);
          setChoices(list);
        }

        if (import.meta.env.DEV) setDebug({ tried: [{ url, status: 200 }], winner: url, payload });
      } catch (e: any) {
        const s = e?.response?.status ?? 0;
        const payload = e?.response?.data;
        if (!cancelled) {
          setError({ code: s, msg: messageForStatus(s, "Failed to load ballot.") });
          if (import.meta.env.DEV) setDebug({ tried: [{ url, status: s }], payload });
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [effectiveId]);

  async function submit() {
    if (!effectiveId) return;

    // Guard: must have some selection
    if (positionMode) {
      const hasAny = Object.values(byPosition).some((cid) => typeof cid === "number");
      if (!hasAny) return;
    } else {
      if (!selected) return;
    }

    setSubmitting(true);
    setError(null);

    try {
      if (positionMode) {
        // Build positions payload from byPosition
        const picks = Object.entries(byPosition)
          .filter(([, cid]) => typeof cid === "number")
          .map(([pid, cid]) => ({
            position_id: Number(pid),
            candidacy_id: Number(cid),
          }));

        await http.post(`elections/${effectiveId}/vote`, { positions: picks });
      } else {
        await http.post(`elections/${effectiveId}/vote`, { candidacyId: selected });
      }

      toast.success("Vote submitted");
      setVoted(true); // freeze controls

      // Refresh the ballot after success to reflect server state
      try {
        const res = await http.get(`elections/${effectiveId}/ballot`);
        const payload = res.data || {};
        const pos = Array.isArray(payload.positions) ? payload.positions : [];
        const secs: Section[] = pos
          .map((p: any) => ({
            id: Number(p.id),
            title: String(p.title ?? "Untitled"),
            winners: Math.max(1, Number((p as { winners?: number | null }).winners ?? 1) || 1),
            options: (
              (Array.isArray(p.options) && p.options.length ? p.options : (Array.isArray(p.choices) ? p.choices : [])) || []
            ) as Choice[],
          }))
          .filter((s: Section) => Array.isArray(s.options) && s.options.length > 0);
          
        setSections(secs);

        if (secs.length === 0) {
          setChoices(Array.isArray(payload.choices) ? payload.choices : (Array.isArray(payload.atLarge) ? payload.atLarge : []));
        } else {
          setChoices([]);
        }

        setSelected(null);
        setByPosition({});
      } catch {
        /* ignore */
      }
    } catch (err: any) {
      const s = err?.response?.status;
      const data = err?.response?.data;

      if (data?.code === "TOO_MANY_FOR_POSITION" && s === 400) {
        const allowed = typeof data?.allowed === "number" ? data.allowed : "?";
        toast.error(`Too many selected for a position (allowed: ${allowed}).`);
      } else if (data?.code === "WRONG_MODE" && s === 400) {
        toast.error("This election uses position-based voting.");
      } else if (s === 403) {
        setError({ code: 403, msg: messageForStatus(403, "") });
      } else if (s === 409) {
        setError({ code: 409, msg: messageForStatus(409, "") });
      } else {
        toast.error("We couldn't submit your vote. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  // ---- Rendering helpers ----------------------------------------------------

  if (!effectiveId) return <Blocked title="No active election." sub="There is no current election to vote on." />;
  if (loading) return <Loader text="Loading ballot…" />;

  if (error?.code === 403)
    return <Blocked title="Voting closed." sub="This election is not open for voting. If you believe this is an error, contact your officer." />;
  if (error?.code === 409)
    return <Blocked title="You already voted." sub="Your vote has been recorded. You cannot vote again for this election." />;
  if (error && ![403, 409].includes(error.code)) return <DevError code={error.code} msg={error.msg} debug={debug} />;

  const empty = !positionMode && choices.length === 0;

  const canSubmit = positionMode
    ? Object.values(byPosition).some((cid) => typeof cid === "number")
    : Boolean(selected);

  return (
    <div>
      <div className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-semibold mb-4">Ballot</h1>
        <p className="subtle mb-6">
          {positionMode ? "Pick one per position." : "Select one candidate."}
        </p>

        {voted && (
          <div className="card mb-6" style={{ borderColor: "rgba(16,185,129,.4)", background: "rgba(16,185,129,.1)" }}>
            <div className="font-medium">Your vote was submitted.</div>
            <div className="text-sm subtle">You cannot modify your vote for this election.</div>
          </div>
        )}

        {positionMode && (
          <div
            className="card mb-6"
            style={{ background: "#eef2ff", borderColor: "#c7d2fe" }}
          >
            <div className="text-sm" style={{ color: "#4338ca" }}>
              Position-based voting — choose up to the allowed number per position (shown as “Max”).
            </div>
          </div>
        )}

        {empty && <div className="callout callout-warn mb-6">No choices returned. If this user already voted, this is expected.</div>}

        {!empty && (
          <>
            {positionMode ? (
              sections.map((sec) => {
                const picked = byPosition[sec.id];

                return (
                  <fieldset key={sec.id} className="card mb-6">
                    <legend className="px-2 text-lg font-medium">{sec.title}</legend>
                    <div className="subtle mb-2">Max: {sec.winners}</div>

                    <div className="mt-2 space-y-2">
                      {sec.options.map((c) => {
                        const isSelected = picked === c.candidacyId;
                        return (
                          <label
                            key={c.candidacyId}
                            className="flex items-start gap-3 rounded-lg px-3 py-2 hover:bg-[var(--surface)] border"
                            style={{ borderColor: "var(--ring)", background: "#fff" }}
                          >
                            <input
                              type="radio"
                              name={`choice-pos-${sec.id}`} // unique group per position
                              checked={isSelected}
                              onChange={() =>
                                setByPosition((prev) => ({
                                  ...prev,
                                  [sec.id]: c.candidacyId,
                                }))
                              }
                              disabled={voted}
                              className="size-4 mt-1"
                              style={{ accentColor: "var(--brand)" }}
                            />
                            <div>
                              <div className="font-medium">{c.name}</div>
                              {c.credentials && <div className="text-sm subtle">{c.credentials}</div>}
                            </div>
                          </label>
                        );
                      })}
                    </div>
                  </fieldset>
                );
              })
            ) : (
              <fieldset className="card mb-6">
                <legend className="px-2 text-lg font-medium">Candidates</legend>
                <div className="mt-2 space-y-2">
                  {choices.map((c) => (
                    <label
                      key={c.candidacyId}
                      className="flex items-start gap-3 rounded-lg px-3 py-2 hover:bg-[var(--surface)] border"
                      style={{ borderColor: "var(--ring)", background: "#fff" }}
                    >
                      <input
                        type="radio"
                        name="choice-global"
                        checked={selected === c.candidacyId}
                        onChange={() => setSelected(c.candidacyId)}
                        disabled={voted}
                        className="size-4 mt-1"
                        style={{ accentColor: "var(--brand)" }}
                      />
                      <div>
                        <div className="font-medium">{c.name}</div>
                        {c.credentials && <div className="text-sm subtle">{c.credentials}</div>}
                      </div>
                    </label>
                  ))}
                </div>
              </fieldset>
            )}
          </>
        )}

        <button
          onClick={submit}
          disabled={!canSubmit || submitting || voted}
          className="btn btn-primary w-full"
        >
          Submit vote
        </button>

        {import.meta.env.DEV && (
          <details className="mt-8 card">
            <summary className="cursor-pointer">Debug</summary>
            <pre className="mt-2 text-xs whitespace-pre-wrap">{JSON.stringify(debug, null, 2)}</pre>
          </details>
        )}
      </div>
    </div>
  );
}

function messageForStatus(code: number, fallback: string) {
  if (code === 403) return "This election is not open for voting. If you believe this is an error, contact your officer.";
  if (code === 409) return "Your vote has been recorded. You cannot vote again for this election.";
  if (code === 404) return "Ballot endpoint not found (404).";
  return fallback || `Request failed (HTTP ${code}).`;
}

function Loader({ text }: { text: string }) {
  return (
    <div className="page grid place-items-center">
      <div className="animate-pulse subtle">{text}</div>
    </div>
  );
}
function Blocked({ title, sub }: { title: string; sub: string }) {
  return (
    <div className="page grid place-items-center px-4">
      <div className="card text-center max-w-lg w-full">
        <h1 className="text-2xl font-semibold">{title}</h1>
        <p className="subtle mt-2">{sub}</p>
      </div>
    </div>
  );
}
function DevError({ code, msg, debug }: { code: number; msg: string; debug?: any }) {
  return (
    <div className="page grid place-items-center px-4">
      <div className="card" style={{ borderColor: "rgba(248,113,113,.4)", background: "rgba(248,113,113,.1)" }}>
        <h2 className="text-xl font-semibold">Error loading ballot (HTTP {code})</h2>
        <p className="mt-2">{msg}</p>
        {import.meta.env.DEV && debug && (
          <details className="mt-3">
            <summary className="cursor-pointer">Show debug</summary>
            <pre className="mt-2 text-xs whitespace-pre-wrap">{JSON.stringify(debug, null, 2)}</pre>
          </details>
        )}
      </div>
    </div>
  );
}
