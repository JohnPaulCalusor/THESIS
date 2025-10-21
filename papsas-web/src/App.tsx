import { useEffect, useState } from "react";

export default function App() {
  const [msg, setMsg] = useState("Checking API…");
  useEffect(() => {
    const base = import.meta.env.VITE_API_BASE as string;
    fetch(`${base}/api/elections/`)      // ← expect 200/401/403, but NOT network error
      .then(r => setMsg(`API reachable, status ${r.status}`))
      .catch(e => setMsg(`Network error: ${e}`));
  }, []);
  return (
    <div style={{ padding: 24 }}>
      <h1>PAPSAS Web (Vite)</h1>
      <p>{msg}</p>
    </div>
  );
}
