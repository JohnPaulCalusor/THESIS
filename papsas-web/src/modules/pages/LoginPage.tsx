// src/modules/pages/LoginPage.tsx
import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";

export default function LoginPage() {
  const { user, login, intendedPath, setIntendedPath } = useAuth();
  const nav = useNavigate();
  const loc = useLocation();

  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // If we landed here from a protected route, remember it once
  useEffect(() => {
    if (!intendedPath && loc.state && (loc.state as any)?.from) {
      setIntendedPath((loc.state as any).from as string);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // If already logged in, go to intended or /ballot
  useEffect(() => {
    if (user) {
      const next = intendedPath || "/ballot";
      setIntendedPath(null);
      nav(next, { replace: true });
    }
  }, [user, intendedPath, setIntendedPath, nav]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(username, password);
      // nav will also run from the effect when user is set
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      <div className="rounded-xl border p-6 bg-[var(--card)]">
        <h1 className="text-3xl font-bold mb-2">Sign in</h1>
        <p className="text-sm text-[var(--muted)] mb-6">Access your PAPSAS officer tools and ballot.</p>
        <form onSubmit={onSubmit} className="space-y-3">
          <div>
            <label className="text-sm">Username</label>
            <input
              className="w-full rounded-md border px-3 py-2 bg-[var(--muted-bg)]"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
            />
          </div>
          <div>
            <label className="text-sm">Password</label>
            <input
              type="password"
              className="w-full rounded-md border px-3 py-2 bg-[var(--muted-bg)]"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </div>
          {error && <div className="text-sm text-red-600">{error}</div>}
          <button
            type="submit"
            disabled={submitting}
            className="btn btn-primary w-full"
          >
            {submitting ? "Signing in…" : "Continue"}
          </button>
        </form>
      </div>
    </div>
  );
}
