import React, { useEffect, useMemo, useState } from "react";
import type { Position } from "../services/electionApi";
import { searchMembers, type Member } from "../services/candidacyApi";
import { useDebounce } from "../../hooks/useDebounce";
import { useToast } from "../../ui/Toast";
import { createCandidacy as createAdminCandidacy } from "../services/candidacyAdminApi";

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
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  const debounced = useDebounce(memberQuery, 250);
  useEffect(() => {
    if (!debounced || debounced.trim().length < 2 || member) { setMemberHits([]); return; }
    (async () => {
      try {
        const hits = await searchMembers(debounced.trim());
        setMemberHits(hits.slice(0, 10));
      } catch { setMemberHits([]); }
    })();
  }, [debounced, member]);

  const canSubmit = useMemo(() => {
    return !!member?.id || (!!email && !!name);
  }, [member?.id, email, name]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }} style={{ background: "rgba(0,0,0,0.4)" }}>
      <div className="bg-white rounded-lg shadow-lg w-full max-w-xl p-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Add Candidate</h2>
          <button className="text-gray-500 hover:text-black" onClick={onClose}>×</button>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium">Pick existing member</label>
            <input
              type="text"
              placeholder="Search by name or email"
              className="mt-1 w-full border rounded p-2"
              value={member ? `${member.name ?? "Member"}${member.email ? ` <${member.email}>` : ""}` : memberQuery}
              onChange={(e) => { setMember(null); setMemberQuery(e.target.value); }}
            />
            {!member && memberHits.length > 0 && (
              <div className="mt-2 max-h-48 overflow-auto rounded border">
                {memberHits.map((m) => (
                  <button
                    key={m.id ?? m.email}
                    className="w-full text-left px-2 py-1 hover:bg-gray-50"
                    onClick={() => { setMember(m); setMemberQuery(""); setEmail(m.email || ""); setName(m.name || ""); }}
                  >
                    <div className="text-sm font-medium">{m.name || "(no name)"}</div>
                    <div className="text-xs text-slate-600">{m.email}</div>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium">Or quick-add by email</label>
            <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="email@example.com" className="mt-1 w-full border rounded p-2" />
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Full name (optional)" className="mt-2 w-full border rounded p-2" />
          </div>
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium">Assign Position (optional)</label>
          <select className="mt-1 border rounded p-2 w-full" value={positionId ?? ""} onChange={(e) => setPositionId(e.target.value ? Number(e.target.value) : null)}>
            <option value="">Unassigned</option>
            {positions.map(p => <option key={p.id} value={p.id}>{p.title}</option>)}
          </select>
        </div>

        <div className="mt-6 flex justify-end gap-2">
          <button className="px-3 py-2 rounded border" onClick={onClose} disabled={busy}>Cancel</button>
          <button
            className="px-3 py-2 rounded bg-blue-600 text-white disabled:opacity-60"
            disabled={!canSubmit || busy}
            onClick={async () => {
              try {
                setBusy(true);
                if (member?.id) {
                  await createAdminCandidacy(electionId, { member_id: member.id, position_id: positionId });
                } else {
                  await createAdminCandidacy(electionId, { email, name, position_id: positionId });
                }
                onAdded();
              } catch (err: any) {
                // >>> PAPSAS v1.3 BEGIN
                toast.apiError?.(err, "Failed to add");
                // Acceptance: 409 duplicate -> toast "Already exists"
                // <<< PAPSAS v1.3 END
              } finally {
                setBusy(false);
              }
            }}
          >Add</button>
        </div>
      </div>
    </div>
  );
};
