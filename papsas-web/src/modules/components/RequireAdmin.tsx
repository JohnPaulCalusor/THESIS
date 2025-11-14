import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";
import { isAdminUser } from "../auth/roles";

export default function RequireAdmin({ children }: { children?: React.ReactNode }) {
  const { user, loading, setIntendedPath } = useAuth();
  const loc = useLocation();

  if (loading) return null; // keep splash minimal; parent can show a spinner

  if (!user || !isAdminUser(user)) {
    setIntendedPath(loc.pathname + loc.search + loc.hash);
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
