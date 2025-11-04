import React, { useCallback, useEffect, useMemo, useState } from "react";
import type { Candidacy } from "../services/candidacyApi";
import { createCandidacy, deleteCandidacy, listCandidacies, updateCandidacy } from "../services/candidacyApi";
import { CandidacyFormModal as CandidacyFormModal2 } from "./CandidacyFormModal2";
import { patchCandidacy } from "../services/candidacyAdminApi";
import { AddCandidateModal } from "./AddCandidateModal";
import type { Position } from "../services/electionApi";
import { listPositions } from "../services/electionApi";
import { useToast } from "../../ui/Toast";

export const CandidacyTable: React.FC<{ electionId: number; readOnly?: boolean }> = ({ electionId, readOnly }) => {
  const [rows, setRows] = useState<Candidacy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setErr] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "enabled" | "disabled">("all");
  const [adding, setAdding] = useState(false);
  const [editing, setEditing] = useState<Candidacy | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const toast = useToast();

  const refresh = useCallback(async () => {
    setLoading(true); setErr(null);
    try {
      const data = await listCandidacies(electionId);
      setRows(data);
    } catch (e: any) {
      setErr(e?.message || "Failed to load candidates");
    } finally {
      setLoading(false);
    }
  }, [electionId]);

  useEffect(() => { void refresh(); }, [refresh]);
  useEffect(() => { listPositions(electionId).then(setPositions).catch(() => setPositions([])); }, [electionId]);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return rows.filter(r => {
      const statusOk =
        statusFilter === "all" ||
        (statusFilter === "enabled" && r.status) ||
        (statusFilter === "disabled" && !r.status);
      const textOk = !q || `${r.name} ${r.positionTitle ?? ""} ${r.credentials ?? ""}`.toLowerCase().includes(q);
      return statusOk && textOk;
    });
  }, [rows, search, statusFilter]);

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <input className="border rounded p-2 flex-1" placeholder="Search…" value={search} onChange={e => setSearch(e.target.value)} />
        <select className="border rounded p-2" value={statusFilter} onChange={e => setStatusFilter(e.target.value as any)}>
          <option value="all">All</option>
          <option value="enabled">Enabled</option>
          <option value="disabled">Disabled</option>
        </select>
        {!readOnly && (
          <button className="px-3 py-2 rounded bg-blue-600 text-white" onClick={() => setAdding(true)} disabled={adding || !!editing}>+ Add Candidate</button>
        )}
      </div>

      {error && <div className="text-red-600">{error}</div>}
      {loading && <div>Loading…</div>}

      {!loading && (
        <div className="overflow-auto border rounded">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50">
              <tr className="[&>th]:px-3 [&>th]:py-2 text-left">
                <th>Candidate</th>
                <th>Position</th>
                <th>Credentials</th>
                <th>Status</th>
                {!readOnly && <th className="w-32">Actions</th>}
              </tr>
            </thead>
            <tbody>
              {filtered.map(row => (
                <tr key={row.id} className="border-t [&>td]:px-3 [&>td]:py-2 align-top">
                  <td>
                    <div className="font-medium">{row.name}</div>
                    {row.email && <div className="text-gray-500 text-xs">{row.email}</div>}
                  </td>
                  <td>
                    {readOnly ? (
                      row.positionTitle ?? row.positionId ?? "—"
                    ) : (
                      <select
                        className="border rounded p-1"
                        value={row.positionId ?? ""}
                        onChange={async (e) => {
                          const val = e.target.value;
                          const nextId = val === "" ? null : Number(val);
                          const prevId = row.positionId;
                          setRows(rs => rs.map(r => (r.id === row.id ? { ...r, positionId: nextId, positionTitle: positions.find(p=>p.id===nextId)?.title ?? undefined } : r)));
                          try {
                            await patchCandidacy(electionId, row.id, { position_id: nextId });
                            toast.success("Position updated");
                          } catch (err: any) {
                            setRows(rs => rs.map(r => (r.id === row.id ? { ...r, positionId: prevId, positionTitle: positions.find(p=>p.id===prevId ?? -1)?.title ?? undefined } : r)));
                            toast.error(err?.message || "Failed to update position");
                          }
                        }}
                      >
                        <option value="">Unassigned</option>
                        {positions.map(p => (
                          <option key={p.id} value={p.id}>{p.title}</option>
                        ))}
                      </select>
                    )}
                  </td>
                  <td className="whitespace-pre-wrap">{row.credentials}</td>
                  <td>
                    {!readOnly ? (
                      <label className="inline-flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={row.status}
                          onChange={async (e) => {
                            const prev = row.status;
                            setRows(rs => rs.map(r => (r.id === row.id ? { ...r, status: e.target.checked } : r)));
                            try {
                              await updateCandidacy(electionId, row.id, { status: e.target.checked });
                            } catch (err: any) {
                              alert(err?.message || "Update failed");
                              setRows(rs => rs.map(r => (r.id === row.id ? { ...r, status: prev } : r)));
                            }
                          }}
                        />
                        <span>{row.status ? "Enabled" : "Disabled"}</span>
                      </label>
                    ) : (
                      <span className={row.status ? "text-green-700" : "text-gray-400"}>
                        {row.status ? "Enabled" : "Disabled"}
                      </span>
                    )}
                  </td>
                  {!readOnly && (
                    <td className="space-x-2">
                      <button className="text-blue-700 underline" onClick={() => setEditing(row)} disabled={adding || !!editing}>Edit</button>
                      <button
                        className="text-red-700 underline"
                        onClick={async () => {
                          if (!confirm("Remove this candidacy?")) return;
                          const prev = rows;
                          setRows(rs => rs.filter(r => r.id !== row.id)); // optimistic
                          try {
                            await deleteCandidacy(electionId, row.id);
                            await refresh();
                            toast.success("Candidate removed");
                          } catch (err: any) {
                            toast.error(err?.message || "Delete failed");
                            alert(err?.message || "Delete failed");
                            setRows(prev); // rollback
                          }
                        }}
                        disabled={adding || !!editing}
                      >
                        Remove
                      </button>
                    </td>
                  )}
                </tr>
              ))}
              {!filtered.length && (
                <tr><td colSpan={readOnly ? 4 : 5} className="text-center text-gray-500 py-6">No candidates found.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Modals */}
      {adding && (
        <AddCandidateModal
          electionId={electionId}
          open={adding}
          positions={positions}
          onClose={() => setAdding(false)}
          onAdded={async () => { await refresh(); toast.success("Candidate added"); setAdding(false); }}
        />
      )}
      {editing && (
        <CandidacyFormModal2
          electionId={electionId}
          open={!!editing}
          positions={positions}
          initial={{
            id: editing.id,
            name: editing.name,
            email: editing.email,
            positionId: editing.positionId ?? null,
            credentials: editing.credentials,
            status: editing.status,
          }}
          onClose={() => setEditing(null)}
          onSubmit={async (data) => {
            await updateCandidacy(electionId, data.id!, {
              memberId: data.memberId,
              name: data.name,
              email: data.email,
              positionId: data.positionId,
              credentials: data.credentials,
            });
            await refresh();
            toast.success("Candidate updated");
            setEditing(null);
          }}
        />
      )}
    </div>
  );
};
