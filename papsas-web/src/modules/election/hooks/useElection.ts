import { useContext } from "react";
import { ElectionContext } from "../context/ElectionContext";

export function useElection() {
  const ctx = useContext(ElectionContext);
  if (!ctx) throw new Error("useElection must be used within <ElectionProvider>");
  return ctx;
}
