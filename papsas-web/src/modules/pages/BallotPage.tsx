import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Topbar from "../components/Topbar";
import { http } from "../lib/http";

type Choice = { candidacyId: number; candidateId: number; name: string; credentials?: string };

export default function BallotPage() {
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ code: number; msg: string } | null>(null);
  const [choices, setChoices] = useState<Choice[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [submitMsg, setSubmitMsg] = useState("");
  const [debug, setDebug] = useState<{ tried: Array<{ url: string; status: number }>; winner?: string; payload?: any }>({ tried: [] });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      setSubmitMsg("");
      setSelected(null);
      const url = `/api/elections/${id}/ballot`;
      try {
        const res = await http.get(url);
        if (cancelled) return;
        const list: Choice[] = Array.isArray(res.data?.choices) ? res.data.choices : [];
        setChoices(list);
        if (import.meta.env.DEV) setDebug({ tried: [{ url, status: 200 }], winner: url, payload: res.data });
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
  }, [id]);

  async function submit() {
    if (!selected) return;
    setSubmitMsg("");
    setError(null);
    try {
      await http.post(`/api/elections/${id}/vote`, { candidacyId: selected });
      setSubmitMsg("Vote submitted!");
      try {
        const res = await http.get(`/api/elections/${id}/ballot`);
        setChoices(Array.isArray(res.data?.choices) ? res.data.choices : []);
      } catch {}
    } catch (e: any) {
      const s = e?.response?.status;
      if (s === 403) setError({ code: 403, msg: messageForStatus(403, "") });
      else if (s === 409) setError({ code: 409, msg: messageForStatus(409, "") });
      else setSubmitMsg("We couldn’t submit your vote. Please try again.");
    }
  }

  if (loading) return <Loader text="Loading ballot…" />;

  if (error?.code === 403) return <Blocked title="Voting closed." sub="This election is not open for voting. If you believe this is an error, contact your officer." />;
  if (error?.code === 409) return <Blocked title="You already voted." sub="Your vote has been recorded. You cannot vote again for this election." />;
  if (error && ![403, 409].includes(error.code)) return <DevError code={error.code} msg={error.msg} debug={debug} />;

  const empty = choices.length === 0;

  return (
    <div className="page">
      <Topbar />
      <div className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-semibold mb-2">Ballot</h1>
        <p className="subtle mb-6">Select one candidate.</p>

        {empty && <div className="callout callout-warn mb-6">No choices returned. If this user already voted, this is expected.</div>}

        {!empty && (
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
                    name="choice"
                    checked={selected === c.candidacyId}
                    onChange={() => setSelected(c.candidacyId)}
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

        <button onClick={submit} disabled={empty || !selected} className="btn btn-primary w-full">
          Submit vote
        </button>

        {submitMsg && <p role="status" className="mt-3 text-sm subtle">{submitMsg}</p>}

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
