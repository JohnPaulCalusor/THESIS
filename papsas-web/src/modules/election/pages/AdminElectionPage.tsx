import React, { useMemo, useState } from "react";
import { useElection } from "../hooks/useElection";
import { CandidacyTable } from "../components/CandidacyTable";
import { PositionsTab } from "../components/PositionsTab";

type TabKey = "candidates" | "positions";

const TabButton: React.FC<{ active: boolean; onClick: () => void; children: React.ReactNode }> = ({ active, onClick, children }) => (
  <button
    onClick={onClick}
    className={`px-4 py-2 border-b-2 ${active ? "border-blue-600 font-semibold" : "border-transparent text-gray-500"} hover:text-blue-700`}
  >
    {children}
  </button>
);

export default function AdminElectionPage() {
  const { election, loading, error } = useElection();
  const [tab, setTab] = useState<TabKey>("candidates");

  const head = useMemo(() => {
    if (loading) return "Loading election…";
    if (!election) return "No active election";
    return `Admin / Election – ${election.title}`;
  }, [loading, election]);

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-xl font-bold mb-2">{head}</h1>

      {error && <div className="text-red-600">Error: {error}</div>}

      {!loading && !election && (
        <div className="rounded border p-4 bg-red-50">No active election. Please create/activate one in the backend.</div>
      )}

      {election && (
        <>
          <div className="flex gap-4 border-b">
            <TabButton active={tab === "candidates"} onClick={() => setTab("candidates")}>Candidates</TabButton>
            <TabButton active={tab === "positions"} onClick={() => setTab("positions")}>Positions</TabButton>
          </div>

          <div className="pt-4">
            {tab === "candidates" && <CandidacyTable electionId={election.id} readOnly={false} />}
            {tab === "positions" && <PositionsTab electionId={election.id} />}
          </div>
        </>
      )}
    </div>
  );
}
