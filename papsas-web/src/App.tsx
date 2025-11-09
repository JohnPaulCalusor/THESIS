import { useEffect, useState } from "react";
import http from "./modules/lib/http";

type Election = { id: number; title?: string };

export default function App() {
  const [elections, setElections] = useState<Election[]>([]);

  useEffect(() => {
    http.get("elections")
      .then(({ data }) => setElections(data))
      .catch(console.error);
  }, []);

  return (
    <div style={{ padding: 16 }}>
      <h1>PAPSAS</h1>
      <ul>
        {elections.map(e => <li key={e.id}>{e.title ?? `Election #${e.id}`}</li>)}
      </ul>
    </div>
  );
}
