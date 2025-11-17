export type AuditFilterDraft = {
  action: string;
  status: "" | "success" | "error";
  election: string;
  since: string;
  until: string;
};

type Props = {
  draft: AuditFilterDraft;
  onChange: (next: AuditFilterDraft) => void;
  onApply: () => void;
  onReset: () => void;
};

export function AuditFilterBar({ draft, onChange, onApply, onReset }: Props) {
  return (
    <div className="rounded border bg-white p-4 shadow-sm space-y-3">
      <h2 className="text-lg font-semibold">Filters</h2>
      <div className="grid gap-4 md:grid-cols-3">
        <label className="flex flex-col text-sm">
          <span className="font-medium mb-1">Action</span>
          <input
            type="text"
            placeholder="AUTH_LOGIN_SUCCESS"
            className="border rounded px-3 py-2"
            value={draft.action}
            onChange={(e) => onChange({ ...draft, action: e.target.value })}
          />
        </label>
        <label className="flex flex-col text-sm">
          <span className="font-medium mb-1">Status</span>
          <select
            className="border rounded px-3 py-2"
            value={draft.status}
            onChange={(e) => onChange({ ...draft, status: e.target.value as AuditFilterDraft["status"] })}
          >
            <option value="">All</option>
            <option value="success">success</option>
            <option value="error">error</option>
          </select>
        </label>
        <label className="flex flex-col text-sm">
          <span className="font-medium mb-1">Election ID</span>
          <input
            type="number"
            min="1"
            placeholder="123"
            className="border rounded px-3 py-2"
            value={draft.election}
            onChange={(e) => onChange({ ...draft, election: e.target.value })}
          />
        </label>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <label className="flex flex-col text-sm">
          <span className="font-medium mb-1">Since</span>
          <input
            type="datetime-local"
            className="border rounded px-3 py-2"
            value={draft.since}
            onChange={(e) => onChange({ ...draft, since: e.target.value })}
          />
        </label>
        <label className="flex flex-col text-sm">
          <span className="font-medium mb-1">Until</span>
          <input
            type="datetime-local"
            className="border rounded px-3 py-2"
            value={draft.until}
            onChange={(e) => onChange({ ...draft, until: e.target.value })}
          />
        </label>
      </div>
      <div className="flex flex-wrap gap-2">
        <button className="px-4 py-2 rounded bg-blue-600 text-white" type="button" onClick={onApply}>
          Apply
        </button>
        <button className="px-4 py-2 rounded border text-sm text-gray-600" type="button" onClick={onReset}>
          Reset
        </button>
      </div>
    </div>
  );
}
