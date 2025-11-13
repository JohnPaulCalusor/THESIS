import axios, { AxiosHeaders } from "axios";
import type { AxiosRequestHeaders } from "axios";

// PAPSAS HTTP audit (Codex): baseURL comes from VITE_API_BASE with "/proxy_api" fallback for dev; the Vite proxy rewrites /proxy_api → http://localhost:8000/api; no raw production URLs remain.
const baseURL = ((import.meta.env.VITE_API_BASE as string) || "/proxy_api").replace(/\/$/, "");
/*
 * Dev: unset VITE_API_BASE → baseURL="/proxy_api" and Vite proxies requests to http://localhost:8000/api
 * Prod: set VITE_API_BASE="/api" during build → baseURL="/api" so the browser hits the deployed API directly.
 */
export const http = axios.create({ baseURL, withCredentials: false });
export const raw  = axios.create({ baseURL });

/* ---------------- tokens ---------------- */
const LS_KEY = "papsas.auth";
type Tokens = { access?: string; refresh?: string };

let accessToken = "";
let refreshToken = "";

export function getTokens(): Tokens {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (!raw) return {};
    const { access, refresh } = JSON.parse(raw) || {};
    return { access, refresh };
  } catch {
    return {};
  }
}

export function setTokens(t: Tokens) {
  accessToken = t.access || "";
  refreshToken = t.refresh || "";
  localStorage.setItem(LS_KEY, JSON.stringify({ access: accessToken, refresh: refreshToken }));
}

export function clearTokens() {
  accessToken = "";
  refreshToken = "";
  localStorage.removeItem(LS_KEY);
}

/* load any existing tokens on boot */
(() => {
  const t = getTokens();
  accessToken = t.access || "";
  refreshToken = t.refresh || "";
})();

/* ---------------- url normalize ---------------- */
function normalize(u?: string) {
  if (!u) return u;
  if (/^https?:\/\//i.test(u)) return u;       // absolute → leave
  return u.replace(/^\/+/, "");                 // strip leading slashes only
}

/* ---------------- interceptors ---------------- */
for (const c of [http, raw]) {
  c.interceptors.request.use((cfg) => {
    if (cfg.url) cfg.url = normalize(cfg.url);
    if (accessToken) {
      const existing = cfg.headers as AxiosRequestHeaders | undefined;
      const merged = new AxiosHeaders(existing ?? {});
      merged.set("Authorization", `Bearer ${accessToken}`);
      cfg.headers = merged;
    }
    return cfg;
  });
}

export default http;
