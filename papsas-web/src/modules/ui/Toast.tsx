import React, { createContext, useContext, useCallback, useEffect, useMemo, useRef, useState } from "react";

type ToastKind = "success" | "error" | "info";
type ToastItem = { id: string; kind: ToastKind; title?: string; message?: string; ttlMs?: number };

type ToastAPI = {
  success: (m: string, title?: string) => void;
  error: (m: string, title?: string) => void;
  info: (m: string, title?: string) => void;
  // >>> PAPSAS v1.3 BEGIN
  apiError?: (err: any, fallback?: string) => void;
  // <<< PAPSAS v1.3 END
};

const ToastContext = createContext<ToastAPI | null>(null);
export const useToast = () => {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within <ToastProvider/>");
  return ctx;
};

const MAX_VISIBLE = 3;
const DEFAULT_TTL = 3500;

export const ToastProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [visible, setVisible] = useState<ToastItem[]>([]);
  const [queue, setQueue] = useState<ToastItem[]>([]);
  const timers = useRef<Map<string, number>>(new Map());

  const dequeueIfPossible = useCallback(() => {
    setVisible((v) => {
      if (v.length >= MAX_VISIBLE) return v;
      let next: ToastItem | undefined;
      setQueue((q) => {
        if (q.length === 0) return q;
        next = q[0];
        return q.slice(1);
      });
      return next ? [...v, next] : v;
    });
  }, []);

  const add = useCallback((kind: ToastKind, message: string, title?: string, ttlMs?: number) => {
    const id = typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : String(Math.random());
    const t: ToastItem = { id, kind, message, title, ttlMs: ttlMs ?? DEFAULT_TTL };
    setQueue((q) => [...q, t]);
  }, []);

  useEffect(() => { if (visible.length < MAX_VISIBLE) dequeueIfPossible(); }, [queue, visible.length, dequeueIfPossible]);

  useEffect(() => {
    visible.forEach((t) => {
      if (timers.current.has(t.id)) return;
      const h = window.setTimeout(() => {
        setVisible((v) => v.filter((x) => x.id !== t.id));
        timers.current.delete(t.id);
      }, t.ttlMs ?? DEFAULT_TTL);
      timers.current.set(t.id, h as unknown as number);
    });
    return () => { timers.current.forEach((h) => window.clearTimeout(h)); };
  }, [visible]);

  useEffect(() => { if (visible.length < MAX_VISIBLE) dequeueIfPossible(); }, [visible.length, dequeueIfPossible]);

  const api = useMemo<ToastAPI>(() => ({
    success: (m, title) => add("success", m, title),
    error:   (m, title) => add("error", m, title),
    info:    (m, title) => add("info", m, title),
    // >>> PAPSAS v1.3 BEGIN
    apiError: (err: any, fallback?: string) => {
      const status = err?.response?.status;
      const code = err?.response?.data?.code;
      const message = err?.response?.data?.message || err?.message || fallback || "Request failed";
      if (status === 403) return add("error", "Admins only", "403");
      if (status === 409) return add("error", code === "ALREADY_VOTED" ? "Already voted" : "Already exists", "409");
      add("error", message);
    },
    // <<< PAPSAS v1.3 END
  }), [add]);

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div className="fixed bottom-4 right-4 z-[9999] flex flex-col gap-2 w-[min(92vw,360px)]">
        {visible.map((t) => (
          <div
            key={t.id}
            className={[
              "rounded-2xl shadow-lg p-3 border text-sm",
              t.kind === "success" ? "bg-emerald-600/90 text-white border-emerald-700"
              : t.kind === "error"   ? "bg-rose-600/90 text-white border-rose-700"
              :                        "bg-slate-800/90 text-white border-slate-700"
            ].join(" ")}
            role="status" aria-live="polite"
          >
            {t.title && <div className="font-semibold mb-0.5">{t.title}</div>}
            <div>{t.message}</div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};
