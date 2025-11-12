import React, { createContext, useContext, useEffect, useMemo, useRef, useState } from "react";

type ToastKind = "info" | "success" | "error";
type ToastItem = {
  id: string;
  kind: ToastKind;
  message: string;
  timeoutMs?: number;
};

type ToastCtx = {
  show: (message: string, kind?: ToastKind, timeoutMs?: number) => string;
  success: (message: string, timeoutMs?: number) => string;
  error: (message: string, timeoutMs?: number) => string;
  dismiss: (id: string) => void;
};

const Ctx = createContext<ToastCtx | null>(null);

export function useToast(): ToastCtx {
  const v = useContext(Ctx);
  if (!v) throw new Error("ToastProvider is missing");
  return v;
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);
  const timers = useRef<Record<string, number>>({});

  const dismiss = React.useCallback((id: string) => {
    setItems((xs) => xs.filter((x) => x.id !== id));
    const t = timers.current[id];
    if (t) {
      window.clearTimeout(t);
      delete timers.current[id];
    }
  }, []);

  const show = React.useCallback(
    (message: string, kind: ToastKind = "info", timeoutMs = 3000) => {
      const id = Math.random().toString(36).slice(2);
      const item: ToastItem = { id, kind, message, timeoutMs };
      setItems((xs) => [...xs, item]);

      if (timeoutMs > 0) {
        const tid = window.setTimeout(() => dismiss(id), timeoutMs);
        timers.current[id] = tid;
      }
      return id;
    },
    [dismiss]
  );

  const success = React.useCallback((message: string, timeoutMs?: number) => show(message, "success", timeoutMs), [show]);
  const error = React.useCallback((message: string, timeoutMs?: number) => show(message, "error", timeoutMs), [show]);

  useEffect(() => {
    const initialTimers = timers.current;
    return () => {
      Object.values(initialTimers).forEach((tid) => window.clearTimeout(tid));
    };
  }, []);

  const value = useMemo<ToastCtx>(() => ({ show, success, error, dismiss }), [show, success, error, dismiss]);

  return (
    <Ctx.Provider value={value}>
      {children}
      {/* very lightweight renderer */}
      <div className="toast-stack" style={{ position: "fixed", right: 16, bottom: 16, display: "grid", gap: 8, zIndex: 50 }}>
        {items.map((t) => (
          <div
            key={t.id}
            role="status"
            className="toast"
            style={{
              padding: "10px 12px",
              borderRadius: 8,
              background: t.kind === "error" ? "#fee2e2" : t.kind === "success" ? "#dcfce7" : "#eef2ff",
              color: "#111827",
              boxShadow: "0 4px 14px rgba(0,0,0,.08)",
              minWidth: 240,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
              <div style={{ fontSize: 14 }}>{t.message}</div>
              <button onClick={() => dismiss(t.id)} style={{ fontSize: 12, opacity: 0.8 }}>×</button>
            </div>
          </div>
        ))}
      </div>
    </Ctx.Provider>
  );
}
