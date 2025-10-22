import React, { useEffect } from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./modules/auth/AuthProvider";
import LoginPage from "./modules/pages/LoginPage";
import BallotPage from "./modules/pages/BallotPage";
import OfficerResults from "./modules/pages/OfficerResults";
import ElectionsIndex from "./modules/pages/ElectionsIndex"; // <-- add

import type { ReactElement } from "react";

function Private({ children }: { children: ReactElement }) {
  const { isAuthed, setIntendedPath } = useAuth();
  const loc = useLocation();
  useEffect(() => {
    if (!isAuthed) setIntendedPath(loc.pathname + loc.search);
  }, [isAuthed, loc.pathname, loc.search, setIntendedPath]);
  if (!isAuthed) return <Navigate to="/login" replace />;
  return children;
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Private><ElectionsIndex /></Private>} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/elections/:id/ballot" element={<Private><BallotPage /></Private>} />
          <Route path="/elections/:id/results" element={<Private><OfficerResults /></Private>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>
);
