# Backend Registration & Operations

## Registration API contract

- **POST /api/events/&lt;id&gt;/registration** (member-only):
  - Success: HTTP 201 with `{"registered": true}`.
  - Errors: Returns JSON `{"code": <code>, "message": <message>}` using the shared `error_response` payload.
  - Possible error `code` values: `EVENT_NOT_FOUND`, `EVENT_CLOSED`, `MEMBER_ONLY`, `ALREADY_REGISTERED`, `RATE_LIMITED`.

- **DELETE /api/events/&lt;id&gt;/registration**:
  - Success: HTTP 204 with an empty body.
  - Errors: Same `{code,message}` shape as POST, with `code` values `EVENT_NOT_FOUND`, `MEMBER_ONLY`, `NOT_REGISTERED`, or `RATE_LIMITED`.

All registration errors bubble up to the client with explicit codes so callers can inform the user (e.g., `ALREADY_REGISTERED` vs `MEMBER_ONLY`).

## Health endpoint

- **GET /api/health** responds with `{"status": "ok"}` and HTTP 200 when the Django app can reach the default database.
- If the database connection fails, the response becomes `{"status": "error", "code": "DB_UNAVAILABLE", "message": "..."}`
  with HTTP 500 so probes can distinguish application-level availability vs. database outages.

## Backups & probes

- Nightly Postgres dumps live under `/srv/papsas/backup` as `db-<name>_<timestamp>.sql.gz`; files older than 14 days are purged automatically.
- A health probe hits `/api/health` every five minutes, logging failures to `/var/log/papsas/health-probe.log`.
- Confirm the timers with `systemctl list-timers | grep papsas` (look for `papsas-health-probe.timer` and `papsas-pg-backup.timer`).
