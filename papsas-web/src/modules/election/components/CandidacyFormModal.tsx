import React, { useEffect, useMemo, useState } from "react";
import { listPositions } from "../services/electionApi";
import type { CandidacyCreate, Member } from "../services/candidacyApi";
import { searchMembers } from "../services/candidacyApi";
// >>> PAPSAS v1.3 BEGIN
import { searchUsers } from "../services/userSearchApi";
// <<< PAPSAS v1.3 END
// >>> PAPSAS v1.4 BEGIN
import { useToast } from "../../ui/Toast";
// <<< PAPSAS v1.4 END

type Props = {
  electionId: number;
  open: boolean;
  initial?: {
    id?: number;
    name?: string; email?: string; memberId?: number;
    positionId?: number; credentials?: string; status?: boolean;
  };
  onClose: () => void;
  onSubmit: (data: CandidacyCreate & { id?: number; status?: boolean }) => Promise<void>;
};

export const CandidacyFormModal: React.FC<Props> = ({ electionId, open, initial, onClose, onSubmit }) => {
  // >>> PAPSAS v1.4 BEGIN
  const toast = useToast();
  // <<< PAPSAS v1.4 END
  const [memberQuery, setMemberQuery] = useState("");
  const [memberOptions, setMemberOptions] = useState<Member[]>([]);
  const [memberId, setMemberId] = useState<number | undefined>(initial?.memberId);
  const [name, setName] = useState(initial?.name ?? "");
  const [email, setEmail] = useState(initial?.email ?? "");
  const [positionId, setPositionId] = useState<number | undefined>(initial?.positionId);
  const [credentials, setCredentials] = useState(initial?.credentials ?? "");
  const [status, setStatus] = useState<boolean>(initial?.status ?? true);
  const [positions, setPositions] = useState<{ id: number; title: string }[]>([]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    listPositions(electionId).then(setPositions).catch(() => setPositions([]));
  }, [open, electionId]);

  useEffect(() => {
    if (!memberQuery.trim()) return setMemberOptions([]);
    const id = window.setTimeout(async () => {
      try {
        // Try tolerant users API first; fallback to existing members search.
        // Debounce target: ~350ms
        // >>> PAPSAS v1.3 BEGIN
        const q = memberQuery.trim();
        const viaUsers = await searchUsers(q);
        if (Array.isArray(viaUsers) && viaUsers.length) {
          setMemberOptions(viaUsers.map(u => ({ id: u.id, name: u.name, email: u.email })));
        } else {
          const viaMembers = await searchMembers(q);
          setMemberOptions(viaMembers);
        }
        // <<< PAPSAS v1.3 END
      } catch { setMemberOptions([]); }
    }, 350);
    return () => window.clearTimeout(id);
  }, [memberQuery]);

  const isEdit = Boolean(initial?.id);
  const canSubmit = useMemo(() => !!positionId && (!!memberId || !!name), [positionId, memberId, name]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-2xl p-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">{isEdit ? "Edit Candidate" : "Add Candidate"}</h2>
          <button onClick={onClose} className="p-2" aria-label="Close">×</button>
        </div>

        {err && <div className="mt-2 text-red-600">{err}</div>}

        {/* Member picker OR Quick add */}
        <div className="mt-3 grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium">Pick existing member</label>
            <input
              value={memberQuery}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMemberQuery(e.target.value)}
              placeholder="Search name or email…"
              className="mt-1 w-full border rounded p-2"
            />
            {memberOptions.length > 0 && (
              <div className="mt-1 border rounded max-h-40 overflow-auto">
                {memberOptions.map(m => (
                  <button
                    type="button"
                    key={m.id}
                    className={`w-full text-left px-2 py-1 hover:bg-gray-100 ${memberId === m.id ? "bg-blue-50" : ""}`}
                    onClick={() => { setMemberId(m.id); setName(m.name || ""); setEmail(m.email || ""); }}
                  >
                    {m.name}{m.email ? ` – ${m.email}` : ""}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium">Or quick add</label>
            <input value={name} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setName(e.target.value)} placeholder="Full name"
                   className="mt-1 w-full border rounded p-2"/>
            <input value={email} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)} placeholder="Email (optional)"
                   className="mt-2 w-full border rounded p-2"/>
          </div>
        </div>

        {/* Position / Credentials / Status */}
        <div className="mt-4 grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium">Position</label>
            <select value={positionId ?? ""} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setPositionId(Number(e.target.value))}
                    className="mt-1 w-full border rounded p-2">
              <option value="" disabled>— Select —</option>
              {positions.map(p => <option key={p.id} value={p.id}>{p.title}</option>)}
            </select>
          </div>
          <div className="flex items-end">
            <label className="inline-flex items-center gap-2">
              <input type="checkbox" checked={status} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setStatus(e.target.checked)} />
              <span>Status: {status ? "Enabled" : "Disabled"}</span>
            </label>
          </div>
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium">Credentials</label>
          <textarea value={credentials} onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setCredentials(e.target.value)}
                    rows={4} className="mt-1 w-full border rounded p-2" />
        </div>

        <div className="mt-6 flex justify-end gap-2">
          <button className="px-4 py-2 border rounded" onClick={onClose} disabled={busy}>Cancel</button>
          <button
            className="px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-50"
            disabled={!canSubmit || busy}
            onClick={async () => {
              setErr(null); setBusy(true);
              try {
                await onSubmit({
                  id: initial?.id,
                  memberId,
                  name: name || undefined,
                  email: email || undefined,
                  positionId: positionId ?? null,
                  credentials,
                  status,
                });
                onClose();
              } catch (e: unknown) {
                // >>> PAPSAS v1.4 BEGIN
                toast.apiError(e, "Save failed");
                const ax = e as { response?: { data?: { message?: string; code?: string } }; message?: string };
                const resp = ax.response?.data as { message?: string; code?: string } | undefined;
                const msg = resp?.message || ax.message || "Save failed";
                const code = resp?.code;
                setErr(code ? `${code}: ${msg}` : msg);
                // <<< PAPSAS v1.4 END
              } finally {
                setBusy(false);
              }
            }}
          >
            {isEdit ? "Save changes" : "Add candidate"}
          </button>
        </div>
      </div>
    </div>
  );
};
