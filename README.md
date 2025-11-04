# THESIS

### Results CSV & Explain (Officer/Admin)

- CSV (server-first): `GET /api/elections/:id/results/export.csv` downloads `results-election-<id>.csv`. If blocked or missing, the web app falls back to a client-generated CSV based on results JSON.
- Analytics: `GET /api/elections/:id/analytics` returns per-position totals with `meta.totalVotes`.
- Explain (dual-key, backward compatible): `POST /api/elections/:id/explain` returns `{ short, long, text }`, where `text` mirrors `short` for legacy clients.
- All API calls use slashless paths and share the axios client with auth refresh.

### Admin Candidates

- Manage candidates under the Admin Election page “Candidates” tab.
- Inline position changes are optimistic and rollback on failure with a toast.
- Adding a duplicate candidacy shows a 409 “Already exists” toast via unified error mapping.
- User search debounces and prefers `/api/users?query=`; if unavailable, the UI falls back to raw `member_id`.
