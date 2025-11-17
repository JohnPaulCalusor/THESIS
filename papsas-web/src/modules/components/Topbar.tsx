import { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";
import { isAdminUser } from "../auth/roles";

export default function Topbar() {
  const { user, logout } = useAuth();
  const loc = useLocation();

  const isLoginRoute =
    loc.pathname === "/login" || loc.pathname.startsWith("/login/");
  const isAuthed = Boolean(user);

  const showAdmin = isAuthed && isAdminUser(user);
  const showResults = showAdmin; // RESULTS nav link only for admin (matches existing logic)
  const showNav = isAuthed && !isLoginRoute;
  const showAuthedActions = isAuthed && !isLoginRoute;

  const uname = user?.username || user?.email || "user";
  const avatarLetter = (uname || "U").charAt(0).toUpperCase();

  const [open, setOpen] = useState(false);

  // Close mobile menu on route change
  useEffect(() => {
    setOpen(false);
  }, [loc.pathname]);

  // ESC closes mobile menu
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <>
      <header className={`topbar ${isLoginRoute ? "topbar--login" : ""}`}>
        <div className="max-w-6xl w-full mx-auto px-4 flex items-center justify-between gap-4">
          {/* LEFT — logo + desktop nav */}
          <div className="flex items-center gap-6">
            <NavLink to="/" className="flex items-center" aria-label="Home">
              <img src="/logo.svg" alt="PAPSAS Logo" className="topbar__logo" />
            </NavLink>

            {showNav && (
              <nav className="topbar__nav">
                <NavLink
                  to="/ballot"
                  className={({ isActive }) => (isActive ? "active" : "")}
                >
                  Ballot
                </NavLink>
                {showResults && (
                  <NavLink
                    to="/results"
                    className={({ isActive }) => (isActive ? "active" : "")}
                  >
                    Results
                  </NavLink>
                )}
                {showAdmin && (
                  <NavLink
                    to="/admin/election"
                    className={({ isActive }) =>
                      isActive || loc.pathname.startsWith("/admin")
                        ? "active"
                        : ""
                    }
                  >
                    Admin
                  </NavLink>
                )}
                {showAdmin && (
                  <NavLink
                    to="/admin/audit"
                    className={({ isActive }) => (isActive ? "active" : "")}
                  >
                    Audit Log
                  </NavLink>
                )}
              </nav>
            )}
          </div>

          {/* RIGHT — user + actions */}
          <div className="flex items-center gap-3">
            {showAuthedActions && (
              <>
                {/* Desktop user summary */}
                <div className="topbar__user hidden sm:flex items-center gap-2">
                  <div className="topbar__avatar">{avatarLetter}</div>
                  <span className="font-medium">@{uname}</span>
                  <button
                    type="button"
                    onClick={logout}
                    className="topbar__logout"
                    title="Log out"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                      />
                    </svg>
                    Logout
                  </button>
                </div>

                {/* Mobile menu toggle (nav + logout are inside the drawer) */}
                <button
                  type="button"
                  onClick={() => setOpen(true)}
                  className="inline-flex items-center justify-center rounded-md border border-[var(--ring)] bg-white px-2 py-1 text-sm sm:hidden"
                  aria-label="Open navigation menu"
                >
                  <svg
                    viewBox="0 0 24 24"
                    width="22"
                    height="22"
                    aria-hidden="true"
                  >
                    <path
                      d="M4 6h16M4 12h16M4 18h16"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                    />
                  </svg>
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* MOBILE MENU */}
      {showNav && (
        <div className={`mobile-menu-root ${open ? "open" : ""}`}>
          <div
            className="mobile-menu-overlay"
            onClick={() => setOpen(false)}
          />
          <nav
            id="mobile-menu"
            className="mobile-menu"
            aria-label="Mobile menu"
            role="dialog"
            aria-modal="true"
          >
            <div className="mobile-menu-head">
              <button
                className="mobile-menu-close"
                aria-label="Close menu"
                type="button"
                onClick={() => setOpen(false)}
              >
                <svg
                  viewBox="0 0 24 24"
                  width="22"
                  height="22"
                  aria-hidden="true"
                >
                  <path
                    d="M6 6l12 12M18 6l-12 12"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                </svg>
              </button>
            </div>

            <ul className="mobile-menu-nav">
              <li>
                <NavLink
                  to="/ballot"
                  className={({ isActive }) => (isActive ? "active" : "")}
                  onClick={() => setOpen(false)}
                >
                  Ballot
                </NavLink>
              </li>
              {showResults && (
                <li>
                  <NavLink
                    to="/results"
                    className={({ isActive }) =>
                      isActive ? "active" : ""
                    }
                    onClick={() => setOpen(false)}
                  >
                    Results
                  </NavLink>
                </li>
              )}
              {showAdmin && (
                <li>
                  <NavLink
                    to="/admin/election"
                    className={({ isActive }) =>
                      isActive || loc.pathname.startsWith("/admin")
                        ? "active"
                        : ""
                    }
                    onClick={() => setOpen(false)}
                  >
                    Admin
                  </NavLink>
                </li>
              )}
              {showAdmin && (
                <li>
                  <NavLink
                    to="/admin/audit"
                    className={({ isActive }) =>
                      isActive ? "active" : ""
                    }
                    onClick={() => setOpen(false)}
                  >
                    Audit Log
                  </NavLink>
                </li>
              )}
            </ul>

            <div className="mobile-menu-footer">
              <div className="mobile-user">
                <div className="mobile-avatar">{avatarLetter}</div>
                <div className="mobile-username">@{uname}</div>
              </div>
              <button
                type="button"
                className="mobile-logout"
                onClick={() => {
                  setOpen(false);
                  logout();
                }}
              >
                Logout
              </button>
            </div>
          </nav>
        </div>
      )}
    </>
  );
}
