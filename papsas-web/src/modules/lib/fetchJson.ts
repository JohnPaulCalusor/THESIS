// src/modules/lib/fetchJson.ts
import type { AxiosRequestConfig } from "axios";
import http from "./http";

// Strip leading "/" and optional leading "api/"
function clean(path: string) {
  return path.replace(/^\/+/, "").replace(/^api\//i, "");
}

export async function fetchJson<T = unknown>(path: string, config?: AxiosRequestConfig): Promise<T> {
  const url = clean(path);
  const { data } = await http.get<T>(url, config);
  return data;
}
