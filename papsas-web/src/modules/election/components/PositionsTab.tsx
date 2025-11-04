import { useEffect, useMemo, useState } from "react";
import { type Position, listPositions, createPosition, updatePosition, deletePosition } from "../services/electionApi";

export const PositionsTab: React.FC<{ electionId: number }> = ({ electionId }) => {
  const [rows, setRows] = useState<Position[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [busyId, setBusyId] = useState<number | "new" | null>(null);

  const refresh = async () => {
    if (!electionId) return;
    setLoading(true); setErr(null);
    try {
      const data = await listPositions(electionId);
      setRows(data.sort((a,b) => (a.sort ?? 0) - (b.sort ?? 0) || a.id - b.id));
    } catch (e: any) {
      setErr(e?.message || "Failed to load positions");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void refresh(); }, [electionId]);

  const canAdd = title.trim().length > 0 && !busyId;

  const add = async (t: string, presetSort?: number) => {
    if (!electionId) return;
    setBusyId("new");
    try {
      const created = await createPosition(electionId, { title: t.trim(), enabled: true, sort: presetSort ?? (rows.length + 1) });
      setRows((r) => [...r, created]);
      setTitle("");
    } catch (e: any) {
      alert(e?.message || "Create failed");
    } finally {
      setBusyId(null);
    }
  };

  const toggle = async (row: Position) => {
    setBusyId(row.id);
    try {
      const updated = await updatePosition(row.id, { enabled: !row.enabled });
      setRows(r => r.map(x => x.id === row.id ? updated : x));
    } catch (e: any) {
      alert(e?.message || "Update failed");
    } finally {
      setBusyId(null);
    }
  };

  const saveTitle = async (row: Position, newTitle: string) => {
    setBusyId(row.id);
    try {
      const updated = await updatePosition(row.id, { title: newTitle.trim() || row.title });
      setRows(r => r.map(x => x.id === row.id ? updated : x));
    } catch (e: any) {
      alert(e?.message || "Rename failed");
    } finally {
      setBusyId(null);
    }
  };

  const remove = async (row: Position) => {
    if (!confirm(`Delete position "${row.title}"?`)) return;
    setBusyId(row.id);
    const snapshot = rows;
    setRows(r => r.filter(x => x.id !== row.id));
    try {
      await deletePosition(row.id);
    } catch (e: any) {
      alert(e?.message || "Delete failed");
      setRows(snapshot);
    } finally {
      setBusyId(null);
    }
  };

  const none = !loading && rows.length === 0;

  return (
    <div className="p-3">
      <div className="flex items-end gap-2 mb-4">
        <div className="flex-1">
          <label className="block text-sm font-medium">Quick add</label>
          <div className="flex gap-2">
            <input
              className="border rounded p-2 w-full"
              placeholder='e.g., "Adviser"'
              value={title}
              onChange={e => setTitle(e.target.value)}
            />
            <button
              className="px-3 py-2 rounded bg-blue-600 text-white disabled:opacity-50"
              disabled={!canAdd}
              onClick={() => add(title)}
            >
              Add
            </button>
            {/* Preset buttons removed per request; free-type title is enough */}
          </div>
        </div>
      </div>

      {err && <div className="text-red-600 mb-2">{err}</div>}
      {loading && <div>Loading…</div>}
      {none && <div className="text-gray-500">No positions yet. Add one above.</div>}

      {rows.length > 0 && (
        <table className="w-full text-sm border">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left p-2 w-16">#</th>
              <th className="text-left p-2">Title</th>
              <th className="text-left p-2 w-28">Enabled</th>
              <th className="text-right p-2 w-40">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr key={row.id} className="border-t">
                <td className="p-2">{row.sort ?? (idx + 1)}</td>
                <td className="p-2">
                  <InlineEditable
                    value={row.title}
                    onSave={(v) => saveTitle(row, v)}
                    disabled={busyId === row.id}
                  />
                </td>
                <td className="p-2">
                  <label className="inline-flex items-center gap-2">
                    <input type="checkbox" checked={!!row.enabled} onChange={() => toggle(row)} disabled={busyId === row.id} />
                    <span>{row.enabled ? "Enabled" : "Disabled"}</span>
                  </label>
                </td>
                <td className="p-2 text-right">
                  <button className="text-red-700 underline disabled:opacity-50" disabled={busyId === row.id} onClick={() => remove(row)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

function InlineEditable({ value, onSave, disabled }: { value: string; onSave: (v: string) => void; disabled?: boolean }) {
  const [v, setV] = useState(value);
  useEffect(() => setV(value), [value]);
  const changed = useMemo(() => v.trim() !== value.trim(), [v, value]);
  return (
    <div className="flex items-center gap-2">
      <input className="border rounded p-1 w-full" value={v} onChange={e => setV(e.target.value)} disabled={disabled} />
      <button className="px-2 py-1 rounded border disabled:opacity-50" disabled={!changed || disabled} onClick={() => onSave(v)}>
        Save
      </button>
    </div>
  );
}
