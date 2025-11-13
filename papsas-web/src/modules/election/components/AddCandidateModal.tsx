// src/components/AddCandidateModal.tsx
import React, { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom"; // ← ADD THIS
import type { Position } from "../services/electionApi";
import { searchMembers, type Member } from "../services/candidacyApi";
import { useDebounce } from "../../hooks/useDebounce";
import { useToast } from "../../ui/Toast";
import { createCandidacy as createAdminCandidacy } from "../services/candidacyAdminApi";
import { Search, X, Loader2 } from "lucide-react";

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

  const canSubmit = useMemo(
    () => !!member?.id || (!!email.trim() && !!name.trim()),
    [member?.id, email, name]
  );

  if (!open) return null;

  // PORTAL: RENDERS ON <body>, NOT INSIDE TABLE
  return createPortal(
      <div
        className="modal-root"
        onClick={(e) => e.target === e.currentTarget && onClose()}
      >
      <div className="modal-overlay" />
      <div className="modal-card max-w-2xl w-full">
        {/* Header */}
        <div className="modal-header">
          <h2 className="modal-title">Add Candidate</h2>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div className="modal-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Member Search */}
            <div>
              <label className="modal-label">Search Existing Member</label>
              <div className="relative">
                <Search className="modal-search-icon" size={18} />
                <input
                  type="text"
                  placeholder="Name or email…"
                  className="modal-input pl-10"
                  value={
                    member
                      ? `${member.name ?? "Member"}${member.email ? ` <${member.email}>` : ""}`
                      : memberQuery
                  }
                  onChange={(e) => {
                    setMember(null);
                    setMemberQuery(e.target.value);
                  }}
                  disabled={busy}
                />
              </div>
              {!member && memberHits.length > 0 && (
                <div className="modal-dropdown">
                  {memberHits.map((m) => (
                    <button
                      key={m.id ?? m.email}
                      className="modal-dropdown-item"
                      onClick={() => {
                        setMember(m);
                        setMemberQuery("");
                        setEmail(m.email || "");
                        setName(m.name || "");
                      }}
                    >
                      <div className="font-medium text-sm">{m.name || "(no name)"}</div>
                      {m.email && <div className="text-xs text-muted">{m.email}</div>}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Quick Add */}
            <div>
              <label className="modal-label">Or Quick Add</label>
              <input
                type="email"
                placeholder="email@example.com"
                className="modal-input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={!!member || busy}
              />
              <input
                type="text"
                placeholder="Full name "
                className="modal-input mt-3"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={!!member || busy}
              />
            </div>
          </div>

          {/* Position */}
          <div className="mt-5">
            <label className="modal-label">Assign Position (optional)</label>
            <div className="relative">
              <select
                className="modal-select"
                value={positionId ?? ""}
                onChange={(e) =>
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
              setBusy(true);
              try {
                if (member?.id) {
                  await createAdminCandidacy(electionId, {
                    member_id: member.id,
                    position_id: positionId,
                  });
                } else {
                  await createAdminCandidacy(electionId, {
                    email: email.trim(),
                    name: name.trim(),
                    position_id: positionId,
                  });
                }
                toast.success("Candidate added");
                onAdded();
                onClose();
              } catch (err) {
                toast.apiError?.(err, "Failed to add");
              } finally {
                setBusy(false);
              }
            }}
          >
            {busy && <Loader2 className="animate-spin" size={16} />}
            Add Candidate
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
};
