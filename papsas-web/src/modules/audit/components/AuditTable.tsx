import type { AuditEvent } from "../hooks/useAuditEvents";

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
    <div className="rounded border bg-white shadow-sm">
      {isLoading && (
        <div className="p-4 text-sm text-gray-500">Loading audit events…</div>
      )}
      {error && (
        <div className="p-4 text-sm text-red-600">{error}</div>
      )}
      {!isLoading && !error && events.length === 0 && (
        <div className="p-4 text-sm text-gray-500">
          No events found for the current filters.
        </div>
      )}
      {events.length > 0 && (
        <div className="overflow-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50 text-xs uppercase tracking-wide text-gray-600">
              <tr>
                <th className="px-3 py-2 text-left">Timestamp</th>
                <th className="px-3 py-2 text-left">Action</th>
                <th className="px-3 py-2 text-left">Actor</th>
                <th className="px-3 py-2 text-left">Target</th>
                <th className="px-3 py-2 text-left">Election</th>
                <th className="px-3 py-2 text-left">IP</th>
                <th className="px-3 py-2 text-left">Method</th>
                <th className="px-3 py-2 text-left">Path</th>
                <th className="px-3 py-2 text-left">Status</th>
                <th className="px-3 py-2 text-left">Details</th>
              </tr>
            </thead>
            <tbody>
              {events.map((ev) => {
                const actor = ev.actor_username || (ev.ip ? "(anonymous)" : "(system)");
                const targetParts = [];
                if (ev.target_type) targetParts.push(ev.target_type);
                if (ev.target_id) targetParts.push(ev.target_id);
                const target = targetParts.join("/") || "—";
                const formattedTime = timestampFormatter.format(new Date(ev.ts));
                const statusClass =
                  ev.status === "success"
                    ? "bg-emerald-100 text-emerald-700"
                    : ev.status === "error"
                      ? "bg-rose-100 text-rose-700"
                      : "bg-gray-100 text-gray-700";
                const metaJson = JSON.stringify(ev.meta || {}, null, 2);
                return (
                  <tr key={ev.id} className="border-t even:bg-gray-50">
                    <td className="px-3 py-2 align-top">
                      <time title={ev.ts} className="font-mono text-xs">
                        {formattedTime}
                      </time>
                    </td>
                    <td className="px-3 py-2 align-top">
                      <div className="font-mono text-[13px] tracking-wide">{ev.action}</div>
                    </td>
                    <td className="px-3 py-2 align-top">{actor}</td>
                    <td className="px-3 py-2 align-top">{target}</td>
                    <td className="px-3 py-2 align-top">{ev.scope_election_id ?? "—"}</td>
                    <td className="px-3 py-2 align-top">{ev.ip || "—"}</td>
                    <td className="px-3 py-2 align-top">{ev.method}</td>
                    <td className="px-3 py-2 align-top break-all">{ev.path}</td>
                    <td className="px-3 py-2 align-top">
                      <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold ${statusClass}`}>
                        {ev.status}
                      </span>
                    </td>
                    <td className="px-3 py-2 align-top">
                      <details>
                        <summary className="cursor-pointer text-xs text-blue-700">View</summary>
                        <div className="mt-1 text-[11px] text-slate-600 space-y-1">
                          <div>User Agent:</div>
                          <div className="break-all text-[10px]">{ev.user_agent || "—"}</div>
                          <div>Payload Hash: {ev.payload_hash || "—"}</div>
                          <pre className="mt-1 max-h-48 overflow-auto rounded bg-slate-50 p-2 text-[10px]">
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
