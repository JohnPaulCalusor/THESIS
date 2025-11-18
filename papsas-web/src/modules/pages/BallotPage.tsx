// src/modules/pages/BallotPage.tsx
import React, { useEffect, useState } from "react";
import { http } from "../lib/http";
import { useElection } from "../election/hooks/useElection";
import { useAuth } from "../auth/AuthProvider";
import { useToast } from "../ui/Toast";
import "./BallotPage.css";

import { postVote } from "../election/services/electionApi";
import type { VoteChoice, VoteRequestPayload } from "../election/services/electionApi";
import { isAdminUser } from "../auth/roles";

/* =========================
   Types
   ========================= */
type Choice = {
  candidacyId: number;
  candidateId: number;
  name: string;
  credentials?: string | string[];
  photoUrl?: string;

  // Extra fields the backend might use
  bio?: string | null;
  platform?: string | null;
  description?: string | null;
  summary?: string | null;
};

type Section = { id: number; title: string; options: Choice[] };

type BallotPositionPayload = {
  id?: string | number;
  title?: string;
  options?: Choice[] | unknown[];
  choices?: Choice[] | unknown[];
};

type BallotDebug = {
  tried: Array<{ url: string; status: number }>;
  winner?: string;
  payload?: unknown;
};

type BallotError = {
  response?: { status?: number; data?: { code?: string; message?: string } };
  message?: string;
};

/* =========================
   Helpers
   ========================= */
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
      return { id: rawId, title: p.title ?? "", options };
    })
    .filter((sec): sec is Section => sec !== null);
};

function initialsFrom(name: string) {
  const base = (name || "").split("@")[0];
  const parts = base.trim().split(/\s+/).slice(0, 2);
  return parts.map((p) => p[0]?.toUpperCase() || "").join("") || "•";
}

function pickCredSource(c: Choice): unknown {
  // Prefer explicit credentials; fall back to other likely fields
  return (
    c.credentials ??
    c.bio ??
    c.platform ??
    c.description ??
    c.summary ??
    null
  );
}

function normalizeCreds(val: unknown): string[] {
  if (Array.isArray(val)) {
    return val
      .map(String)
      .map((s) => s.trim())
      .filter(Boolean);
  }
  if (typeof val === "string") {
    return val
      .split(/\r?\n|;|•|·/)
      .map((s) => s.trim())
      .filter(Boolean);
  }
  return [];
}

/* =========================
   Small UI bits
   ========================= */
function Avatar({
  src,
  name,
  size = 64,
  radius = 50,
}: {
  src?: string;
  name: string;
  size?: number;
  radius?: number;
}) {
  const initials = initialsFrom(name);
  const wrapStyle: React.CSSProperties = {
    width: size,
    height: size,
    borderRadius: radius,
    overflow: "hidden",
    display: "inline-grid",
    placeItems: "center",
    fontWeight: 700,
    letterSpacing: ".5px",
    background: "#e5e7eb",
    color: "#374151",
    flex: "0 0 auto",
  };

  return (
    <span className="ballot-avatar" style={wrapStyle} aria-hidden={src ? undefined : true}>
      {src ? (
        <img
          src={src}
          alt=""
          style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
        />
      ) : (
        initials
      )}
    </span>
  );
}

function OptionRow({
  c,
  checked,
  name,
  onSelect,
  voted,
}: {
  c: Choice;
  checked: boolean;
  name: string;
  onSelect: () => void;
  voted: boolean;
}) {
  const creds = normalizeCreds(pickCredSource(c));

  return (
    <label className="ep-candidate block">
      {/* Outer flex row so radio is perfectly centered vertically */}
      <div className="flex items-center gap-4">
        {/* Radio */}
        <div className="ep-radio-wrap flex items-center justify-center flex-none">
          <input
            type="radio"
            name={name}
            checked={checked}
            onChange={onSelect}
            disabled={voted}
            className="size-5"
            style={{ accentColor: "var(--brand-primary)" }}
          />
        </div>

        {/* Avatar + content */}
        <div className="flex items-center gap-4 flex-1 min-w-0">
          <Avatar src={c.photoUrl} name={c.name} size={48} radius={9999} />

          {/* Name + credentials */}
          <div className="flex-1 min-w-0">
            <div className="font-semibold text-base leading-tight break-words">
              {c.name}
            </div>

            {creds.length > 0 && (
              <details
                className="ep-cred"
                onClick={(e) => e.stopPropagation()}
                onMouseDown={(e) => e.stopPropagation()}
                onKeyDown={(e) => e.stopPropagation()}
              >
                {/* No emoji/icon here, just the text */}
                <summary className="text-sm text-gray-500 hover:text-gray-700 cursor-pointer">
                  View Credentials
                </summary>
                <ul className="ep-cred-list mt-2 space-y-1 text-sm text-gray-600">
                  {creds.map((line, i) => (
                    <li key={i} className="list-disc ml-4">
                      {line}
                    </li>
                  ))}
                </ul>
              </details>
            )}
          </div>
        </div>
      </div>
    </label>
  );
}

/* =========================
   Page
   ========================= */
export default function BallotPage() {
  const { election } = useElection();
  const { user } = useAuth();
  const showDebug = import.meta.env.DEV && !!user && isAdminUser(user);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ code: number; msg: string } | null>(null);
  const [choices, setChoices] = useState<Choice[]>([]);
  const [sections, setSections] = useState<Section[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [picks, setPicks] = useState<Record<number, number>>({});
  const [submitting, setSubmitting] = useState(false);
  const [voted, setVoted] = useState(false);
  const [debug, setDebug] = useState<BallotDebug>({ tried: [] });
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

      if (!effectiveId) {
        setLoading(false);
        return;
      }

      const url = `elections/${effectiveId}/ballot`;

      try {
        const res = await http.get(url);
        if (cancelled) return;

        const payload = res.data || {};
        const secs = buildSections(payload);

        const baseList: Choice[] =
          secs.length === 0
            ? Array.isArray((payload as any).choices)
              ? ((payload as any).choices as Choice[])
              : Array.isArray((payload as any).atLarge)
              ? ((payload as any).atLarge as Choice[])
              : []
            : [];

        setSections(secs);
        setChoices(baseList);
        setPicks({});

        if (import.meta.env.DEV) {
          setDebug({
            tried: [{ url, status: 200 }],
            winner: url,
            payload,
          });
          if (secs[0]?.options?.[0]) {
             
            console.debug("Ballot sample candidate:", secs[0].options[0]);
          }
        }
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

    return () => {
      cancelled = true;
    };
  }, [effectiveId]);

  async function submit() {
    if (!effectiveId) return;
    setError(null);

        // Count how many positions are filled
    const filledPositionsCount = sections.reduce((count, sec) => {
      return typeof picks[sec.id] === "number" ? count + 1 : count;
    }, 0);

    const positionsPayload: VoteChoice[] =
      sections.length > 0
        ? sections.flatMap((sec) => {
            const candidacyId = picks[sec.id];
            if (!candidacyId) return [];
            return [{ position_id: sec.id, candidacy_id: candidacyId }];
          })
        : [];

    // Position-based voting: require ALL positions to be filled
    if (sections.length > 0 && filledPositionsCount < sections.length) {
      toast.error("Please select a candidate for every position.");
      return;
    }

    // At-large voting: require one candidate
    if (sections.length === 0 && !selected) {
      toast.error("Select a candidate before submitting.");
      return;
    }

    const payload: VoteRequestPayload =
      sections.length > 0 ? { positions: positionsPayload } : { atLarge: [selected!] };

    setSubmitting(true);
    setError(null);

    try {
      await postVote(Number(effectiveId), payload);
      toast.success("Vote submitted");
      setVoted(true);
      setPicks({});
      setSelected(null);

      // refresh ballot after vote
      try {
        const res = await http.get(`elections/${effectiveId}/ballot`);
        const payload = res.data || {};
        const secs = buildSections(payload);
        const list: Choice[] =
          secs.length === 0
            ? Array.isArray((payload as any).choices)
              ? ((payload as any).choices as Choice[])
              : Array.isArray((payload as any).atLarge)
              ? ((payload as any).atLarge as Choice[])
              : []
            : [];
        setSections(secs);
        setChoices(list);
        setPicks({});
      } catch {
        /* ignore */
      }
    } catch (err: unknown) {
      const info = err as { response?: { status?: number; data?: Record<string, any> } };
      const s = info.response?.status;
      const data = info.response?.data as any;

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

  if (!user)
    return (
      <Blocked
        title="Not signed in."
        sub="You need to sign in to view the ballot."
      />
    );
  if (!effectiveId)
    return (
      <Blocked
        title="No active election."
        sub="There is no current election to vote on."
      />
    );
  if (loading) return <Loader text="Loading ballot…" />;

  if (error?.code === 403)
    return (
      <Blocked
        title="Voting closed."
        sub="This election is not open for voting. If you believe this is an error, contact your officer."
      />
    );
  if (error?.code === 409)
    return (
      <Blocked
        title="You already voted."
        sub="Your vote has been recorded. You cannot vote again for this election."
      />
    );
  if (error && ![403, 409].includes(error.code))
    return <DevError code={error.code} msg={error.msg} debug={debug} />;

  const positionMode = sections.length > 0;
  const empty = !positionMode && choices.length === 0;

  // How many positions currently have a selected candidacy
  const filledPositionsCount = sections.reduce((count, sec) => {
    return typeof picks[sec.id] === "number" ? count + 1 : count;
  }, 0);

  const canSubmit = positionMode
    ? filledPositionsCount === sections.length // ALL positions must be filled
    : Boolean(selected);


  return (
    <div className="ballot-page-container">
      <div className="ballot-content">
        <h1 className="ballot-title">Ballot</h1>
        <p className="ballot-instructions">
          Select one candidate for each position.
        </p>

        {voted && (
          <div className="ballot-success-message">
            <div className="font-semibold">
              Your vote was submitted successfully.
            </div>
            <div className="text-sm text-gray-600">
              You cannot modify your vote for this election.
            </div>
          </div>
        )}

        {empty && (
          <div className="ballot-empty-message">
            No choices available. If you've already voted, this is expected.
          </div>
        )}

        {!empty && (
          <>
            {sections.length > 0 ? (
              sections.map((sec) => (
                <fieldset key={sec.id} className="ballot-section">
                  <legend className="ballot-section-title">{sec.title}</legend>
                  <div className="ballot-options">
                    {sec.options.map((c) => (
                      <OptionRow
                        key={c.candidacyId}
                        c={c}
                        checked={picks[sec.id] === c.candidacyId}
                        name={`position-${sec.id}`}
                        onSelect={() => {
                          if (!c.candidacyId) return;
                          setPicks((prev) => ({
                            ...prev,
                            [sec.id]: c.candidacyId,
                          }));
                        }}
                        voted={voted}
                      />
                    ))}
                  </div>
                </fieldset>
              ))
            ) : (
              <fieldset className="ballot-section">
                <legend className="ballot-section-title">Candidates</legend>
                <div className="ballot-options">
                  {choices.map((c) => (
                    <OptionRow
                      key={c.candidacyId}
                      c={c}
                      checked={selected === c.candidacyId}
                      name="choice-global"
                      onSelect={() => {
                        if (c.candidacyId) setSelected(c.candidacyId);
                      }}
                      voted={voted}
                    />
                  ))}
                </div>
              </fieldset>
            )}
          </>
        )}

        <button
          onClick={submit}
          disabled={!canSubmit || submitting || voted}
          className="ballot-submit-btn"
        >
          Submit Vote
        </button>

{showDebug && (
  <details className="ballot-debug">
    <summary>Debug Info</summary>
    <pre>{JSON.stringify(debug, null, 2)}</pre>
  </details>
)}

      </div>
    </div>
  );
}

/* =========================
   Misc UI helpers
   ========================= */
function messageForStatus(code: number, fallback: string) {
  if (code === 403)
    return "This election is not open for voting. If you believe this is an error, contact your officer.";
  if (code === 409)
    return "Your vote has been recorded. You cannot vote again for this election.";
  if (code === 404) return "Ballot endpoint not found (404).";
  return fallback || `Request failed (HTTP ${code}).`;
}

function Loader({ text }: { text: string }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-white">
      <div className="animate-pulse text-lg font-medium text-gray-500">
        {text}
      </div>
    </div>
  );
}

function Blocked({ title, sub }: { title: string; sub: string }) {
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="ballot-blocked-card">
        <h1 className="text-2xl font-semibold">{title}</h1>
        <p className="mt-2 text-gray-600">{sub}</p>
      </div>
    </div>
  );
}

function DevError({
  code,
  msg,
  debug,
}: {
  code: number;
  msg: string;
  debug?: BallotDebug | null;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="ballot-error-card">
        <h2 className="text-xl font-semibold">
          Error Loading Ballot (HTTP {code})
        </h2>
        <p className="mt-2">{msg}</p>
        {import.meta.env.DEV && debug && (
          <details className="mt-4">
            <summary className="cursor-pointer font-medium">
              Show Debug Info
            </summary>
            <pre className="mt-2 text-xs overflow-auto">
              {JSON.stringify(debug, null, 2)}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
}
