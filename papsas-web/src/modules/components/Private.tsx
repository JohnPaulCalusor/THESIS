import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";

export default function Private() {
  const { isAuthed, loading } = useAuth();
  const loc = useLocation();
  if (loading) return null;
  if (!isAuthed) return <Navigate to="/login" state={{ from: loc.pathname }} replace />;
  return <Outlet />;
}
