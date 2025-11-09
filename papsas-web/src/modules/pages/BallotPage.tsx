import { useEffect, useState } from "react";
import { http } from "../lib/http";
import { useElection } from "../election/hooks/useElection";
import { useToast } from "../ui/Toast";

type Choice = { candidacyId: number; candidateId: number; name: string; credentials?: string };
type Section = { id: string | number; title: string; options: Choice[] };

export default function BallotPage() {
  const { election } = useElection();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ code: number; msg: string } | null>(null);
  const [choices, setChoices] = useState<Choice[]>([]);
  const [sections, setSections] = useState<Section[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);
  // >>> PAPSAS v1.3 BEGIN
  const [voted, setVoted] = useState(false);
  // <<< PAPSAS v1.3 END
  const [debug, setDebug] = useState<{ tried: Array<{ url: string; status: number }>; winner?: string; payload?: any }>({ tried: [] });
  const toast = useToast();

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
        const pos = Array.isArray(payload.positions) ? payload.positions : [];
        const secs: Section[] = pos
          .map((p: any) => ({ id: p.id, title: p.title, options: Array.isArray(p.options) && p.options.length ? p.options : (Array.isArray(p.choices) ? p.choices : []) }))
          .filter((s: Section) => Array.isArray(s.options) && s.options.length > 0);
        setSections(secs);
        if (secs.length === 0) {
          const list: Choice[] = Array.isArray(payload.choices) ? payload.choices : (Array.isArray(payload.atLarge) ? payload.atLarge : []);
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
    return () => { cancelled = true; };
  }, [effectiveId]);

  async function submit() {
    if (!selected) return;
    setError(null);
    try {
      if (!effectiveId) return;
      await http.post(`elections/${effectiveId}/vote`, { candidacyId: selected });
      toast.success("Vote submitted");
      // >>> PAPSAS v1.3 BEGIN
      // Freeze controls and show success banner
      setVoted(true);
      // <<< PAPSAS v1.3 END
      try {
        const res = await http.get(`elections/${effectiveId}/ballot`);
        const payload = res.data || {};
        const pos = Array.isArray(payload.positions) ? payload.positions : [];
        const secs: Section[] = pos
          .map((p: any) => ({ id: p.id, title: p.title, options: Array.isArray(p.options) && p.options.length ? p.options : (Array.isArray(p.choices) ? p.choices : []) }))
          .filter((s: Section) => Array.isArray(s.options) && s.options.length > 0);
        setSections(secs);
        if (secs.length === 0) {
          setChoices(Array.isArray(payload.choices) ? payload.choices : (Array.isArray(payload.atLarge) ? payload.atLarge : []));
        } else {
          setChoices([]);
        }
        setSelected(null);
      } catch {}
    } catch (e: any) {
      const s = e?.response?.status;
      if (s === 403) setError({ code: 403, msg: messageForStatus(403, "") });
      else if (s === 409) setError({ code: 409, msg: messageForStatus(409, "") });
      else toast.error("We couldn't submit your vote. Please try again.");
      setSubmitting(false);
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

  return (
    <div>
      <div className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-semibold mb-4">Ballot</h1>
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

        <button onClick={submit} disabled={empty || !selected || submitting || voted} className="btn btn-primary w-full">
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
