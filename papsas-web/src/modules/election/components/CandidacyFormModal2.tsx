// src/modules/election/components/CandidacyFormModal2.tsx
import React, { useEffect, useMemo, useState, useRef } from "react";
import { createPortal } from "react-dom";
import Alert from "../../ui/Alert";
import type { Position } from "../services/electionApi";
import { searchMembers, type Member } from "../services/candidacyApi";
import { useDebounce } from "../../hooks/useDebounce";
import { useToast } from "../../ui/Toast";
import { Search, X, Loader2, ChevronDown } from "lucide-react";

type Props = {
  electionId: number;
  open: boolean;
  initial?: {
    id: number;
    memberId?: number;
    name?: string;
    email?: string;
    positionId: number | null | undefined;
    credentials?: string | null;
    status?: boolean | null;
  } | null;
  positions: Position[];
  onClose: () => void;
  onSubmit: (payload: { id?: number; positionId: number | null; credentials?: string }) => Promise<void>;
};

type ApiErrorData = { code?: string; message?: string };
type AxiosLikeError = {
  response?: {
    data?: ApiErrorData | string;
    status?: number;
  };
  message?: string;
};

function friendlyErrorFromResponse(err: unknown): string {
  const error = err as AxiosLikeError | null;
  const data = error?.response?.data;
  const obj = typeof data === "object" && data !== null ? (data as ApiErrorData) : undefined;
  const code = obj?.code || "";
  const msg =
    obj?.message ||
    (typeof data === "string" ? data : undefined) ||
    error?.message ||
    "Request failed";
  if (code === "EMAIL_TAKEN" || code === "USER_EXISTS")
    return "That email already belongs to an account. Pick it via “Pick existing member”, or the system will try to link it automatically.";
  if (code === "ALREADY_EXISTS")
    return "This member is already a candidate in the current election.";
  if (code === "HAS_VOTES")
    return "This candidate already has votes and cannot be deleted.";
  if (code === "VALIDATION_ERROR")
    return String(msg);
  if (error?.response?.status === 404)
    return "Endpoint not found (404). Make sure the server route exists.";
  return typeof msg === "string" ? msg : "Something went wrong.";
}

/* -------------------------------------------------------------
   EDIT CANDIDATE MODAL – FULL OVERLAY (PORTAL)
   ------------------------------------------------------------- */
export const EditCandidateModal: React.FC<Props> = ({
  open,
  initial,
  positions,
  onClose,
  onSubmit,
}) => {
  const isEdit = !!initial?.id;
  const toast = useToast();
  const [member, setMember] = useState<Member | null>(
    initial?.memberId
      ? { id: initial.memberId, name: initial.name, email: initial.email } as Member
      : null
  );
  const [memberQuery, setMemberQuery] = useState<string>("");
  const [memberHits, setMemberHits] = useState<Member[]>([]);
  const [activeIdx, setActiveIdx] = useState(-1);
  const listRef = useRef<HTMLDivElement | null>(null);
  const [name, setName] = useState(initial?.name || "");
  const [email, setEmail] = useState(initial?.email || "");
  const [positionId, setPositionId] = useState<number | undefined>(initial?.positionId ?? undefined);
  const [credentials, setCredentials] = useState(initial?.credentials || "");
  const [status, setStatus] = useState<boolean>(!!initial?.status);
  const [busy, setBusy] = useState(false);
  const [errText, setErrText] = useState<string | null>(null);

  /* ---- Escape handling ---- */
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  /* ---- Debounced search ---- */
  const debounced = useDebounce(memberQuery, 250);
  useEffect(() => {
    if (!debounced || debounced.trim().length < 2 || member) {
      setMemberHits([]);
      return;
    }
    (async () => {
      try {
        const hits = await searchMembers(debounced.trim());
        setMemberHits(hits.slice(0, 10));
      } catch {
        setMemberHits([]);
      }
    })();
  }, [debounced, member]);

  /* ---- Keyboard navigation in dropdown ---- */
  const onKeyDown: React.KeyboardEventHandler<HTMLInputElement> = (e) => {
    if (!memberHits.length) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIdx((i) => Math.min(i + 1, memberHits.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIdx((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter" && activeIdx >= 0) {
      e.preventDefault();
      const picked = memberHits[activeIdx];
      setMember(picked);
      setMemberHits([]);
      setActiveIdx(-1);
    } else if (e.key === "Escape") {
      setMemberHits([]);
      setActiveIdx(-1);
    }
  };

  useEffect(() => {
    const el = listRef.current?.querySelector<HTMLDivElement>(`[data-idx="${activeIdx}"]`);
    el?.scrollIntoView({ block: "nearest" });
  }, [activeIdx]);

  const canSubmit = useMemo(() => {
    const hasIdOrEmail = !!member?.id || !!email.trim();
    const positionsOptional = positions.length === 0;
    const hasPositionChoice = positionId !== undefined;
    return hasIdOrEmail && (positionsOptional || hasPositionChoice);
  }, [member?.id, email, positionId, positions.length]);

  if (!open) return null;

  /* -------------------------------------------------------------
     PORTAL: Renders directly on <body> → full overlay
     ------------------------------------------------------------- */
  return createPortal(
    <div
      className="modal-root"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      {/* Backdrop */}
      <div className="modal-overlay" />

      {/* Modal Card */}
      <div className="modal-card max-w-3xl w-full">
        {/* Header */}
        <div className="modal-header">
          <h2 className="modal-title">{isEdit ? "Edit Candidate" : "Add Candidate"}</h2>
          <button className="modal-close-btn" onClick={onClose} aria-label="Close">
            <X size={20} />
          </button>
        </div>

        {/* Error Alert */}
        {errText && (
          <div className="px-5">
            <Alert title="We couldn’t save this">{errText}</Alert>
          </div>
        )}

        {/* Body */}
        <div className="modal-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Member Search */}
            <div>
              <label className="modal-label">Pick existing member</label>
              <div className="relative">
                <Search className="modal-search-icon" size={18} />
                <input
                  type="text"
                  placeholder="Search by name or email"
                  className="modal-input pl-10"
                  value={member ? `${member.name ?? "Member"}${member.email ? ` <${member.email}>` : ""}` : memberQuery}
                  onChange={(e) => {
                    setMember(null);
                    setMemberQuery(e.target.value);
                  }}
                  onKeyDown={onKeyDown}
                  disabled={busy}
                />
              </div>

              {member && (
                <div className="mt-2 text-xs text-muted">
                  Selected: {member.name || "Member"} ({member.email})
                  <button className="ml-2 underline" onClick={() => setMember(null)} type="button">
                    Clear
                  </button>
                </div>
              )}

              {!member && memberHits.length > 0 && (
                <div ref={listRef} className="modal-dropdown">
                  {memberHits.map((m, i) => (
                    <button
                      key={m.id}
                      data-idx={i}
                      className={`modal-dropdown-item ${i === activeIdx ? "selected" : ""}`}
                      onMouseEnter={() => setActiveIdx(i)}
                      onClick={() => {
                        setMember(m);
                        setMemberQuery("");
                        setMemberHits([]);
                        setActiveIdx(-1);
                        if (m.email) setEmail(m.email);
                        if (m.name) setName(m.name);
                      }}
                    >
                      <div className="font-medium text-sm">{m.name || "Member"}</div>
                      {m.email && <div className="text-xs text-muted">{m.email}</div>}
                    </button>
                  ))}
                </div>
              )}
              <p className="text-xs text-muted mt-1">
                Select a member or use quick-add on the right.
              </p>
            </div>

            {/* Quick Add */}
            <div>
              <label className="modal-label">Quick-add (email + optional name)</label>
              <input
                type="email"
                placeholder="Email (required if not picking)"
                className="modal-input"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (!name) setName(e.target.value.split("@")[0] || "");
                }}
                disabled={!!member || busy}
              />
              <input
                type="text"
                placeholder="Full name (optional)"
                className="modal-input mt-3"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={!!member || busy}
              />
            </div>
          </div>

          {/* Position + Credentials */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mt-5">
            <div>
              <label className="modal-label">
                Position {positions.length === 0 && <span className="text-muted">(optional)</span>}
              </label>
              <div className="relative">
                <select
                  className="modal-select"
                  value={positionId ?? ""}
                  onChange={(e) => setPositionId(e.target.value ? Number(e.target.value) : undefined)}
                  disabled={positions.length === 0}
                >
                  <option value="">
                    {positions.length === 0 ? "— No positions available —" : "Unassigned"}
                  </option>
                  {positions.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.title}
                    </option>
                  ))}
                </select>
                <ChevronDown className="modal-select-chevron" size={16} />
              </div>
            </div>

            <div>
              <label className="modal-label">Credentials / Platform</label>
              <textarea
                rows={4}
                className="modal-textarea"
                value={credentials}
                onChange={(e) => setCredentials(e.target.value)}
                placeholder="Achievements, platform, etc."
              />
            </div>
          </div>

          {/* Status Toggle */}
          <div className="mt-5">
            <label className="candidacy-toggle">
              <input type="checkbox" checked={status} onChange={(e) => setStatus(e.target.checked)} />
              <span className="candidacy-toggle-slider" />
              <span className="candidacy-toggle-label">{status ? "Enabled" : "Disabled"}</span>
            </label>
          </div>
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose} disabled={busy}>
            Cancel
          </button>
          <button
            className="btn btn-primary flex items-center gap-2"
            disabled={!canSubmit || busy}
            onClick={async () => {
              setErrText(null);
              setBusy(true);
              try {
                await onSubmit({
                  id: initial?.id,
                  positionId: positionId ?? null,
                  credentials: credentials || undefined,
                });
                toast.success(initial?.id ? "Candidate updated" : "Candidate added");
                onClose();
              } catch (e) {
                const msg = friendlyErrorFromResponse(e);
                setErrText(msg);
                toast.error(msg);
              } finally {
                setBusy(false);
              }
            }}
          >
            {busy && <Loader2 className="animate-spin" size={16} />}
            {isEdit ? "Save changes" : "Add candidate"}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
};
