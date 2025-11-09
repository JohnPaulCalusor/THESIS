import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";
import { isAdminUser } from "../auth/roles";

export default function RequireAdmin({ children }: { children?: React.ReactNode }) {
  const { user, loading, setIntendedPath } = useAuth();
  const loc = useLocation();
  if (loading) return <div className="page grid place-items-center"><div className="animate-pulse subtle">Loading…</div></div>;
  if (!user || !isAdminUser(user)) {
    setIntendedPath(loc.pathname + loc.search + loc.hash);
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}
