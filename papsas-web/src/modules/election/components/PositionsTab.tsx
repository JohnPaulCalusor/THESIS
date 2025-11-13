// src/components/PositionsTab.tsx
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  type Position,
  listPositions,
  createPosition,
  updatePosition,
  deletePosition,
} from "../services/electionApi";
import {Trash2 } from "lucide-react";
import { useToast } from "../../ui/Toast";

type PositionsError = { message?: string };

export const PositionsTab: React.FC<{ electionId: number }> = ({
  electionId,
}) => {
  const [rows, setRows] = useState<Position[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [busyId, setBusyId] = useState<number | "new" | null>(null);
  const toast = useToast();

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
    } catch (error) {
      const err = error as PositionsError;
      setErr(err.message || "Failed to load positions");
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
      toast.success("Position added");
      setTitle("");
    } catch (error) {
      const err = error as PositionsError;
      toast.error(err.message || "Create failed");
    } finally {
      setBusyId(null);
    }
  };

  const toggle = async (row: Position) => {
    setBusyId(row.id);
    try {
      const updated = await updatePosition(row.id, {
        enabled: !row.enabled,
      });
      setRows((r) =>
        r.map((x) => (x.id === row.id ? updated : x))
      );
      toast.success("Position updated");
    } catch (error) {
      const err = error as PositionsError;
      toast.error(err.message || "Update failed");
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
      setRows((r) =>
        r.map((x) => (x.id === row.id ? updated : x))
      );
      toast.success("Position renamed");
    } catch (error) {
      const err = error as PositionsError;
      toast.error(err.message || "Rename failed");
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
      toast.success("Position deleted");
    } catch (error) {
      const err = error as PositionsError;
      toast.error(err.message || "Delete failed");
      setRows(snapshot);
    } finally {
      setBusyId(null);
    }
  };

  const none = !loading && rows.length === 0;

  /* -------------------------------------------------------------
     UI – ONLY MARKUP & CLASSES CHANGED
     ------------------------------------------------------------- */
  return (
    <div className="positions-tab-container">
      {/* Quick-add toolbar */}
      <div className="positions-toolbar">
        <div className="flex-1">
          <label className="positions-label">Quick add</label>
          <div className="positions-add-row">
            <input
              className="positions-input"
              placeholder='e.g., "Adviser"'
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
            <button
              className="positions-add-btn"
              disabled={!canAdd}
              onClick={() => add(title)}
            >
              Add
            </button>
          </div>
        </div>

      </div>

      {/* Alerts */}
      {err && <div className="admin-alert admin-alert-error">{err}</div>}
      {loading && <div className="text-center py-6">Loading positions…</div>}
      {none && (
        <div className="empty-state">
          <div className="text-2xl mb-2">No positions yet</div>
          <div className="text-sm">
            Type a title above and click <strong>Add</strong>.
          </div>
        </div>
      )}

      {/* Table Card */}
      {rows.length > 0 && (
        <div className="positions-card">
          <table className="positions-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Title</th>
                <th>Enabled</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, idx) => (
                <tr key={row.id} className="positions-row">
                  <td className="positions-index">
                    {row.sort ?? idx + 1}
                  </td>

                  {/* Inline Editable */}
                  <td>
                    <InlineEditable
                      value={row.title}
                      onSave={(v) => saveTitle(row, v)}
                      disabled={busyId === row.id}
                    />
                  </td>

                  {/* Enabled Toggle */}
                  <td>
                    <label className="positions-toggle">
                      <input
                        type="checkbox"
                        checked={!!row.enabled}
                        onChange={() => toggle(row)}
                        disabled={busyId === row.id}
                      />
                      <span className="positions-toggle-slider" />
                      <span className="positions-toggle-label">
                        {row.enabled ? "Enabled" : "Disabled"}
                      </span>
                    </label>
                  </td>

                  {/* Delete */}
                  <td className="positions-actions">
                    <button
                      className="positions-btn-delete"
                      title="Delete"
                      onClick={() => remove(row)}
                      disabled={busyId === row.id}
                    >
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

/* -------------------------------------------------------------
   InlineEditable – unchanged logic, only styled
   ------------------------------------------------------------- */
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
        className="positions-inline-save"
        disabled={!changed || disabled}
        onClick={() => onSave(v)}
      >
        Save
      </button>
    </div>
  );
}
