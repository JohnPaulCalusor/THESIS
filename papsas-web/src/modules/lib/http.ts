// src/modules/lib/http.ts
import axios, { AxiosHeaders, type AxiosRequestConfig } from "axios";

const baseURL = import.meta.env.VITE_API_BASE as string;
export const http = axios.create({ baseURL, withCredentials: false });

// ---- token storage (persist between refreshes) ----
const LS_KEY = "papsas.auth";
let accessToken = "";
let refreshToken = "";
let refreshing = false;
let refreshPromise: Promise<string> | null = null;

export function initTokensFromStorage() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (!raw) return;
    const { access, refresh } = JSON.parse(raw) || {};
    if (access) accessToken = access;
    if (refresh) refreshToken = refresh;
  } catch {}
}

export function setTokens(access: string, refresh: string) {
  accessToken = access;
  refreshToken = refresh;
  localStorage.setItem(LS_KEY, JSON.stringify({ access, refresh }));
}

export function clearTokens() {
  accessToken = "";
  refreshToken = "";
  localStorage.removeItem(LS_KEY);
}

export function hasAccess() {
  return !!accessToken;
}

// ✅ Load tokens once when this module is imported
initTokensFromStorage();

// Ensure headers is an AxiosHeaders instance (v1 requires this for type-safety)
function ensureHeaders(cfg: AxiosRequestConfig): AxiosHeaders {
  if (!cfg.headers) {
    cfg.headers = new AxiosHeaders();
  } else if (!(cfg.headers as any).set) {
    cfg.headers = new AxiosHeaders(cfg.headers as any);
  }
  return cfg.headers as AxiosHeaders;
}

// ---- axios hooks ----
http.interceptors.request.use((cfg) => {
  if (accessToken) {
    const h = ensureHeaders(cfg);
    h.set("Authorization", `Bearer ${accessToken}`);
  }
  return cfg;
});

http.interceptors.response.use(
  (r) => r,
  async (err) => {
    const { response, config } = err || {};
    if (response?.status === 401 && refreshToken && !(config as any)._retry) {
      if (!refreshing) {
        refreshing = true;
        refreshPromise = http
          .post("/api/auth/refresh/", { refresh: refreshToken })
          .then((res) => {
            const newAccess = res.data?.access as string;
            if (!newAccess) throw new Error("No access token from refresh");
            accessToken = newAccess;
            localStorage.setItem(LS_KEY, JSON.stringify({ access: accessToken, refresh: refreshToken }));
            return newAccess;
          })
          .finally(() => {
            refreshing = false;
          });
      }
      const newAccess = await refreshPromise!;
      (config as any)._retry = true;
      const h = ensureHeaders(config);
      h.set("Authorization", `Bearer ${newAccess}`);
      return http(config);
    }
    return Promise.reject(err);
  }
);
