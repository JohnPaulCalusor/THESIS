// src/modules/audit/components/AuditFilterBar.tsx
import "./AuditFilterBar.css";

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

export function AuditFilterBar({
  draft,
  onChange,
  onApply,
  onReset,
}: Props) {
  return (
    <div className="card audit-filters">
      <div className="audit-filters-header">
        <div>
          <h2 className="audit-filters-title">Filters</h2>
          <p className="audit-filters-subtitle">
            Narrow results by action type, status, election or time range.
          </p>
        </div>
      </div>

      <div className="audit-filters-grid audit-filters-grid--top">
        <label className="audit-field">
          <span className="audit-field-label">Action</span>
          <input
            type="text"
            placeholder="e.g., AUTH_LOGIN_SUCCESS"
            className="audit-input"
            value={draft.action}
            onChange={(e) =>
              onChange({ ...draft, action: e.target.value })
            }
          />
        </label>

        <label className="audit-field">
          <span className="audit-field-label">Status</span>
          <select
            className="audit-input"
            value={draft.status}
            onChange={(e) =>
              onChange({
                ...draft,
                status: e.target.value as AuditFilterDraft["status"],
              })
            }
          >
            <option value="">All</option>
            <option value="success">success</option>
            <option value="error">error</option>
          </select>
        </label>

        <label className="audit-field">
          <span className="audit-field-label">Election ID</span>
          <input
            type="number"
            min="1"
            placeholder="e.g., 42"
            className="audit-input"
            value={draft.election}
            onChange={(e) =>
              onChange({ ...draft, election: e.target.value })
            }
          />
        </label>
      </div>

      <div className="audit-filters-grid audit-filters-grid--bottom">
        <label className="audit-field">
          <span className="audit-field-label">Since</span>
          <input
            type="datetime-local"
            className="audit-input"
            value={draft.since}
            onChange={(e) =>
              onChange({ ...draft, since: e.target.value })
            }
          />
        </label>
        <label className="audit-field">
          <span className="audit-field-label">Until</span>
          <input
            type="datetime-local"
            className="audit-input"
            value={draft.until}
            onChange={(e) =>
              onChange({ ...draft, until: e.target.value })
            }
          />
        </label>
      </div>

      <div className="audit-filters-actions">
        <button
          className="audit-btn audit-btn--primary"
          type="button"
          onClick={onApply}
        >
          Apply
        </button>
        <button
          className="audit-btn audit-btn--ghost"
          type="button"
          onClick={onReset}
        >
          Reset
        </button>
      </div>
    </div>
  );
}
