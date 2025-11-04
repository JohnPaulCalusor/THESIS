// src/modules/lib/http.ts
import axios, {
  AxiosHeaders,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from "axios";

/**
 * Base URL rules:
 * - DEV: use "" (relative). Your calls like "/api/..." will hit Vite,
 *        and Vite's proxy will forward to https://api.papsasinc.com.
 * - PROD: use VITE_API_BASE (e.g., "https://api.papsasinc.com").
 *   Your calls like "/api/..." will become "https://api.papsasinc.com/api/..."
 */
const baseURL = (import.meta.env.VITE_API_BASE as string) || "";

export const http = axios.create({ baseURL, withCredentials: false });

/* ---------------- Token storage ---------------- */
const LS_KEY = "papsas.auth";
let accessToken = "";
let refreshToken = "";

export function initTokensFromStorage() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (!raw) return;
    const { access, refresh } = JSON.parse(raw) || {};
    accessToken = access || "";
    refreshToken = refresh || "";
  } catch { /* ignore */ }
}
export function setTokens(access: string, refresh: string) {
  accessToken = access || "";
  refreshToken = refresh || "";
  localStorage.setItem(LS_KEY, JSON.stringify({ access: accessToken, refresh: refreshToken }));
}
export function clearTokens() {
  accessToken = "";
  refreshToken = "";
  localStorage.removeItem(LS_KEY);
}
export function hasAccess() { return !!accessToken; }
initTokensFromStorage();

/* ---------------- Helpers ---------------- */
function ensureHeaders(cfg: AxiosRequestConfig): AxiosHeaders {
  if (!cfg.headers) cfg.headers = new AxiosHeaders();
  if (!(cfg.headers as any).set) cfg.headers = new AxiosHeaders(cfg.headers as any);
  return cfg.headers as AxiosHeaders;
}

/* ---------------- REQUEST: add Bearer ---------------- */
http.interceptors.request.use((cfg: InternalAxiosRequestConfig) => {
  if (accessToken) {
    const h = ensureHeaders(cfg);
    h.set("Authorization", `Bearer ${accessToken}`);
  }
  return cfg;
});

/* ---------------- RESPONSE: one-time refresh on 401 ---------------- */
let isRefreshing = false;
let waiters: Array<(token: string | null) => void> = [];

// plain axios (no interceptors) to perform refresh
const raw = axios.create({ baseURL });

async function doRefresh(): Promise<string> {
  if (!refreshToken) throw new Error("No refresh token");
  const { data } = await raw.post("/api/auth/refresh/", { refresh: refreshToken });
  const next = data?.access as string;
  if (!next) throw new Error("Refresh returned no access token");
  setTokens(next, refreshToken);
  return next;
}

http.interceptors.response.use(
  (r) => r,
  async (error) => {
    const { response, config } = error || {};
    if (!response || response.status !== 401 || (config as any)?._retried) {
      return Promise.reject(error);
    }
    if (!refreshToken) {
      clearTokens();
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        waiters.push((token) => {
          if (!token) return reject(error);
          const h = ensureHeaders(config);
          h.set("Authorization", `Bearer ${token}`);
          (config as any)._retried = true;
          resolve(http(config));
        });
      });
    }

    isRefreshing = true;
    try {
      const newAccess = await doRefresh();
      waiters.forEach((fn) => fn(newAccess));
      waiters = [];
      const h = ensureHeaders(config);
      h.set("Authorization", `Bearer ${newAccess}`);
      (config as any)._retried = true;
      return http(config);
    } catch (e) {
      clearTokens();
      waiters.forEach((fn) => fn(null));
      waiters = [];
      return Promise.reject(e);
    } finally {
      isRefreshing = false;
    }
  }
);
