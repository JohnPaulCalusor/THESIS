import { useEffect, useState, useMemo } from "react";
import { http } from "../lib/http";
import { useElection } from "../election/hooks/useElection";
import { useToast } from "../ui/Toast";
import { useAuth } from "../auth/AuthProvider";
import { postVote } from "../election/services/electionApi";
import type { VoteChoice, VoteRequestPayload } from "../election/services/electionApi";

type Choice = { candidacyId: number; candidateId: number; name: string; credentials?: string };
type Section = { id: number; title: string; options: Choice[] };
type BallotPositionPayload = { id?: string | number; title?: string; options?: Choice[] | unknown[]; choices?: Choice[] | unknown[] };
type BallotDebug = { tried: Array<{ url: string; status: number }>; winner?: string; payload?: unknown };
type BallotError = { response?: { status?: number; data?: { code?: string; message?: string } }; message?: string };

const extractOptions = (p: BallotPositionPayload): Choice[] => {
  if (Array.isArray(p.options) && p.options.length) return p.options as Choice[];
  if (Array.isArray(p.choices) && p.choices.length) return p.choices as Choice[];
  return [];
};

const buildSections = (payload: { positions?: BallotPositionPayload[] }) => {
  const pos = Array.isArray(payload.positions) ? payload.positions : [];
  return pos
    .map((p) => {
      const rawId = typeof p.id === "number" ? p.id : Number(p.id ?? -1);
      if (!Number.isFinite(rawId) || rawId < 0) return null;
      const options = extractOptions(p);
      if (!options.length) return null;
      return {
        id: rawId,
        title: p.title ?? "",
        options,
      };
    })
    .filter((sec): sec is Section => sec !== null);
};
export default function BallotPage() {
  const { election } = useElection();
  const { user } = useAuth();               // ← NEW
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ code: number; msg: string } | null>(null);
  const [choices, setChoices] = useState<Choice[]>([]);
  const [sections, setSections] = useState<Section[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [picks, setPicks] = useState<Record<number, number>>({});
  const [submitting, setSubmitting] = useState(false);
  // >>> PAPSAS v1.3 BEGIN
  const [voted, setVoted] = useState(false);
  // <<< PAPSAS v1.3 END
  const [debug, setDebug] = useState<BallotDebug>({ tried: [] });
  const toast = useToast();

  // ---- NEW: is the current user an admin or officer? ----
  const isPrivileged = useMemo(() => {
    if (!user) return false;
    // super-user → admin
    if (user.is_superuser) return true;
    // Django staff → officer / admin
    if (user.is_staff) return true;
    // role string (if your backend sends it)
    if (user.role && ["admin", "officer"].includes(user.role.toLowerCase())) return true;
    // groups array (if you use Django groups)
    if (Array.isArray(user.groups) && user.groups.some(g => ["admin", "officer"].includes(g.toLowerCase()))) return true;
    return false;
  }, [user]);
  // -------------------------------------------------------
  const effectiveId = election?.id?.toString();

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      setSections([]);
      setChoices([]);
      setSelected(null);
      if (!effectiveId) { setLoading(false); return; }
      const url = `elections/${effectiveId}/ballot`;
      try {
        const res = await http.get(url);
        if (cancelled) return;
        const payload = res.data || {};
        const secs = buildSections(payload);
        setSections(secs);
        setPicks({});
        setPicks({});
        if (secs.length === 0) {
          const list: Choice[] = Array.isArray(payload.choices) ? payload.choices : (Array.isArray(payload.atLarge) ? payload.atLarge : []);
          setChoices(list);
        }
        if (import.meta.env.DEV) setDebug({ tried: [{ url, status: 200 }], winner: url, payload });
      } catch (error) {
        const err = error as BallotError;
        const s = err.response?.status ?? 0;
        const payload = err.response?.data;
        if (!cancelled) {
          setError({ code: s, msg: messageForStatus(s, "Failed to load ballot.") });
          if (import.meta.env.DEV) setDebug({ tried: [{ url, status: s }], payload });
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [effectiveId]);

  async function submit() {
    if (!effectiveId) return;
    setError(null);
    const positionsPayload: VoteChoice[] = sections.length > 0
      ? sections.flatMap((sec) => {
          const candidacyId = picks[sec.id];
          if (!candidacyId) return [];
          return [{ position_id: sec.id, candidacy_id: candidacyId }];
        })
      : [];
    if (sections.length > 0 && !positionsPayload.length) {
      toast.error("Select at least one candidate per position.");
      return;
    }
    if (sections.length === 0 && !selected) {
      toast.error("Select a candidate before submitting.");
      return;
    }
    const payload: VoteRequestPayload = sections.length > 0
      ? { positions: positionsPayload }
      : { atLarge: [selected!] };
    setSubmitting(true);
    try {
      if (import.meta.env.DEV) {
        console.log("DEBUG vote payload", payload);
        console.log("DEBUG vote payload JSON", JSON.stringify(payload));
      }
      await postVote(Number(effectiveId), payload);
      toast.success("Vote submitted");
      setVoted(true);
      setPicks({});
      setSelected(null);
      try {
        const res = await http.get(`elections/${effectiveId}/ballot`);
        const payload = res.data || {};
        const secs = buildSections(payload);
        setSections(secs);
        setPicks({});
        if (secs.length === 0) {
          setChoices(Array.isArray(payload.choices) ? payload.choices : (Array.isArray(payload.atLarge) ? payload.atLarge : []));
        } else {
          setChoices([]);
        }
      } catch {
        // ignore refresh errors after vote submission
      }
    } catch (error) {
      const err = error as BallotError;
      const status = err.response?.status;
      const code = err.response?.data?.code;
      if (status === 403) setError({ code: 403, msg: messageForStatus(403, "") });
      else if (status === 409 || code === "ALREADY_VOTED") setError({ code: 409, msg: messageForStatus(409, "") });
      else {
        const message = err.response?.data?.message || err.message || "We couldn't submit your vote. Please try again.";
        toast.error(message);
      }
    } finally {
      setSubmitting(false);
    }
  }

  if (!effectiveId) return <Blocked title="No active election." sub="There is no current election to vote on." />;
  if (loading) return <Loader text="Loading ballot…" />;

  if (error?.code === 403) return <Blocked title="Voting closed." sub="This election is not open for voting. If you believe this is an error, contact your officer." />;
  if (error?.code === 409) return <Blocked title="You already voted." sub="Your vote has been recorded. You cannot vote again for this election." />;
  if (error && ![403, 409].includes(error.code)) return <DevError code={error.code} msg={error.msg} debug={debug} />;

  const empty = sections.length === 0 && choices.length === 0;
  const picksCount = Object.keys(picks).length;
  const hasPositionSelections = sections.length > 0 && picksCount === sections.length;
  const hasNonPositionSelection = sections.length === 0 && Boolean(selected);
  const canSubmit = hasPositionSelections || hasNonPositionSelection;

  return (
    <div>
      <div className="page-ballot">{/* ← add this wrapper */}
        <div className="ballot-wrap max-w-2xl mx-auto px-4 py-3"></div>
        <h1 className="text-2xl font-semibold mb-4">BALLOT</h1>
        <p className="subtle mb-6">Select one candidate.</p>
        {/* >>> PAPSAS v1.3 BEGIN */}
        {voted && (
          <div className="card mb-6" style={{ borderColor: "rgba(16,185,129,.4)", background: "rgba(16,185,129,.1)" }}>
            <div className="font-medium">Your vote was submitted.</div>
            <div className="text-sm subtle">You cannot modify your vote for this election.</div>
          </div>
        )}
        {/* <<< PAPSAS v1.3 END */}

        {empty && <div className="callout callout-warn mb-6">No choices returned. If this user already voted, this is expected.</div>}

        {!empty && (
          <>
            {sections.length > 0 ? (
              sections.map((sec) => (
                <fieldset key={sec.id} className="card mb-6">
                  <legend className="px-2 text-lg font-medium">{sec.title}</legend>
                  <div className="mt-2 space-y-2">
                    {sec.options.map((c) => (
                      <label
                        key={c.candidacyId}
                        className="flex items-start gap-3 rounded-lg px-3 py-2 hover:bg-[var(--surface)] border"
                        style={{ borderColor: "var(--ring)", background: "#fff" }}
                      >
                        <input
                          type="radio"
                          name={`position-${sec.id}`}
                          checked={picks[sec.id] === c.candidacyId}
                          onChange={() => {
                            if (!c.candidacyId) return;
                            setPicks((prev) => ({ ...prev, [sec.id]: c.candidacyId }));
                          }}
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
              ))
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
                          onChange={() => {
                            if (c.candidacyId) setSelected(c.candidacyId);
                          }}
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

        <button onClick={submit} disabled={!canSubmit || submitting || voted} className="btn btn-primary w-full">
          Submit vote
        </button>


        {/* DEBUG PANEL – ONLY FOR ADMINS / OFFICERS */}
        {import.meta.env.DEV && isPrivileged && (
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
    <div className="flex min-h-screen items-center justify-center bg-white">
      <div className="animate-pulse text-lg font-medium text-[var(--text-muted)]">
        {text}
      </div>
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
function DevError({ code, msg, debug }: { code: number; msg: string; debug?: BallotDebug | null }) {
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
