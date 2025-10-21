import { type FormEvent, useEffect, useState } from "react";
import { useAuth } from "../auth/AuthProvider";
import { useNavigate } from "react-router-dom";
import Topbar from "../components/Topbar";

export default function LoginPage() {
  const { login, isAuthed, intendedPath, setIntendedPath } = useAuth();
  const [u, setU] = useState("");
  const [p, setP] = useState("");
  const [err, setErr] = useState("");
  const nav = useNavigate();

  useEffect(() => {
    if (isAuthed) {
      const to = intendedPath || "/";
      setIntendedPath(null);
      nav(to, { replace: true });
    }
  }, [isAuthed]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr("");
    try {
      await login(u, p);
    } catch {
      setErr("Invalid credentials.");
    }
  }

  return (
    <div className="page">
      <Topbar />
      <div className="max-w-md mx-auto px-4 py-10">
        <form className="card" onSubmit={onSubmit} aria-labelledby="login-title">
          <h1 id="login-title" className="text-xl font-semibold">Sign in</h1>
          <p className="subtle mb-3">Access your PAPSAS officer tools and ballot.</p>

          {err && <div role="alert" className="callout callout-warn">{err}</div>}

          <div className="field">
            <label htmlFor="username">Username</label>
            <input id="username" className="input" value={u} onChange={(e) => setU(e.target.value)} autoComplete="username" required />
          </div>

          <div className="field">
            <label htmlFor="password">Password</label>
            <input id="password" className="input" type="password" value={p} onChange={(e) => setP(e.target.value)} autoComplete="current-password" required />
          </div>

          <button type="submit" className="btn btn-primary w-full mt-2">Continue</button>
        </form>
      </div>
    </div>
  );
}
