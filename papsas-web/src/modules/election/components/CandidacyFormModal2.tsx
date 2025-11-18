// src/modules/election/components/CandidacyFormModal2.tsx
import React, { useEffect, useMemo, useState, useRef } from "react";
import Alert from "../../ui/Alert";
import type { Position } from "../services/electionApi";
import { searchMembers, type Member } from "../services/candidacyApi";
import { useDebounce } from "../../hooks/useDebounce";
import { useToast } from "../../ui/Toast";

import "./ElectionModals.css";

type Props = {
  electionId: number;
  open: boolean;
  initial?:
    | {
        id: number;
        memberId?: number;
        name?: string;
        email?: string;
        positionId: number | null | undefined;
        credentials?: string | null;
      }
    | null;
  positions: Position[];
  onClose: () => void;
  onSubmit: (payload: {
    id?: number;
    memberId?: number;
    name?: string;
    email?: string;
    positionId: number | null;
    credentials?: string;
  }) => Promise<void>;
};

function friendlyErrorFromResponse(err: unknown): string {
  const ax = err as {
    response?: { data?: Record<string, unknown>; status?: number };
    message?: string;
  };
  const data = ax.response?.data;
  const code = (data as Record<string, unknown>)?.code || "";
  const msg =
    (data as Record<string, unknown>)?.message ||
    data ||
    ax.message ||
    "Request failed";
  if (code === "EMAIL_TAKEN" || code === "USER_EXISTS")
    return 'That email already belongs to an account. Pick it via "Pick existing member", or the system will try to link it automatically.';
  if (code === "ALREADY_EXISTS")
    return "This member is already a candidate in the current election.";
  if (code === "HAS_VOTES")
    return "This candidate already has votes and cannot be deleted.";
  if (code === "VALIDATION_ERROR") return String(msg);
  if (ax.response?.status === 404)
    return "Endpoint not found (404). Make sure the server route exists.";
  return typeof msg === "string" ? msg : "Something went wrong.";
}

export const CandidacyFormModal: React.FC<Props> = ({
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
      ? ({
          id: initial.memberId,
          name: initial.name,
          email: initial.email,
        } as Member)
      : null
  );
  const [memberQuery, setMemberQuery] = useState<string>("");
  const [memberHits, setMemberHits] = useState<Member[]>([]);
  const [activeIdx, setActiveIdx] = useState(-1);
  const listRef = useRef<HTMLDivElement | null>(null);

  const [name, setName] = useState(initial?.name || "");
  const [email, setEmail] = useState(initial?.email || "");
  const [positionId, setPositionId] = useState<number | undefined>(
    initial?.positionId ?? undefined
  );
  const [credentials, setCredentials] = useState(
    initial?.credentials || ""
  );
  const [busy, setBusy] = useState(false);
  const [errText, setErrText] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  // Debounced member search
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

  const onKeyDown: React.KeyboardEventHandler<HTMLInputElement> = (e) => {
    if (!memberHits || memberHits.length === 0) return;
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
    const el =
      listRef.current?.querySelector<HTMLDivElement>(
        `[data-idx="${activeIdx}"]`
      ) ||
      document.querySelector<HTMLDivElement>(
        `[data-idx="${activeIdx}"]`
      );
    if (el) el.scrollIntoView({ block: "nearest" });
  }, [activeIdx]);

  const canSubmit = useMemo(() => {
    const hasIdOrEmail = !!member?.id || !!email.trim();
    const positionsOptional = positions.length === 0;
    const hasPositionChoice = positionId !== undefined;
    return hasIdOrEmail && (positionsOptional || hasPositionChoice);
  }, [member?.id, email, positionId, positions.length]);

  if (!open) return null;

  return (
    <div
      className="election-modal-overlay"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className="election-modal"
        onMouseDown={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="election-modal-header">
          <div>
            <h2 className="election-modal-title">
              {isEdit ? "Edit Candidate" : "Add Candidate"}
            </h2>
            <p className="election-modal-subtitle">
              {isEdit
                ? "Update this candidate’s details for the current election."
                : "Pick an existing member or quickly add a new candidate."}
            </p>
          </div>
          <button
            className="election-modal-close"
            onClick={onClose}
            type="button"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div className="election-modal-body">
          {errText && (
            <div className="election-modal-alert">
              <Alert title="We couldn’t save this">{errText}</Alert>
            </div>
          )}

          {/* Member picker + quick add */}
          <div className="election-modal-grid">
            <div className="election-modal-section">
              <label className="election-modal-label">
                Pick existing member
              </label>
              <input
                type="text"
                placeholder="Search by name or email"
                onKeyDown={onKeyDown}
                className="election-modal-input"
                value={
                  member
                    ? `${member.name ?? "Member"}${
                        member.email ? ` <${member.email}>` : ""
                      }`
                    : memberQuery
                }
                onChange={(e) => {
                  setMember(null);
                  setMemberQuery(e.target.value);
                }}
                disabled={busy}
              />

              {member && (
                <div className="election-modal-selected">
                  Selected: {member.name || "Member"}
                  {member.email ? ` (${member.email})` : ""}
                  <button
                    className="election-modal-selected-clear"
                    onClick={() => setMember(null)}
                    type="button"
                  >
                    Clear
                  </button>
                </div>
              )}

              {!member && memberHits.length > 0 && (
                <div
                  className="election-modal-hits"
                  ref={listRef}
                >
                  {memberHits.map((m, i) => (
                    <button
                      key={m.id}
                      data-idx={i}
                      type="button"
                      onMouseEnter={() => setActiveIdx(i)}
                      className={`election-modal-hit-row${
                        i === activeIdx
                          ? " election-modal-hit-row--active"
                          : ""
                      }`}
                      onClick={() => {
                        setMember(m);
                        setMemberQuery("");
                        setMemberHits([]);
                        setActiveIdx(-1);
                        if (m.email) setEmail(m.email);
                        if (m.name) setName(m.name);
                      }}
                    >
                      <div className="election-modal-hit-name">
                        {m.name || "Member"}
                      </div>
                      {m.email && (
                        <div className="election-modal-hit-email">
                          {m.email}
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              )}

              <div className="election-modal-help">
                Select a member or use quick-add on the right.
              </div>
            </div>

            <div className="election-modal-section">
              <label className="election-modal-label">
                Quick-add (email + optional name)
              </label>
              <input
                type="email"
                placeholder="Email (required if not picking)"
                className="election-modal-input"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (!name)
                    setName(e.target.value.split("@")[0] || "");
                }}
                disabled={!!member || busy}
              />
              <input
                type="text"
                placeholder="Full name (optional)"
                className="election-modal-input election-modal-input--spaced"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={!!member || busy}
              />
            </div>
          </div>

          {/* Position + credentials */}
          <div className="election-modal-grid election-modal-grid--bottom">
            <div className="election-modal-section">
              <label className="election-modal-label">
                Position
                {positions.length === 0 && (
                  <span className="election-modal-label-optional">
                    (optional)
                  </span>
                )}
              </label>
              <select
                value={positionId ?? ""}
                onChange={(e) =>
                  setPositionId(
                    e.target.value
                      ? Number(e.target.value)
                      : undefined
                  )
                }
                className="election-modal-select"
                disabled={positions.length === 0}
              >
                <option value="">
                  {positions.length === 0
                    ? "— No positions available —"
                    : "— Select —"}
                </option>
                {positions.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.title}
                  </option>
                ))}
              </select>
            </div>

            <div className="election-modal-section">
              <label className="election-modal-label">
                Credentials / Platform
              </label>
              <textarea
                className="election-modal-textarea"
                value={credentials}
                onChange={(e) => setCredentials(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="election-modal-footer">
          <button
            className="btn btn-secondary"
            onClick={onClose}
            disabled={busy}
            type="button"
          >
            Cancel
          </button>
          <button
            className="btn btn-primary"
            disabled={!canSubmit || busy}
            onClick={async () => {
              setErrText(null);
              setBusy(true);
              try {
                await onSubmit({
                  id: initial?.id,
                  memberId: member?.id,
                  name: name || undefined,
                  email: email || undefined,
                  positionId: positionId ?? null,
                  credentials: credentials || undefined,
                });
                onClose();
              } catch (e: unknown) {
                const msg = friendlyErrorFromResponse(e);
                setErrText(msg);
                toast.error(msg);
              } finally {
                setBusy(false);
              }
            }}
            type="button"
          >
            {isEdit ? "Save changes" : "Add candidate"}
          </button>
        </div>
      </div>
    </div>
  );
};
