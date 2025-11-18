// src/modules/audit/components/AuditTable.tsx
import type { AuditEvent } from "../hooks/useAuditEvents";
import "./AuditTable.css";

type Props = {
  events: AuditEvent[];
  isLoading: boolean;
  error: string | null;
};

const timestampFormatter = new Intl.DateTimeFormat("en-PH", {
  timeZone: "Asia/Manila",
  year: "numeric",
  month: "short",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
});

export function AuditTable({ events, isLoading, error }: Props) {
  return (
    <div className="card audit-table-card">
      {isLoading && (
        <div className="audit-table-message">
          Loading audit events…
        </div>
      )}
      {error && (
        <div className="audit-table-message audit-table-message--error">
          {error}
        </div>
      )}
      {!isLoading && !error && events.length === 0 && (
        <div className="audit-table-message">
          No events found for the current filters.
        </div>
      )}

      {events.length > 0 && (
        <div className="audit-table-wrapper">
          <table className="audit-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Action</th>
                <th>Actor</th>
                <th>Target</th>
                <th>Election</th>
                <th>IP</th>
                <th>Method</th>
                <th>Path</th>
                <th>Status</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {events.map((ev) => {
                const actor =
                  ev.actor_username ||
                  (ev.ip ? "(anonymous)" : "(system)");
                const targetParts: string[] = [];
                if (ev.target_type) targetParts.push(ev.target_type);
                if (ev.target_id) targetParts.push(String(ev.target_id));
                const target = targetParts.join("/") || "—";
                const formattedTime = timestampFormatter.format(
                  new Date(ev.ts)
                );

                let statusClass = "audit-status-pill";
                if (ev.status === "success") {
                  statusClass += " audit-status-pill--success";
                } else if (ev.status === "error") {
                  statusClass += " audit-status-pill--error";
                }

                const metaJson = JSON.stringify(ev.meta || {}, null, 2);

                return (
                  <tr key={ev.id}>
                    <td>
                      <time
                        title={ev.ts}
                        className="audit-table-timestamp"
                      >
                        {formattedTime}
                      </time>
                    </td>
                    <td>
                      <div className="audit-table-action">
                        {ev.action}
                      </div>
                    </td>
                    <td>{actor}</td>
                    <td>{target}</td>
                    <td>{ev.scope_election_id ?? "—"}</td>
                    <td>{ev.ip || "—"}</td>
                    <td>{ev.method}</td>
                    <td className="audit-table-path">{ev.path}</td>
                    <td>
                      <span className={statusClass}>{ev.status}</span>
                    </td>
                    <td>
                      <details className="audit-details">
                        <summary>View</summary>
                        <div className="audit-details-body">
                          <div className="audit-details-label">
                            User Agent:
                          </div>
                          <div className="audit-details-ua">
                            {ev.user_agent || "—"}
                          </div>
                          <div className="audit-details-label">
                            Payload Hash:
                          </div>
                          <div className="audit-details-hash">
                            {ev.payload_hash || "—"}
                          </div>
                          <pre className="audit-details-meta">
                            {metaJson}
                          </pre>
                        </div>
                      </details>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
