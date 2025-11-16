// src/modules/pages/BallotPage.tsx
import { useEffect, useState, useMemo } from "react";
import { http } from "../lib/http";
import { useElection } from "../election/hooks/useElection";
import { useToast } from "../ui/Toast";

// Hydrate credentials/photo from candidacies
import { listCandidacies } from "../election/services/candidacyApi";

/* =========================
   Types
   ========================= */
type Choice = {
  candidacyId: number;
  candidateId: number;
  name: string;
  credentials?: string | string[];
  photoUrl?: string;
};
type Section = { id: number; title: string; options: Choice[] };
type BallotPositionPayload = {
  id?: string | number;
  title?: string;
  options?: Choice[] | unknown[];
  choices?: Choice[] | unknown[];
};
type BallotDebug = { tried: Array<{ url: string; status: number }>; winner?: string; payload?: unknown };
type BallotError = { response?: { status?: number; data?: { code?: string; message?: string } }; message?: string };

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

function normalizeCreds(val: unknown): string[] {
  if (Array.isArray(val)) return val.map(String).map((s) => s.trim()).filter(Boolean);
  if (typeof val === "string") {
    return val.split(/\r?\n|;|•|·/).map((s) => s.trim()).filter(Boolean);
  }
  return [];
}

/** Overlay credentials/photo from candidacy list */
async function hydrateWithCandidacies(electionId: number, secs: Section[], list: Choice[]) {
  try {
    const rows = await listCandidacies(electionId);
    const map = new Map<number, { credentials?: string | string[]; photoUrl?: string; name?: string }>();
    for (const r of rows as any[]) {
      map.set(Number(r.id), {
        credentials: r.credentials ?? r.bio ?? r.platform,
        photoUrl: r.photoUrl ?? r.photo_url ?? r.avatar ?? r.member?.avatar_url,
        name: r.name,
      });
    }
    const overlay = (c: Choice): Choice => {
      const m = map.get(Number(c.candidacyId));
      if (!m) return c;
      return {
        ...c,
        credentials: c.credentials ?? m.credentials,
        photoUrl: c.photoUrl ?? m.photoUrl,
        name: c.name || m.name || c.name,
      };
    };
    return {
      sections: secs.map((s) => ({ ...s, options: s.options.map(overlay) })),
      choices: list.map(overlay),
    };
  } catch {
    return { sections: secs, choices: list };
  }
}

/* =========================
   Small UI bits
   ========================= */
function Avatar({
  src,
  name,
  size = 84,            // bigger
  radius = 12,          // square with gentle rounding
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
    background: "var(--surface)",
    color: "var(--brand-700)",
    border: "1px solid var(--ring)",
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
  const creds = normalizeCreds(c.credentials);

  return (
    <label
      className="ep-candidate block" // let CSS style it; no inline red ring
    >
      {/* Row: radio | (avatar + text) */}
      <div className="flex items-start gap-5 md:gap-6">
        {/* Radio */}
        <input
          type="radio"
          name={name}
          checked={checked}
          onChange={onSelect}
          disabled={voted}
          className="size-4 mt-1 flex-none"
          style={{ accentColor: "var(--brand)" }}
        />

        {/* Avatar + content */}
        <div className="flex items-start gap-5 md:gap-6 flex-1 min-w-0">
          <Avatar src={c.photoUrl} name={c.name} size={88} radius={12} />

          {/* Name + credentials */}
          <div className="flex-1 min-w-0">
            <div className="font-medium text-[15px] leading-snug break-words mb-2">
              {c.name}
            </div>

            {creds.length > 0 && (
              <details
                className="ep-cred"
                onClick={(e) => e.stopPropagation()}
                onMouseDown={(e) => e.stopPropagation()}
                onKeyDown={(e) => e.stopPropagation()}
              >
                <summary>Credentials</summary>
                <ul className="ep-cred-list">
                  {creds.map((line, i) => (
                    <li key={i}>{line}</li>
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

  const isPrivileged = useMemo(() => {
    if (!user) return false;
    if ((user as any).is_superuser) return true;
    if ((user as any).is_staff) return true;
    if ((user as any).role && ["admin", "officer"].includes((user as any).role.toLowerCase())) return true;
    if (Array.isArray((user as any).groups) && (user as any).groups.some((g: string) => ["admin", "officer"].includes(g.toLowerCase())))
      return true;
    return false;
  }, [user]);

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

        const list: Choice[] =
          secs.length === 0
            ? Array.isArray(payload.choices)
              ? (payload.choices as Choice[])
              : Array.isArray(payload.atLarge)
              ? (payload.atLarge as Choice[])
              : []
            : [];

        const hydrated = await hydrateWithCandidacies(Number(effectiveId), secs, list);

        setSections(hydrated.sections);
        setChoices(hydrated.choices);
        setPicks({});

        if (import.meta.env.DEV) {
          setDebug({
            tried: [{ url, status: 200 }],
            winner: url,
            payload: {
              ballot: payload,
              hydratedPreview: hydrated.sections?.[0]?.options?.slice?.(0, 1) ?? [],
            },
          });
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

    const positionsPayload: VoteChoice[] =
      sections.length > 0
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

    const payload: VoteRequestPayload = sections.length > 0 ? { positions: positionsPayload } : { atLarge: [selected!] };

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
            ? Array.isArray(payload.choices)
              ? (payload.choices as Choice[])
              : Array.isArray(payload.atLarge)
              ? (payload.atLarge as Choice[])
              : []
            : [];
        const hydrated = await hydrateWithCandidacies(Number(effectiveId), secs, list);
        setSections(hydrated.sections);
        setChoices(hydrated.choices);
        setPicks({});
      } catch {
        /* ignore */
      }
    } catch (err: unknown) {
      const info = err as { response?: { status?: number; data?: Record<string, unknown> } };
      const s = info.response?.status;
      const data = info.response?.data;

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
    return (
      <Blocked
        title="Voting closed."
        sub="This election is not open for voting. If you believe this is an error, contact your officer."
      />
    );
  if (error?.code === 409)
    return <Blocked title="You already voted." sub="Your vote has been recorded. You cannot vote again for this election." />;
  if (error && ![403, 409].includes(error.code)) return <DevError code={error.code} msg={error.msg} debug={debug} />;

  const empty = !positionMode && choices.length === 0;

  const canSubmit = positionMode
    ? Object.values(byPosition).some((cid) => typeof cid === "number")
    : Boolean(selected);

  return (
    <div>
      <div className="page-ballot">
  <div className="ballot-wrap max-w-2xl mx-auto px-4 py-3">
    <h1 className="text-2xl font-semibold mb-4">BALLOT</h1>
    <p className="subtle mb-6">Select one candidate.</p>

    {voted && (
      <div
        className="card mb-6"
        style={{ borderColor: "rgba(16,185,129,.4)", background: "rgba(16,185,129,.1)" }}
      >
        <div className="font-medium">Your vote was submitted.</div>
        <div className="text-sm subtle">You cannot modify your vote for this election.</div>
      </div>
    )}

    {empty && (
      <div className="callout callout-warn mb-6">
        No choices returned. If this user already voted, this is expected.
      </div>
    )}

    {!empty && (
      <>
        {sections.length > 0 ? (
          sections.map((sec) => (
            <fieldset key={sec.id} className="card mb-6">
              <legend className="px-2 text-lg font-medium">{sec.title}</legend>
              <div className="mt-2 space-y-2">
                {sec.options.map((c) => (
                  <OptionRow
                    key={c.candidacyId}
                    c={c}
                    checked={picks[sec.id] === c.candidacyId}
                    name={`position-${sec.id}`}
                    onSelect={() => {
                      if (!c.candidacyId) return;
                      setPicks((prev) => ({ ...prev, [sec.id]: c.candidacyId }));
                    }}
                    voted={voted}
                  />
                ))}
              </div>
            </fieldset>
          ))
        ) : (
          <fieldset className="card mb-6">
            <legend className="px-2 text-lg font-medium">Candidates</legend>
            <div className="mt-2 space-y-2">
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

    <button onClick={submit} disabled={!canSubmit || submitting || voted} className="btn btn-primary w-full">
      Submit vote
    </button>

    {import.meta.env.DEV && isPrivileged && (
      <details className="mt-8 card">
        <summary className="cursor-pointer">Debug</summary>
        <pre className="mt-2 text-xs whitespace-pre-wrap">{JSON.stringify(debug, null, 2)}</pre>
      </details>
    )}
  </div>
</div>
    </div>
  );
}

/* =========================
   Misc UI helpers
   ========================= */
function messageForStatus(code: number, fallback: string) {
  if (code === 403) return "This election is not open for voting. If you believe this is an error, contact your officer.";
  if (code === 409) return "Your vote has been recorded. You cannot vote again for this election.";
  if (code === 404) return "Ballot endpoint not found (404).";
  return fallback || `Request failed (HTTP ${code}).`;
}

function Loader({ text }: { text: string }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-white">
      <div className="animate-pulse text-lg font-medium text-[var(--text-muted)]">{text}</div>
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
