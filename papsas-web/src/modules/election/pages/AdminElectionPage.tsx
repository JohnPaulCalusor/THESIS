// adminElectionPage.tsx
import { useMemo, useState } from "react";
import { useElection } from "../hooks/useElection";
import { CandidacyTable } from "../components/CandidacyTable";
import { PositionsTab } from "../components/PositionsTab";

type TabKey = "candidates" | "positions";

export default function AdminElectionPage() {
  const { election, loading, error } = useElection();
  const [tab, setTab] = useState<TabKey>("candidates");

  const head = useMemo(() => {
    if (loading) return "Loading election…";
    if (!election) return "No active election";
    const t = typeof election.title === "string" ? election.title.trim() : "";
    return `Admin / Election${t ? ` – ${t}` : ""}`; // ← no “undefined”
  }, [loading, election]);

  return (
    <div className="admin-page">
      <header className="admin-header">
        <h1 className="admin-title">{head}</h1>
      </header>

      {error && <div className="admin-alert admin-alert-error">{error}</div>}

      {!loading && !election && (
        <div className="admin-alert admin-alert-warn">
          No active election. Please create/activate one in the backend.
        </div>
      )}

      {election && (
        <section className="admin-body">
          <nav className="admin-tabs">
            <button
              className={`admin-tab ${tab === "candidates" ? "admin-tab-active" : ""}`}
              onClick={() => setTab("candidates")}
            >
              Candidates
            </button>
            <button
              className={`admin-tab ${tab === "positions" ? "admin-tab-active" : ""}`}
              onClick={() => setTab("positions")}
            >
              Positions
            </button>
          </nav>

          <div className="admin-content">
            {tab === "candidates" && <CandidacyTable electionId={election.id} readOnly={false} />}
            {tab === "positions" && <PositionsTab electionId={election.id} />}
          </div>
        </section>
      )}
    </div>
  );
}
