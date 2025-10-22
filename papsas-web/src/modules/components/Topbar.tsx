import { NavLink, useParams } from "react-router-dom";

export default function Topbar(){
  const { id = "1" } = useParams();
  return (
    <header className="topbar">
      <div className="max-w-6xl w-full mx-auto px-4 flex items-center gap-6">
        <div className="brand">PAPSAS</div>
        <nav>
          <NavLink to={`/elections/${id}/ballot`} className={({isActive}) => isActive ? "active" : ""}>Ballot</NavLink>
          <NavLink to={`/elections/${id}/results`} className={({isActive}) => isActive ? "active" : ""}>Results</NavLink>
        </nav>
      </div>
    </header>
  );
}
