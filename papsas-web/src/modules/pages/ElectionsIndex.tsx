import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Topbar from "../components/Topbar";
import { http } from "../lib/http";

type Election = { id: number; title?: string; startDate?: string; endDate?: string; electionStatus?: boolean };

export default function ElectionsIndex() {
  const [rows, setRows] = useState<Election[]>([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const res = await http.get("/api/elections/");
        const list: Election[] =
          Array.isArray(res.data?.results) ? res.data.results :
          Array.isArray(res.data) ? res.data : [];
        setRows(list);
      } catch {
        setErr("Failed to load elections.");
      }
    })();
  }, []);

  return (
    <div className="page">
      <Topbar />
      <div className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-semibold mb-4">Elections</h1>
        {err && <p className="subtle">{err}</p>}
        {!err && (
          <ul className="space-y-3">
            {rows.map(e => (
              <li key={e.id} className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">{e.title || `Election #${e.id}`}</div>
                    <div className="subtle text-sm">
                      {e.startDate} – {e.endDate} {e.electionStatus ? "(open)" : "(closed)"}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Link className="btn btn-primary" to={`/elections/${e.id}/ballot`}>Ballot</Link>
                    <Link className="btn btn-outline" to={`/elections/${e.id}/results`}>Results</Link>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
