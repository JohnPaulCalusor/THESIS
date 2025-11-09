import { useEffect, useState } from "react";
import { http } from "./modules/lib/http";

type Election = { id: number; title?: string };

export default function App() {
  const [elections, setElections] = useState<Election[]>([]);

  useEffect(() => {
    (async () => {
      try {
        const { data } = await http.get<Election[]>("elections");
        setElections(data);
      } catch (err) {
        console.error(err);
      }
    })();
  }, []);

  return (
    <div style={{ padding: 16 }}>
      <h1>PAPSAS</h1>
      <ul>
        {elections.map(e => (
          <li key={e.id}>{e.title ?? `Election #${e.id}`}</li>
        ))}
      </ul>
    </div>
  );
}
