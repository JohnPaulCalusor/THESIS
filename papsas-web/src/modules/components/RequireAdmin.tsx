import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";

export default function RequireAdmin() {
  const { isAuthed, user, loading } = useAuth();
  if (loading) return null;
  if (!isAuthed) return <Navigate to="/login" replace />;

  const groups: string[] = Array.isArray(user?.groups) ? (user!.groups as string[]) : [];
  const isAdmin = Boolean(user?.is_staff || groups.includes("admin") || user?.role === "admin");
  if (!isAdmin) return <div className="p-6 text-red-600">403 — Not authorized.</div>;
  return <Outlet />;
}
