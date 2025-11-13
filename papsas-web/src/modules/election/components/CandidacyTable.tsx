import React, { useCallback, useEffect, useMemo, useState } from "react";
import type { Candidacy } from "../services/candidacyApi";
import {
  deleteCandidacy,
  listCandidacies,
  updateCandidacy,
} from "../services/candidacyApi";
import { EditCandidateModal } from "./CandidacyFormModal2";
import { patchCandidacy } from "../services/candidacyAdminApi";
import { AddCandidateModal } from "./AddCandidateModal";
import type { Position } from "../services/electionApi";
import { listPositions } from "../services/electionApi";
import { useToast } from "../../ui/Toast";
import { Plus, Edit2, Trash2, ChevronDown } from "lucide-react";

const isRowActive = (row: Candidacy) => Boolean(row.candidacyStatus ?? row.status);

export const CandidacyTable: React.FC<{
  electionId: number;
  readOnly?: boolean;
}> = ({ electionId, readOnly }) => {
  const [rows, setRows] = useState<Candidacy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setErr] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<
    "all" | "enabled" | "disabled"
  >("all");
  const [adding, setAdding] = useState(false);
  const [editing, setEditing] = useState<Candidacy | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const toast = useToast();

  const refresh = useCallback(async () => {
    setLoading(true);
    setErr(null);
    try {
      const data = await listCandidacies(electionId);
      setRows(data);
    } catch (e) {
      const err = e as { message?: string };
      setErr(err.message || "Failed to load candidates");
    } finally {
      setLoading(false);
    }
  }, [electionId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    listPositions(electionId)
      .then(setPositions)
      .catch(() => setPositions([]));
  }, [electionId]);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return rows.filter((r) => {
      const active = isRowActive(r);
      const statusOk =
        statusFilter === "all" ||
        (statusFilter === "enabled" && active) ||
        (statusFilter === "disabled" && !active);
      const textOk =
        !q ||
        `${r.name} ${r.positionTitle ?? ""} ${r.credentials ?? ""}`
          .toLowerCase()
          .includes(q);
      return statusOk && textOk;
    });
  }, [rows, search, statusFilter]);

  /* -------------------------------------------------------------
     UI – ONLY MARKUP & CLASSES CHANGED
     ------------------------------------------------------------- */
  return (
    <div className="candidacy-table-container">
      {/* Toolbar */}
<div className="candidacy-toolbar">
  {/* Search */}
  <div className="candidacy-search-wrapper">
    <input
      type="text"
      placeholder="Search candidates…"
      className="candidacy-search-input"
      value={search}
      onChange={(e) => setSearch(e.target.value)}
    />
  </div>

  {/* Filter */}
  <div className="candidacy-filter">
    <select
      className="candidacy-filter-select"
      value={statusFilter}
      onChange={(e) =>
        setStatusFilter(e.target.value as "all" | "enabled" | "disabled")
      }
    >
      <option value="all">All</option>
      <option value="enabled">Enabled</option>
      <option value="disabled">Disabled</option>
    </select>
    <ChevronDown className="candidacy-filter-chevron" size={16} />
  </div>

  {/* FAB – NOW INLINE */}
  {!readOnly && (
    <button
      className="candidacy-fab-inline"
      title="Add Candidate"
      onClick={() => setAdding(true)}
      disabled={adding}
    >
      <Plus size={20} />
    </button>
  )}
</div>

      {/* Errors / Loading */}
      {error && <div className="admin-alert admin-alert-error">{error}</div>}
      {loading && <div className="text-center py-4">Loading…</div>}

      {/* Table Card */}
      {!loading && (
        <div className="candidacy-card">
          <table className="candidacy-table">
            <thead>
              <tr>
                <th>Candidate</th>
                <th>Position</th>
                <th>Credentials</th>
                <th>Status</th>
                {!readOnly && <th className="text-right">Actions</th>}
              </tr>
            </thead>

            <tbody>
              {filtered.map((row) => (
                <tr key={row.id} className="candidacy-row">
                  {/* Candidate */}
                  <td>
                    <div className="candidacy-candidate">
                      <div className="font-medium">{row.name}</div>
                      {row.email && (
                        <div className="text-muted text-sm">{row.email}</div>
                      )}
                    </div>
                  </td>

                  {/* Position */}
                  <td>
                    {readOnly ? (
                      row.positionTitle ?? row.positionId ?? "—"
                    ) : (
                      <select
                        className="candidacy-position-select"
                        value={row.positionId ?? ""}
                        onChange={async (e) => {
                          const val = e.target.value;
                          const nextId = val === "" ? null : Number(val);
                          const prevId = row.positionId;
                          setRows((rs) =>
                            rs.map((r) =>
                              r.id === row.id
                                ? {
                                    ...r,
                                    positionId: nextId,
                                    positionTitle:
                                      positions.find((p) => p.id === nextId)
                                        ?.title ?? undefined,
                                  }
                                : r
                            )
                          );
                          try {
                            await patchCandidacy(electionId, row.id, {
                              position_id: nextId,
                            });
                            toast.success("Position updated");
                          } catch (err) {
                            setRows((rs) =>
                              rs.map((r) =>
                                r.id === row.id
                                  ? {
                                      ...r,
                                      positionId: prevId,
                                      positionTitle:
                                        positions.find(
                                          (p) => p.id === (prevId ?? -1)
                                        )?.title ?? undefined,
                                    }
                                  : r
                              )
                            );
                            toast.apiError?.(err, "Failed to update position");
                          }
                        }}
                      >
                        <option value="">Unassigned</option>
                        {positions.map((p) => (
                          <option key={p.id} value={p.id}>
                            {p.title}
                          </option>
                        ))}
                      </select>
                    )}
                  </td>

                  {/* Credentials */}
                  <td className="candidacy-credentials">{row.credentials}</td>

                  {/* Status */}
                  <td>
                    {!readOnly ? (
                      <label className="candidacy-toggle">
                        <input
                          type="checkbox"
                          checked={isRowActive(row)}
                          aria-pressed={isRowActive(row)}
                          onChange={async () => {
                            const prevStatus = row.candidacyStatus ?? row.status;
                            const nextStatus = !prevStatus;
                            setRows((rs) =>
                              rs.map((r) =>
                                r.id === row.id
                                  ? {
                                      ...r,
                                      status: nextStatus,
                                      candidacyStatus: nextStatus,
                                    }
                                  : r
                              )
                            );
                            if (import.meta.env.DEV) {
                              console.log("DEBUG toggle candidacy", {
                                electionId,
                                candidacyId: row.id,
                                nextStatus,
                                row,
                              });
                            }
                            try {
                              await updateCandidacy(electionId, row.id, {
                                candidacyStatus: nextStatus,
                              });
                              toast.success("Toggle saved");
                              await refresh();
                            } catch (err) {
                              toast.apiError?.(err, "Update failed");
                              setRows((rs) =>
                                rs.map((r) =>
                                  r.id === row.id
                                    ? {
                                        ...r,
                                        status: prevStatus,
                                        candidacyStatus: prevStatus,
                                      }
                                    : r
                                )
                              );
                            }
                          }}
                        />
                        <span className="candidacy-toggle-slider" />
                        <span className="candidacy-toggle-label">
                          {isRowActive(row) ? "Enabled" : "Disabled"}
                        </span>
                      </label>
                    ) : (
                      <span
                        className={
                          isRowActive(row) ? "text-green-700" : "text-gray-400"
                        }
                      >
                        {isRowActive(row) ? "Enabled" : "Disabled"}
                      </span>
                    )}
                  </td>

                  {/* Actions */}
                  {!readOnly && (
                    <td className="candidacy-actions">
                      <button
                        className="candidacy-btn-edit"
                        title="Edit"
                        onClick={() => setEditing(row)}
                        disabled={editing !== null}  // Only disable while editing this row
                      >
                        <Edit2 size={14} />
                      </button>
                      <button
                        className="candidacy-btn-delete"
                        title="Remove"
                        onClick={async () => {
                          if (!confirm("Remove this candidacy?")) return;
                          const prev = rows;
                          setRows((rs) => rs.filter((r) => r.id !== row.id));
                          try {
                            await deleteCandidacy(electionId, row.id);
                            await refresh();
                            toast.success("Candidate removed");
                          } catch (err) {
                            toast.apiError?.(err, "Delete failed");
                            setRows(prev);
                          }
                        }}
                        disabled={adding || !!editing}
                      >
                        <Trash2 size={14} />
                      </button>
                    </td>
                  )}
                </tr>
              ))}

              {/* Empty */}
              {!filtered.length && (
                <tr>
                  <td
                    colSpan={readOnly ? 4 : 5}
                    className="text-center text-muted py-8"
                  >
                    No candidates found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Modals – unchanged */}
      {adding && (
        <AddCandidateModal
          electionId={electionId}
          open={adding}
          positions={positions}
          onClose={() => setAdding(false)}
          onAdded={async () => {
            await refresh();
            toast.success("Candidate added");
            setAdding(false);
          }}
        />
      )}
      {editing && (
        <EditCandidateModal
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
              position_id: data.positionId ?? null,
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
