// src/modules/election/pages/AdminElectionPage.tsx
import React, { useState } from "react";
import { useElection } from "../hooks/useElection";
import { CandidacyTable } from "../components/CandidacyTable";
import { PositionsTab } from "../components/PositionsTab";

import "./AdminElectionPage.css";

type TabKey = "candidates" | "positions";

const TabButton: React.FC<{
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}> = ({ active, onClick, children }) => (
  <button
    onClick={onClick}
    className={`admin-election-tab ${
      active ? "admin-election-tab--active" : ""
    }`}
  >
    {children}
  </button>
);

export default function AdminElectionPage() {
  const { election, loading, error } = useElection();
  const [tab, setTab] = useState<TabKey>("candidates");

  // Only show a subtitle when it actually has content
  const subtitle =
    loading
      ? "Loading election details…"
      : election && election.title
      ? `Active election: ${election.title}`
      : "";

  return (
    <div className="admin-election-page">
      <div className="admin-election-container">
        {/* Header */}
        <header className="admin-election-header">
          <div>
            <h1 className="admin-election-title">Admin Page</h1>
            {subtitle && (
              <p className="admin-election-subtitle">{subtitle}</p>
            )}
          </div>
        </header>

        {error && (
          <div className="admin-election-error">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* When there is no active election */}
        {!loading && !election && (
          <div className="card admin-election-empty">
            <h2>No active election</h2>
            <p>
              There is currently no active election. Set one up in the backend
              to manage candidates and positions here.
            </p>
          </div>
        )}

        {/* Main card when election exists */}
        {election && (
          <div className="card admin-election-card">
            {/* Tabs */}
            <div className="admin-election-tabs">
              <TabButton
                active={tab === "candidates"}
                onClick={() => setTab("candidates")}
              >
                Candidates
              </TabButton>
              <TabButton
                active={tab === "positions"}
                onClick={() => setTab("positions")}
              >
                Positions
              </TabButton>
            </div>

            <div className="admin-election-body">
              {tab === "candidates" && (
                <CandidacyTable electionId={election.id} readOnly={false} />
              )}
              {tab === "positions" && (
                <PositionsTab electionId={election.id} />
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
