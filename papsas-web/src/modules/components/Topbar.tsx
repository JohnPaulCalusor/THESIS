// src/modules/components/Topbar.tsx
import { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";
import { isAdminUser } from "../auth/roles";
import "./Topbar.css";

const desktopNavLinkClass = ({ isActive }: { isActive: boolean }) =>
  `topbar__nav-link${isActive ? " topbar__nav-link--active" : ""}`;

const mobileNavLinkClass = ({ isActive }: { isActive: boolean }) =>
  `mobile-drawer__link${isActive ? " mobile-drawer__link--active" : ""}`;

// Local typing for what we actually use from AuthProvider user
type AuthUser = {
  username?: string | null;
  email?: string | null;
  role?: string | null;
  groups?: string[];
  is_staff?: boolean;
  is_superuser?: boolean;
};

// Local helper: decide if this user is an officer
function isOfficerUser(u?: AuthUser | null): boolean {
  if (!u) return false;
  const role = String(u.role ?? "").toLowerCase();
  const groups = (u.groups ?? []).map((g) => String(g ?? "").toLowerCase());

  // Adjust "officer" here if your backend uses a different name,
  // e.g. "election_officer"
  return role === "officer" || groups.includes("officer");
}

export default function Topbar() {
  // Type-cast to any so we don't fight existing AuthProvider types
  const { user, logout } = useAuth() as { user: AuthUser | null; logout: () => void };
  const loc = useLocation();

  const isLoginRoute =
    loc.pathname === "/login" || loc.pathname.startsWith("/login/");
  const isAuthed = Boolean(user);

  const showAdmin = isAuthed && isAdminUser(user as any);
  const showOfficer = isAuthed && isOfficerUser(user);

  // Officers AND admins see RESULTS
  const showResults = isAuthed && (showAdmin || showOfficer);

  const showNav = isAuthed && !isLoginRoute;
  const showAuthedActions = isAuthed && !isLoginRoute;

  const uname = user?.username || user?.email || "user";
  const avatarLetter = (uname || "U").charAt(0).toUpperCase();

  const [open, setOpen] = useState(false);

  // Close mobile drawer on route change
  useEffect(() => {
    setOpen(false);
  }, [loc.pathname]);

  // Close mobile drawer on Escape
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <>
      <header className={`topbar ${isLoginRoute ? "topbar--login" : ""}`}>
        <div className="topbar__container">
          {/* Logo + Desktop Nav */}
          <div className="topbar__left">
            <NavLink
              to="/"
              className="topbar__logo-link"
              aria-label="PAPSAS Home"
            >
              <img
                src="/papsas.png"
                alt="PAPSAS Logo"
                className="topbar__logo"
              />
            </NavLink>

            {showNav && (
              <nav className="topbar__nav" aria-label="Main navigation">
                <NavLink to="/ballot" className={desktopNavLinkClass}>
                  BALLOT
                </NavLink>

                {showResults && (
                  <NavLink to="/results" className={desktopNavLinkClass}>
                    RESULTS
                  </NavLink>
                )}

                {showAdmin && (
                  <NavLink
                    to="/admin/election"
                    className={desktopNavLinkClass}
                  >
                    ADMIN
                  </NavLink>
                )}

                {showAdmin && (
                  <NavLink to="/admin/audit" className={desktopNavLinkClass}>
                    AUDIT LOG
                  </NavLink>
                )}
              </nav>
            )}
          </div>

          {/* User Actions */}
          {showAuthedActions && (
            <div className="topbar__right">
              {/* Desktop User */}
              <div className="topbar__user-desktop">
                <div className="topbar__avatar">{avatarLetter}</div>
                {/* display name beside avatar REMOVED on desktop */}
                <button onClick={logout} className="topbar__logout-btn">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
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

              {/* Mobile Menu Toggle */}
              <button
                onClick={() => setOpen(true)}
                className="topbar__menu-btn"
                aria-label="Open menu"
              >
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path
                    d="M4 6h16M4 12h16M4 18h16"
                    strokeLinecap="round"
                  />
                </svg>
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Mobile Menu Drawer */}
      {showNav && (
        <div className={`mobile-drawer ${open ? "open" : ""}`}>
          <div
            className="mobile-drawer__overlay"
            onClick={() => setOpen(false)}
          />
          <div className="mobile-drawer__panel">
            <div className="mobile-drawer__header">
              <div className="mobile-drawer__user">
                <div className="mobile-drawer__avatar">{avatarLetter}</div>
                <div className="mobile-drawer__greeting">
                  <div className="text-sm opacity-70">Signed in as</div>
                  <div className="font-semibold">@{uname}</div>
                </div>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="mobile-drawer__close"
              >
                <svg
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path
                    d="M6 18L18 6M6 6l12 12"
                    strokeLinecap="round"
                  />
                </svg>
              </button>
            </div>

            <nav className="mobile-drawer__nav">
              <NavLink
                to="/ballot"
                className={mobileNavLinkClass}
                onClick={() => setOpen(false)}
              >
                BALLOT
              </NavLink>

              {showResults && (
                <NavLink
                  to="/results"
                  className={mobileNavLinkClass}
                  onClick={() => setOpen(false)}
                >
                  RESULTS
                </NavLink>
              )}

              {showAdmin && (
                <NavLink
                  to="/admin/election"
                  className={mobileNavLinkClass}
                  onClick={() => setOpen(false)}
                >
                  ADMIN
                </NavLink>
              )}

              {showAdmin && (
                <NavLink
                  to="/admin/audit"
                  className={mobileNavLinkClass}
                  onClick={() => setOpen(false)}
                >
                  AUDIT LOG
                </NavLink>
              )}
            </nav>

            <div className="mobile-drawer__footer">
              <button
                onClick={() => {
                  setOpen(false);
                  logout();
                }}
                className="mobile-drawer__logout"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
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
          </div>
        </div>
      )}
    </>
  );
}
