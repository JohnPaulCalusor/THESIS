import axios, { type AxiosError, type AxiosRequestHeaders } from "axios";

/* ---------------- baseURL ---------------- */
// Dev: use Vite proxy via /proxy_api
// Prod: usually /api or a full absolute URL from VITE_API_BASE
const defaultDevBase = "/proxy_api/";
const defaultProdBase = "/api/";

function normalizeBase(value?: string) {
  if (!value) return "/";
  const absoluteMatch = /^https?:\/\//i.test(value);
  const trimmed = value.replace(/\/+$/, ""); // drop trailing slashes
  if (absoluteMatch) return trimmed;        // keep absolute URLs as-is

  // normalize relative paths to a single leading slash, optional trailing slash
  const withoutSlashes = trimmed.replace(/^\/+/, "");
  return withoutSlashes ? `/${withoutSlashes}/` : "/";
}

const envBase = (import.meta.env.VITE_API_BASE as string | undefined) || "";
const baseCandidate = envBase || (import.meta.env.DEV ? defaultDevBase : defaultProdBase);
const baseURL = normalizeBase(baseCandidate);

// Axios instances that everything else uses
export const http = axios.create({ baseURL, withCredentials: false });
export const raw  = axios.create({ baseURL });

/* ---------------- tokens ---------------- */
const LS_KEY = "papsas.auth";
type Tokens = { access?: string; refresh?: string };

let accessToken = "";
let refreshToken = "";

export function getTokens(): Tokens {
  try {
    const rawVal = localStorage.getItem(LS_KEY);
    if (!rawVal) return {};
    const { access, refresh } = JSON.parse(rawVal) || {};
    return { access, refresh };
  } catch (err: unknown) {
    const ax = err as AxiosError<unknown>;
    const status = ax.response?.status;
    void status;
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
  if (/^https?:\/\//i.test(u)) return u;  // absolute → leave as-is
  return u.replace(/^\/+/, "");           // strip leading slashes only
}

/* ---------------- interceptors ---------------- */
for (const c of [http, raw]) {
  c.interceptors.request.use((cfg) => {
    if (cfg.url) cfg.url = normalize(cfg.url);
    if (accessToken) {
      const headers = { ...(cfg.headers ?? {}) } as AxiosRequestHeaders;
      headers.Authorization = `Bearer ${accessToken}`;
      cfg.headers = headers;
    }
    return cfg;
  });
}

export default http;
