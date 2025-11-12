import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";
import { isAdmin } from "../auth/roles";

export default function RequireAdmin() {
  const { isAuthed, me, loading } = useAuth();
  if (loading) return null;
  if (!isAuthed) return <Navigate to="/login" replace />;

  if (!isAdmin(me)) return <div className="p-6 text-red-600">403 — Not authorized.</div>;
  return <Outlet />;
}
