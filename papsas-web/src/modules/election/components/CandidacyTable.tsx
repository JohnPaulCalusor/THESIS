import React, { useCallback, useEffect, useMemo, useState } from "react";
import type { AxiosError } from "axios";
import type { Candidacy } from "../services/candidacyApi";
import { deleteCandidacy, listCandidacies, updateCandidacy } from "../services/candidacyApi";
import { CandidacyFormModal as CandidacyFormModal2 } from "./CandidacyFormModal2";
import { patchCandidacy } from "../services/candidacyAdminApi";
import { AddCandidateModal } from "./AddCandidateModal";
import type { Position } from "../services/electionApi";
import { listPositions } from "../services/electionApi";
import { useToast } from "../../ui/Toast";

export type CandidacyRow = {
  id: number;
  candidate: { id: number; name: string; email?: string };
  position: { id: number | null; title: string };
  credentials?: string;
  status?: "pending" | "approved" | "rejected" | string;
  active: boolean;
  created_at?: string;
  updated_at?: string;
  source: Candidacy;
};

const toRow = (c: Candidacy): CandidacyRow => ({
  id: c.id,
  candidate: { id: c.id, name: c.name, email: c.email },
  position: {
    id: c.positionId ?? null,
    title: c.positionTitle || "Unassigned",
  },
  credentials: c.credentials,
  active: Boolean(c._status),
  status: c._status ? "approved" : "disabled",
  source: { ...c },
});

export const CandidacyTable: React.FC<{ electionId: number; readOnly?: boolean }> = ({ electionId, readOnly }) => {
  const [rows, setRows] = useState<CandidacyRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setErr] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "enabled" | "disabled">("all");
  const [adding, setAdding] = useState(false);
  const [editing, setEditing] = useState<CandidacyRow | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const toast = useToast();

  const refresh = useCallback(async () => {
    setLoading(true); setErr(null);
    try {
      const data = await listCandidacies(electionId);
      setRows(data.map(toRow));
    } catch (e: unknown) {
      const info = e as { message?: string };
      setErr(info.message || "Failed to load candidates");
    } finally {
      setLoading(false);
    }
  }, [electionId]);

  useEffect(() => { void refresh(); }, [refresh]);
  useEffect(() => { listPositions(electionId).then(setPositions).catch(() => setPositions([])); }, [electionId]);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return rows.filter((r) => {
      const statusOk =
        statusFilter === "all" ||
        (statusFilter === "enabled" && r.active) ||
        (statusFilter === "disabled" && !r.active);
      const textOk =
        !q ||
        `${r.candidate.name} ${r.candidate.email ?? ""} ${r.position.title} ${r.credentials ?? ""}`
          .toLowerCase()
          .includes(q);
      return statusOk && textOk;
    });
  }, [rows, search, statusFilter]);

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <input className="border rounded p-2 flex-1" placeholder="Search…" value={search} onChange={e => setSearch(e.target.value)} />
        <select
          className="border rounded p-2"
          value={statusFilter}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setStatusFilter(e.target.value as "all" | "enabled" | "disabled")}
        >
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
                    <div className="font-medium">{row.candidate.name}</div>
                    {row.candidate.email && <div className="text-gray-500 text-xs">{row.candidate.email}</div>}
                  </td>
                  <td>
                    {readOnly ? (
                      row.position.title ?? row.position.id ?? "�"
                    ) : (
                      <select
                        className="border rounded p-1"
                        value={row.position.id ?? ""}
                        onChange={async (e: React.ChangeEvent<HTMLSelectElement>) => {
                          const val = e.target.value;
                          const nextId = val === "" ? null : Number(val);
                          const prevId = row.position.id;
                          setRows((rs) =>
                            rs.map((r) =>
                              r.id === row.id
                                ? {
                                    ...r,
                                    position: {
                                      id: nextId,
                                      title: positions.find((p) => p.id === nextId)?.title ?? "Unassigned",
                                    },
                                    source: { ...r.source, positionId: nextId },
                                  }
                                : r
                            )
                          );
                          try {
                            await patchCandidacy(electionId, row.id, { position_id: nextId });
                            toast.success("Position updated");
                          } catch (err: unknown) {
                            const info = err as AxiosError<unknown>;
                            setRows((rs) =>
                              rs.map((r) =>
                                r.id === row.id
                                  ? {
                                      ...r,
                                      position: {
                                        id: prevId,
                                        title:
                                          positions.find((p) => p.id === (prevId ?? -1))?.title ?? "Unassigned",
                                      },
                                      source: { ...r.source, positionId: prevId },
                                    }
                                  : r
                              )
                            );
                            toast.apiError(info, "Failed to update position");
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
                          checked={row.active}
                          onChange={async (e) => {
                            const nextActive = e.target.checked;
                            const prevStatus = row.status;
                            const prevActive = row.active;
                            setRows((rs) =>
                              rs.map((r) =>
                                r.id === row.id
                                  ? {
                                      ...r,
                                      status: nextActive ? "approved" : "disabled",
                                      active: nextActive,
                                      source: { ...r.source, _status: nextActive },
                                    }
                                  : r
                              )
                            );
                            try {
                              await updateCandidacy(electionId, row.id, { _status: nextActive });
                            } catch (err: unknown) {
                              const info = err as AxiosError<unknown>;
                              toast.apiError(info, "Update failed");
                              setRows((rs) =>
                                rs.map((r) =>
                                  r.id === row.id
                                    ? {
                                        ...r,
                                        status: prevStatus,
                                        active: prevActive,
                                        source: { ...r.source, _status: prevActive },
                                      }
                                    : r
                                )
                              );
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
                          } catch (err: unknown) {
                            // >>> PAPSAS v1.4 BEGIN
                            const info = err as AxiosError<unknown>;
                            toast.apiError(info, "Delete failed");
                            // <<< PAPSAS v1.4 END
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
            name: editing.candidate.name,
            email: editing.candidate.email,
            positionId: editing.position.id ?? null,
            credentials: editing.credentials,
            status: editing.active,
          }}
          onClose={() => setEditing(null)}
              onSubmit={async (data) => {
                await updateCandidacy(electionId, data.id!, {
                  memberId: data.memberId,
                  name: data.name,
                  email: data.email,
                  positionId: data.positionId,
                  credentials: data.credentials,
                  _status: data.status ?? undefined,
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
