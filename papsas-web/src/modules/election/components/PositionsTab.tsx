// src/modules/election/components/PositionsTab.tsx
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  type Position,
  listPositions,
  createPosition,
  updatePosition,
  deletePosition,
} from "../services/electionApi";

import "./PositionsTab.css";

export const PositionsTab: React.FC<{ electionId: number }> = ({ electionId }) => {
  const [rows, setRows] = useState<Position[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [busyId, setBusyId] = useState<number | "new" | null>(null);

  const refresh = useCallback(async () => {
    if (!electionId) return;
    setLoading(true);
    setErr(null);
    try {
      const data = await listPositions(electionId);
      setRows(
        data.sort(
          (a, b) => (a.sort ?? 0) - (b.sort ?? 0) || a.id - b.id
        )
      );
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Failed to load positions");
    } finally {
      setLoading(false);
    }
  }, [electionId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const canAdd = title.trim().length > 0 && !busyId;

  const add = async (t: string, presetSort?: number) => {
    if (!electionId) return;
    setBusyId("new");
    try {
      const created = await createPosition(electionId, {
        title: t.trim(),
        enabled: true,
        sort: presetSort ?? rows.length + 1,
      });
      setRows((r) => [...r, created]);
      setTitle("");
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : "Create failed");
    } finally {
      setBusyId(null);
    }
  };

  const saveTitle = async (row: Position, newTitle: string) => {
    setBusyId(row.id);
    try {
      const updated = await updatePosition(row.id, {
        title: newTitle.trim() || row.title,
      });
      setRows((r) => r.map((x) => (x.id === row.id ? updated : x)));
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : "Rename failed");
    } finally {
      setBusyId(null);
    }
  };

  const remove = async (row: Position) => {
    if (!confirm(`Delete position "${row.title}"?`)) return;
    setBusyId(row.id);
    const snapshot = rows;
    setRows((r) => r.filter((x) => x.id !== row.id));
    try {
      await deletePosition(row.id);
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : "Delete failed");
      setRows(snapshot);
    } finally {
      setBusyId(null);
    }
  };

  const none = !loading && rows.length === 0;

  return (
    <div className="positions-tab">
      {/* Header */}
      <div className="positions-header">
        <div>
          <h2 className="positions-title">Positions</h2>
          <p className="positions-subtitle">
            Manage which positions appear on the ballot for this election.
          </p>
        </div>
        <div className="positions-count-badge">
          {rows.length} {rows.length === 1 ? "position" : "positions"}
        </div>
      </div>

      {/* Quick add card */}
      <div className="positions-card">
        <div className="positions-quick-add">
          <label
            htmlFor="position-quick-add"
            className="positions-quick-add-label"
          >
            Quick add
          </label>
          <div className="positions-quick-add-row">
            <input
              id="position-quick-add"
              className="positions-input"
              placeholder='e.g., "Adviser"'
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
            <button
              className="btn btn-primary positions-add-btn"
              disabled={!canAdd}
              onClick={() => add(title)}
            >
              Add
            </button>
          </div>
          <p className="positions-quick-add-hint">
            Add positions one by one. You can rename or delete them below.
          </p>
        </div>
      </div>

      {/* States */}
      {err && <div className="positions-error">{err}</div>}
      {loading && <div className="positions-loading">Loading…</div>}
      {none && (
        <div className="positions-empty">
          No positions yet. Add one above.
        </div>
      )}

      {/* Table */}
      {rows.length > 0 && (
        <div className="positions-card">
          <div className="positions-table-wrapper">
            <table className="positions-table">
              <thead>
                <tr>
                  <th className="positions-col-sort">#</th>
                  <th>Title</th>
                  <th className="positions-col-actions">Actions</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, idx) => (
                  <tr key={row.id}>
                    <td className="positions-cell-sort">
                      {row.sort ?? idx + 1}
                    </td>
                    <td>
                      <InlineEditable
                        value={row.title}
                        onSave={(v) => saveTitle(row, v)}
                        disabled={busyId === row.id}
                      />
                    </td>
                    <td className="positions-cell-actions">
                      <button
                        className="positions-delete-link"
                        disabled={busyId === row.id}
                        onClick={() => remove(row)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

function InlineEditable({
  value,
  onSave,
  disabled,
}: {
  value: string;
  onSave: (v: string) => void;
  disabled?: boolean;
}) {
  const [v, setV] = useState(value);
  useEffect(() => setV(value), [value]);
  const changed = useMemo(
    () => v.trim() !== value.trim(),
    [v, value]
  );

  return (
    <div className="positions-inline-edit">
      <input
        className="positions-inline-input"
        value={v}
        onChange={(e) => setV(e.target.value)}
        disabled={disabled}
      />
      <button
        className="positions-inline-save-btn"
        disabled={!changed || disabled}
        onClick={() => onSave(v)}
      >
        Save
      </button>
    </div>
  );
}
