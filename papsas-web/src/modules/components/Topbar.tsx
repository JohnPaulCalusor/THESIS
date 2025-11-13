// Topbar.tsx
import React from "react";
import { NavLink, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";
import { isAdminUser } from "../auth/roles";
import logo from "../../assets/logo.png";

export default function Topbar() {
  const { user, logout } = useAuth();
  const loc = useLocation();

  const isLoginRoute = loc.pathname === "/login" || loc.pathname.startsWith("/login/");
  const isAuthed = Boolean(user);

  const showAdmin = isAuthed && isAdminUser(user);
  const showNav = isAuthed && !isLoginRoute;
  const showAuthedActions = isAuthed && !isLoginRoute;

  const uname = user?.username || user?.email || "user";
  const avatarLetter = (uname || "U").charAt(0).toUpperCase();

  const [open, setOpen] = React.useState(false);
  React.useEffect(() => { setOpen(false); }, [loc.pathname]);           // close on route change
  React.useEffect(() => {
    function onKey(e: KeyboardEvent){ if(e.key === "Escape") setOpen(false); }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <>
      <header className={`topbar ${isLoginRoute ? "topbar--login" : ""}`}>
        <div className="max-w-6xl w-full mx-auto px-4 flex items-center justify-between gap-6">
          {/* LEFT — LOGO + DESKTOP NAV */}
          <div className="flex items-center gap-10">
            <NavLink to="/" className="flex items-center" aria-label="Home">
              <img src={logo} alt="PAPSAS Logo" className="topbar__logo" />
            </NavLink>

            {showNav && (
              <nav className="topbar__nav">
                <NavLink to="/ballot"  className={({isActive}) => (isActive ? "active" : "")}>Ballot</NavLink>
                <NavLink to="/results" className={({isActive}) => (isActive ? "active" : "")}>Results</NavLink>
                {showAdmin && (
                  <NavLink
                    to="/admin/election"
                    className={({isActive}) => (isActive || loc.pathname.startsWith("/admin")) ? "active" : ""}
                  >
                    Admin
                  </NavLink>
                )}
              </nav>
            )}
          </div>

          {/* RIGHT — DESKTOP USER + LOGOUT */}
          {showAuthedActions && (
            <>
              <div className="topbar__user">
                <div className="topbar__avatar">{avatarLetter}</div>
                <span className="font-medium">@{uname}</span>
                <button onClick={logout} className="topbar__logout" title="Log out">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round"
                          d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                  </svg>
                  Logout
                </button>
              </div>

              {/* MOBILE HAMBURGER (shown only on phones via CSS) */}
              <button
                className="topbar__hamburger"
                aria-label="Open menu"
                aria-controls="mobile-menu"
                aria-expanded={open}
                onClick={() => setOpen(true)}
              >
                {/* hamburger icon */}
                <svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true">
                  <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </button>
            </>
          )}
        </div>
      </header>

      {/* MOBILE MENU */}
      {showNav && (
        <div className={`mobile-menu-root ${open ? "open" : ""}`}>
          <div className="mobile-menu-overlay" onClick={() => setOpen(false)} />
          <nav id="mobile-menu" className="mobile-menu" aria-label="Mobile menu" role="dialog" aria-modal="true">
            <div className="mobile-menu-head">
              <button className="mobile-menu-close" aria-label="Close menu" onClick={() => setOpen(false)}>
                <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
                  <path d="M6 6l12 12M18 6l-12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </button>
            </div>

            <ul className="mobile-menu-nav">
              <li><NavLink to="/ballot"  className={({isActive}) => (isActive ? "active" : "")}  onClick={() => setOpen(false)}>Ballot</NavLink></li>
              <li><NavLink to="/results" className={({isActive}) => (isActive ? "active" : "")}  onClick={() => setOpen(false)}>Results</NavLink></li>
              {showAdmin && (
                <li><NavLink to="/admin/election" className={({isActive}) => (isActive || loc.pathname.startsWith("/admin")) ? "active" : ""} onClick={() => setOpen(false)}>Admin</NavLink></li>
              )}
            </ul>

            <div className="mobile-menu-footer">
              <div className="mobile-user">
                <div className="mobile-avatar">{avatarLetter}</div>
                <div className="mobile-username">@{uname}</div>
              </div>
              <button className="mobile-logout" onClick={logout}>Logout</button>
            </div>
          </nav>
        </div>
      )}
    </>
  );
}
