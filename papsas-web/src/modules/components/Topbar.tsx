import { Link, NavLink, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";
import { useElection } from "../election/hooks/useElection";
import { isAdmin } from "../auth/roles";

export default function Topbar(){
  const { isAuthed, me, logout } = useAuth();
  const { election } = useElection();
  const loc = useLocation();

  const admin = isAdmin(me);
  const showAuthedActions = isAuthed && loc.pathname !== "/login";

  return (
    <header className="topbar">
      <div className="max-w-6xl w-full mx-auto px-4 flex items-center justify-between gap-6">
        {/* LEFT: brand + title, then nav, spaced by gap-10 */}
        <div className="flex items-center gap-10">
          <div className="flex items-baseline gap-2">
            <Link to="/" className="brand font-semibold">PAPSAS</Link>
            {election && <span className="text-gray-500">- {election.title}</span>}
          </div>

          <nav className="topbar__nav ml-8 flex items-center gap-8">
            <NavLink to={`/ballot`} className={({isActive}) => isActive ? "active" : ""}>Ballot</NavLink>
            <NavLink to={`/results`} className={({isActive}) => isActive ? "active" : ""}>Results</NavLink>
            {showAuthedActions && admin && (
              <NavLink to="/admin/election" className={({isActive}) => isActive || loc.pathname.startsWith("/admin") ? "active" : ""}>Admin</NavLink>
            )}
          </nav>
        </div>
        <div className="flex items-center gap-3">
          {showAuthedActions && (
            <>
              <span className="text-sm text-gray-600">@{me?.username || me?.email || "guest"}</span>
              <button
                onClick={logout}
                className="px-3 py-1 rounded bg-gray-900 text-white hover:opacity-90"
                title="Log out"
              >
                Logout
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
