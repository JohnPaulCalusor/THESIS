// src/modules/pages/LoginPage.tsx
import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";
import { Eye, EyeOff, Loader2, LogIn } from "lucide-react";
import { useToast } from "../ui/Toast";

export default function LoginPage() {
  const { user, login, intendedPath, setIntendedPath } = useAuth();
  const nav = useNavigate();
  const loc = useLocation();
  const toast = useToast();

  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPass, setShowPass] = useState(false);

  useEffect(() => {
    type LocationState = { from?: string };
    const state = loc.state as LocationState | null;
    if (!intendedPath && state?.from) {
      setIntendedPath(state.from);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
    } catch (err) {
      const info = err as { response?: { data?: { message?: string } }; message?: string };
      const message = info?.response?.data?.message || info?.message || "Login failed";
      toast.error(message);
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-head">
          <div className="login-icon-badge" aria-hidden>
            <LogIn size={18} />
          </div>
          <h1 className="login-title">Sign in to Election Portal</h1>
        </div>

        <form onSubmit={onSubmit} className="login-form" noValidate>
          {/* Username */}
          <label className="login-label" htmlFor="username">Username</label>
          <div className="login-input-group">
            <input
              id="username"
              className="login-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              placeholder="Enter your username"
            />
          </div>

          {/* Password */}
          <label className="login-label" htmlFor="password">Password</label>
          <div className="login-input-group">
            <input
              id="password"
              type={showPass ? "text" : "password"}
              className="login-input login-input--with-toggle"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              placeholder="Enter your password"
            />
            <button
              type="button"
              className="login-input-toggle"
              aria-label={showPass ? "Hide password" : "Show password"}
              onClick={() => setShowPass((v) => !v)}
            >
              {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          {error && <div role="alert" className="login-error">{error}</div>}

          <button type="submit" disabled={submitting} className="btn btn-primary login-submit">
            {submitting ? (
              <>
                <Loader2 className="animate-spin" size={16} /> Signing in…
              </>
            ) : (
              "Continue"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
