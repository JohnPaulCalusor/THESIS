// src/modules/pages/LoginPage.tsx
import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";
import "./LoginPage.css";

export default function LoginPage() {
  const { user, login, intendedPath, setIntendedPath } = useAuth();
  const nav = useNavigate();
  const loc = useLocation();

  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // If we landed here from a protected route, remember it once
  useEffect(() => {
    if (
      !intendedPath &&
      loc.state &&
      typeof loc.state === "object" &&
      loc.state !== null &&
      "from" in loc.state
    ) {
      const from = (loc.state as { from?: string }).from;
      if (typeof from === "string") {
        setIntendedPath(from);
      }
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

  const onUser = (e: React.ChangeEvent<HTMLInputElement>) =>
    setUsername(e.target.value);

  const onPass = (e: React.ChangeEvent<HTMLInputElement>) =>
    setPassword(e.target.value);

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(username, password);
      // nav will also run from the effect when user is set
    } catch (err: unknown) {
      const info = err as {
        response?: { data?: { message?: string } };
        message?: string;
      };
      setError(
        info.response?.data?.message || info.message || "Login failed"
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-page__container">
        <div className="login-card card">
          <header className="login-card__header">
            {/* Centered logo */}
            <img
              src="/papsas.png" // change this path if your logo file is different
              alt="PAPSAS Inc."
              className="login-card__logo"
            />
            <h1 className="login-card__title">Sign in to Vote</h1>
          </header>

          <form onSubmit={onSubmit} className="login-form">
            <div className="login-field">
              <label className="login-label" htmlFor="login-username">
                Username
              </label>
              <input
                id="login-username"
                className="login-input"
                value={username}
                onChange={onUser}
                autoComplete="username"
                placeholder="Enter your username"
              />
            </div>

            <div className="login-field">
              <label className="login-label" htmlFor="login-password">
                Password
              </label>
              <div className="login-password-wrap">
                <input
                  id="login-password"
                  type={showPassword ? "text" : "password"}
                  className="login-input login-input--password"
                  value={password}
                  onChange={onPass}
                  autoComplete="current-password"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  className="login-password-toggle"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    // Eye with slash (hide)
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      className="login-password-icon"
                      aria-hidden="true"
                    >
                      <path
                        d="M2 12s4-7 10-7c1.52 0 2.9.34 4.14.9"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                      <path
                        d="M22 12s-4 7-10 7c-2.03 0-3.84-.6-5.45-1.53"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                      <path
                        d="M9.88 9.88A3 3 0 0 1 14.12 14.12"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                      <line
                        x1="3"
                        y1="3"
                        x2="21"
                        y2="21"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                      />
                    </svg>
                  ) : (
                    // Simple eye (show)
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      className="login-password-icon"
                      aria-hidden="true"
                    >
                      <path
                        d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                      <circle
                        cx="12"
                        cy="12"
                        r="3"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                      />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {error && <div className="login-error">{error}</div>}

            <button
              type="submit"
              disabled={submitting}
              className="btn btn-primary login-submit"
            >
              {submitting ? "Signing in…" : "Continue"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
