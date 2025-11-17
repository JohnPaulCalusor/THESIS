# AUDIT REPORT

## TL;DR
| Check | Status | Notes |
| --- | --- | --- |
| A1. Health & HTTPS behavior | ❌ | `/srv/papsas/app` is missing here, so the required `curl` requests to gunicorn/nginx cannot be executed. |
| A2. Email backend outbox | ❌ | Without the Django app tree the venv/`manage.py` inspection cannot run; need the server path to exist. |
| A3. OTP email flow | ❌ | `papsas-otp` and the `/auth/email/*` endpoints are unreachable from this workspace. |
| A4. Rate limiting | ❌ | Cannot send burst `/auth/email/start` calls or tail `/var/log/nginx/error.log` without the server. |
| B1. systemd unit | ❌ | `systemctl cat papsas.service` cannot be run because `/srv/papsas/app`/systemd are not present locally. |
| B2. Nginx OTP location | ❌ | `/etc/nginx` and `sudo nginx -t` are unavailable from this environment. |
| C1. Web base/proxy | ✅ | `http.ts` now defaults to `/proxy_api/` (dev) or `/api/` (prod) via `normalizeBase`, and `vite.config.ts` proxies `/proxy_api` to `https://api.papsasinc.com/api`. |
| C2. Topbar admin gating | ✅ | `showAdmin = isAuthed && isAdminUser(user)` with `showResults = showAdmin` in `Topbar.tsx`. |
| D1. Mobile start helper | ❌ | `papsas-mobile` repo is missing locally; helper cannot be inspected. |
| D2. EmailVerifyStartScreen | ❌ | Same as D1; screen code is not available. |
| D3. EventDetail navigation | ❌ | Cannot confirm navigator routes without the mobile repo. |
| D4. Mobile lint/typecheck | ❌ | `npm run lint && npm run typecheck` cannot run because `papsas-mobile` is absent. |
| E. GET /api/me | ❌ | The backend/API is not reachable, so `email_verified` status cannot be confirmed. |

## Findings

### A) Backend (OTP)
- **A1 – Health & HTTPS behavior**: Attempting to list the requested backend directory fails, so none of the `curl` health checks can be executed locally.
  ```
  $ ls /srv/papsas/app
  ls: cannot access '/srv/papsas/app': No such file or directory
  ```
  Without that path the gunicorn process and nginx proxy are not reachable from here.

- **A2 – Email backend outbox**: Same directory absence prevents sourcing the venv and running `manage.py shell`. There is no evidence for `EMAIL_BACKEND` or `EMAIL_FILE_PATH` because the code is not present in this workspace.

- **A3 – OTP flow**: `papsas-otp` and the API host `https://api.papsasinc.com/api` cannot be contacted from this directory, so the `{}` body, limiter headers, and email verification results are unknown.

- **A4 – Rate limiting**: The `/auth/email/start` burst cannot be issued and `/var/log/nginx/error.log` cannot be tailed here, so there is no proof of `429` responses or the `limiting requests, zone "otp_zone"` log entry.

### B) DevOps – systemd & Nginx
- **B1 – systemd unit**: `systemctl cat papsas.service` (and any drop-in/`ExecReload`) requires the actual Ubuntu host; the current workspace lacks `/etc/systemd/system` entries for inspection.

- **B2 – Nginx OTP location snippet**: `/etc/nginx/snippets/otp_email_limit_location.conf` and `sudo nginx -t` are unreachable, so the rate-limit snippet presence, `proxy_pass`, headers, and config test cannot be proven here.

### C) Web (Vite + TS)
- **C1 – Base URL & dev proxy**: `papsas-web/src/modules/lib/http.ts:3-19` now defines `defaultDevBase`, `defaultProdBase`, a `normalizeBase` helper, and selects `/proxy_api/` in dev or `/api/` in prod unless `VITE_API_BASE` overrides. `papsas-web/vite.config.ts:5-17` already proxies `/proxy_api` → `https://api.papsasinc.com/api` with `changeOrigin` and `secure` enabled.

- **C2 – Topbar admin gating**: `papsas-web/src/modules/components/Topbar.tsx:11-68` shows `showAdmin = isAuthed && isAdminUser(user)` and `showResults = showAdmin`, so results and admin links only appear for admin/officer users.

### D) Mobile (Expo RN)
- **D1–D4 – Mobile repo**: The `papsas-mobile` directory does not exist locally (`ls papsas-mobile` reports "No such file or directory"), so there is no access to `startEmailVerification`, `EmailVerifyStartScreen`, navigator routes, or npm scripts.

### E) Result proof (/api/me)
- **E – me endpoint**: The API host `https://api.papsasinc.com/api` is unreachable, so the `GET /api/me` response cannot be captured to verify `email_verified: true` or `email_verified_at`.

## Fixes
- **Web base URL defaults (C1)**: `papsas-web/src/modules/lib/http.ts` now uses helper logic so that dev defaults to `/proxy_api/`, prod defaults to `/api/`, and any `VITE_API_BASE` overrides are normalized to have consistent leading/trailing slashes.
  ```ts
  const defaultDevBase = "/proxy_api/";
  const defaultProdBase = "/api/";

  function normalizeBase(value?: string) {
    if (!value) return "/";
    const absoluteMatch = /^https?:\/\//i.test(value);
    const trimmed = value.replace(/\/+$/, "");
    if (absoluteMatch) return trimmed;
    const withoutSlashes = trimmed.replace(/^\/+/, "");
    return withoutSlashes ? `/${withoutSlashes}/` : "/";
  }

  const envBase = (import.meta.env.VITE_API_BASE as string) || "";
  const baseCandidate = envBase || (import.meta.env.DEV ? defaultDevBase : defaultProdBase);
  const baseURL = normalizeBase(baseCandidate);
  export const http = axios.create({ baseURL, withCredentials: false });
  export const raw = axios.create({ baseURL });
  ```
- **Backend/devops/rate-limit checks**: There is no fixable code in this workspace because the `/srv/papsas` host is not mounted; please execute the requested commands on the actual server and provide their outputs so the audit can confirm PASS.
- **Mobile helpers/screens/navigation**: The `papsas-mobile` repo must be supplied (or its code extracted here); once available, rerun `npm run lint && npm run typecheck` and verify the helper/screen/route requirements.

## Next actions
- [ ] Run the A1–A4, B1–B2, and E commands on the Ubuntu host (`/srv/papsas/app`) and capture their outputs to confirm the backend and nginx behavior.
- [ ] Provide or mount the `/etc/nginx` configuration so `otp_email_limit_location.conf` and `sudo nginx -t` can be inspected and the `ExecReload` drop-in can be reviewed.
- [ ] Supply the `papsas-mobile` repository (branch `main`) locally, then inspect `src/api/authEmail.ts`, `src/screens/EmailVerifyStartScreen.tsx`, navigator routes, and run `npm run lint && npm run typecheck`.
- [ ] After the OTP flow is verified, call `GET /api/me` with the refreshed token to confirm `email_verified: true` and include that output in the next audit.

## GO/NO-GO
- Backend OTP verification: NO-GO (server unreachable)
- Nginx throttling: NO-GO (cannot validate nginx/systemd without host access)
- Mobile email verify flow: NO-GO (mobile repo unavailable)
- Web proxy/base URL: GO (default bases and proxy exist and were codified)
