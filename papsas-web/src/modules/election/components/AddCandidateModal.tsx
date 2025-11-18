// src/modules/election/components/AddCandidateModal.tsx
import React, { useEffect, useMemo, useState } from "react";
import type { Position } from "../services/electionApi";
import { searchMembers, type Member } from "../services/candidacyApi";
import { useDebounce } from "../../hooks/useDebounce";
import { useToast } from "../../ui/Toast";
import { createCandidacy as createAdminCandidacy } from "../services/candidacyAdminApi";

import "./ElectionModals.css";

export const AddCandidateModal: React.FC<{
  electionId: number;
  open: boolean;
  positions: Position[];
  onClose: () => void;
  onAdded: () => void;
}> = ({ electionId, open, positions, onClose, onAdded }) => {
  const toast = useToast();
  const [member, setMember] = useState<Member | null>(null);
  const [memberQuery, setMemberQuery] = useState("");
  const [memberHits, setMemberHits] = useState<Member[]>([]);
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [positionId, setPositionId] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

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

  const canSubmit = useMemo(() => {
    return !!member?.id || (!!email && !!name);
  }, [member?.id, email, name]);

  if (!open) return null;

  return (
    <div
      className="election-modal-overlay"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="election-modal" role="dialog" aria-modal="true">
        <div className="election-modal-header">
          <div>
            <h2 className="election-modal-title">Add Candidate</h2>
            <p className="election-modal-subtitle">
              Pick an existing member or quickly add by email, then optionally
              assign a position.
            </p>
          </div>
          <button
            className="election-modal-close"
            onClick={onClose}
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        <div className="election-modal-body">
          <div className="election-modal-grid">
            <div>
              <label className="election-modal-label">
                Pick existing member
              </label>
              <input
                type="text"
                placeholder="Search by name or email"
                className="election-modal-input"
                value={
                  member
                    ? `${member.name ?? "Member"}${
                        member.email ? ` <${member.email}>` : ""
                      }`
                    : memberQuery
                }
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                  setMember(null);
                  setMemberQuery(e.target.value);
                }}
                disabled={busy}
              />
              {!member && memberHits.length > 0 && (
                <div className="election-modal-hits">
                  {memberHits.map((m) => (
                    <button
                      key={m.id ?? m.email}
                      className="election-modal-hit-row"
                      onClick={() => {
                        setMember(m);
                        setMemberQuery("");
                        setEmail(m.email || "");
                        setName(m.name || "");
                      }}
                      type="button"
                    >
                      <div className="election-modal-hit-name">
                        {m.name || "(no name)"}
                      </div>
                      <div className="election-modal-hit-email">
                        {m.email}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className="election-modal-label">
                Or quick-add by email
              </label>
              <input
                value={email}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setEmail(e.target.value)
                }
                placeholder="email@example.com"
                className="election-modal-input"
                disabled={busy}
              />
              <input
                value={name}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setName(e.target.value)
                }
                placeholder="Full name (optional)"
                className="election-modal-input election-modal-input--spaced"
                disabled={busy}
              />
            </div>
          </div>

          <div className="election-modal-section">
            <label className="election-modal-label">
              Assign position <span className="election-modal-label-optional">(optional)</span>
            </label>
            <select
              className="election-modal-select"
              value={positionId ?? ""}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                setPositionId(e.target.value ? Number(e.target.value) : null)
              }
              disabled={busy}
            >
              <option value="">Unassigned</option>
              {positions.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.title}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="election-modal-footer">
          <button
            className="btn btn-secondary"
            onClick={onClose}
            disabled={busy}
          >
            Cancel
          </button>
          <button
            className="btn btn-primary"
            disabled={!canSubmit || busy}
            onClick={async () => {
              try {
                setBusy(true);
                if (member?.id) {
                  await createAdminCandidacy(electionId, {
                    member_id: member.id,
                    position_id: positionId,
                  });
                } else {
                  await createAdminCandidacy(electionId, {
                    email,
                    name,
                    position_id: positionId,
                  });
                }
                onAdded();
              } catch (err: unknown) {
                toast.apiError(err, "Failed to add");
              } finally {
                setBusy(false);
              }
            }}
          >
            Add candidate
          </button>
        </div>
      </div>
    </div>
  );
};
