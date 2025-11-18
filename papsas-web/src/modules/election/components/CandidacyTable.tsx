// src/modules/election/components/CandidacyTable.tsx
import React, { useCallback, useEffect, useMemo, useState } from "react";
import type { AxiosError } from "axios";
import type { Candidacy } from "../services/candidacyApi";
import {
  deleteCandidacy,
  listCandidacies,
  updateCandidacy,
} from "../services/candidacyApi";
import { CandidacyFormModal as CandidacyFormModal2 } from "./CandidacyFormModal2";
import { patchCandidacy } from "../services/candidacyAdminApi";
import type { Position } from "../services/electionApi";
import { listPositions } from "../services/electionApi";
import { AddCandidateModal } from "./AddCandidateModal";
import { useToast } from "../../ui/Toast";

import "./CandidacyTable.css";

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

export const CandidacyTable: React.FC<{
  electionId: number;
  readOnly?: boolean;
}> = ({ electionId, readOnly }) => {
  const [rows, setRows] = useState<CandidacyRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setErr] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [adding, setAdding] = useState(false);
  const [editing, setEditing] = useState<CandidacyRow | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const toast = useToast();

  const refresh = useCallback(async () => {
    setLoading(true);
    setErr(null);
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
      const textOk =
        !q ||
        `${r.candidate.name} ${r.candidate.email ?? ""} ${
          r.position.title
        } ${r.credentials ?? ""}`
          .toLowerCase()
          .includes(q);

      return textOk;
    });
  }, [rows, search]);

  return (
    <div className="candidacy-admin">
      {/* Toolbar */}
      <div className="candidacy-admin-toolbar">
        <div className="candidacy-admin-search-wrap">
          <label
            className="candidacy-admin-search-label"
            htmlFor="candidate-search"
          >
            Search
          </label>
          <input
            id="candidate-search"
            className="candidacy-admin-search-input"
            placeholder="Search by name, email, position, or credentials…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="candidacy-admin-toolbar-right">
          {!readOnly && (
            <button
              className="btn btn-primary candidacy-admin-add-btn"
              onClick={() => setAdding(true)}
              disabled={adding || !!editing}
            >
              + Add candidate
            </button>
          )}
        </div>
      </div>

      {error && <div className="candidacy-admin-error">{error}</div>}
      {loading && <div className="candidacy-admin-loading">Loading…</div>}

      {!loading && (
        <div className="card candidacy-admin-table">
          <div className="candidacy-admin-table-scroll">
            <table className="candidacy-admin-table-grid">
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Position</th>
                  <th>Credentials</th>
                  {!readOnly && (
                    <th className="candidacy-admin-actions-col">Actions</th>
                  )}
                </tr>
              </thead>
              <tbody>
                {filtered.map((row) => (
                  <tr key={row.id}>
                    <td>
                      <div className="candidacy-admin-name">
                        {row.candidate.name}
                      </div>
                      {row.candidate.email && (
                        <div className="candidacy-admin-email">
                          {row.candidate.email}
                        </div>
                      )}
                    </td>
                    <td>
                      {readOnly ? (
                        row.position.title ?? row.position.id ?? "�"
                      ) : (
                        <select
                          className="candidacy-admin-position-select"
                          value={row.position.id ?? ""}
                          onChange={async (
                            e: React.ChangeEvent<HTMLSelectElement>
                          ) => {
                            const val = e.target.value;
                            const nextId = val === "" ? null : Number(val);
                            const prevId = row.position.id;

                            // optimistic update
                            setRows((rs) =>
                              rs.map((r) =>
                                r.id === row.id
                                  ? {
                                      ...r,
                                      position: {
                                        id: nextId,
                                        title:
                                          positions.find(
                                            (p) => p.id === nextId
                                          )?.title ?? "Unassigned",
                                      },
                                      source: {
                                        ...r.source,
                                        positionId: nextId,
                                      },
                                    }
                                  : r
                              )
                            );
                            try {
                              await patchCandidacy(electionId, row.id, {
                                position_id: nextId,
                              });
                              toast.success("Position updated");
                            } catch (err: unknown) {
                              const info = err as AxiosError<unknown>;
                              toast.apiError(info, "Failed to update position");
                              // rollback
                              setRows((rs) =>
                                rs.map((r) =>
                                  r.id === row.id
                                    ? {
                                        ...r,
                                        position: {
                                          id: prevId,
                                          title:
                                            positions.find(
                                              (p) => p.id === (prevId ?? -1)
                                            )?.title ?? "Unassigned",
                                        },
                                        source: {
                                          ...r.source,
                                          positionId: prevId,
                                        },
                                      }
                                    : r
                                )
                              );
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
                    <td className="candidacy-admin-credentials">
                      {row.credentials}
                    </td>
                    {!readOnly && (
                      <td className="candidacy-admin-actions">
                        <button
                          className="candidacy-admin-link"
                          onClick={() => setEditing(row)}
                          disabled={adding || !!editing}
                        >
                          Edit
                        </button>
                        <button
                          className="candidacy-admin-link candidacy-admin-link--danger"
                          onClick={async () => {
                            if (!confirm("Remove this candidacy?")) return;
                            const prev = rows;
                            // optimistic removal
                            setRows((rs) => rs.filter((r) => r.id !== row.id));
                            try {
                              await deleteCandidacy(electionId, row.id);
                              await refresh();
                              toast.success("Candidate removed");
                            } catch (err: unknown) {
                              const info = err as AxiosError<unknown>;
                              toast.apiError(info, "Delete failed");
                              setRows(prev);
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
                  <tr>
                    <td
                      colSpan={readOnly ? 3 : 4}
                      className="candidacy-admin-empty-state"
                    >
                      No candidates found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Modals */}
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
