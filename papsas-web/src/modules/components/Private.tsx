// src/modules/components/Private.tsx
import React, { useEffect } from "react";
import { Navigate, useLocation, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";

export default function Private({ children }: { children?: React.ReactNode }) {
  const { user, loading, setIntendedPath } = useAuth();
  const loc = useLocation();

  useEffect(() => {
    if (!loading && !user) {
      const from = loc.pathname + loc.search + loc.hash;
      setIntendedPath(from);
    }
  }, [loading, user, loc, setIntendedPath]);

  if (loading) {
    return (
      <div className="page grid place-items-center">
        <div className="animate-pulse subtle">Loading…</div>
      </div>
    );
  }
  if (!user) return <Navigate to="/login" state={{ from: loc.pathname }} replace />;

  // Works as wrapper OR as a route element
  return <>{children ?? <Outlet />}</>;
}
