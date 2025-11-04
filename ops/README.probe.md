PAPSAS Ops Probe — elections current

Overview
- Script `ops/probe_election_current.sh` checks the canonical API endpoints:
  - `GET /api/elections/current`
  - `GET /api/elections/<id>/positions`
  - `GET /api/elections/<id>/results`

Install (server)
- Copy script and make it executable:
  - `sudo install -m 0755 ops/probe_election_current.sh /usr/local/bin/papsas-probe`
- Optional: provide admin token at runtime via env:
  - `ADMIN=... API=https://api.papsasinc.com/api papsas-probe`

Systemd (optional)
- `/etc/systemd/system/papsas-probe.service`:
  - [Service]
  - Type=oneshot
  - Environment="API=https://api.papsasinc.com/api"
  - ExecStart=/usr/local/bin/papsas-probe
  - StandardOutput=append:/var/log/papsas/probe.log
  - StandardError=append:/var/log/papsas/probe.log

- `/etc/systemd/system/papsas-probe.timer`:
  - [Timer]
  - OnCalendar=*:0/10
  - Persistent=true
  - [Install]
  - WantedBy=timers.target

- Enable & start:
  - `sudo systemctl daemon-reload`
  - `sudo systemctl enable --now papsas-probe.timer`
# Election Probe – Token-Aware Health Checks

**Last updated:** 2025-11-04 (+08)  
**Status:** Live on production

This document explains how we probe the current election endpoints with a **token-aware** script that logs in automatically, caches an access token, and retries on `401`. Results are written to `/var/log/papsas/probe.log`. A systemd timer runs the probe every 5 minutes.

---

## What it checks

For the **current** election (`GET /api/elections/current` → `id`), the probe hits:

- `GET /api/elections/{id}/positions`
- `GET /api/elections/{id}/results`
- `GET /api/elections/{id}/ballot`
- `GET /api/elections/{id}/candidacies`

Each line is logged as:


2025-11-04T16:06:57+0800 GET /elections/1/ballot -> 200 (OK)

Tags:
- `OK`   = 2xx
- `AUTH?`= 4xx (likely missing/expired token)
- `WARN` = 5xx

---

## Prereqs

- Ubuntu with `systemd`
- `curl`, `python3`
- API reachable at the URL set in `API` (default: `https://api.papsasinc.com/api`)

---

## Configuration file

Create `/etc/papsas/probe.env` (owned by root, `0600`) with:

```env
API=https://api.papsasinc.com/api
PROBE_USER=probe@papsasinc.com
PROBE_PASS=**********        # strong, unique

Permissions:
sudo install -d -m 755 -o root -g adm /var/log/papsas
sudo install -d -m 755 /etc/papsas
echo 'API=https://api.papsasinc.com/api' | sudo tee /etc/papsas/probe.env >/dev/null
echo 'PROBE_USER=probe@papsasinc.com'   | sudo tee -a /etc/papsas/probe.env >/dev/null
echo 'PROBE_PASS=**********'            | sudo tee -a /etc/papsas/probe.env >/dev/null
sudo chown root:root /etc/papsas/probe.env
sudo chmod 600 /etc/papsas/probe.env


Note: The script also respects an ADMIN environment variable (a raw Bearer token) if present in the systemd service environment. If ADMIN is set, username/password login is skipped.


Probe script (installed on server)
Path: /usr/local/bin/probe_election_current.sh
Behavior:


Loads /etc/papsas/probe.env if present


Logs in via /auth/login/ using PROBE_USER/PROBE_PASS


Caches token in /run/papsas/probe.token for 10 minutes


Retries a request once if it gets 401


Appends to /var/log/papsas/probe.log


To run manually:
sudo /usr/local/bin/probe_election_current.sh
sudo tail -n 50 /var/log/papsas/probe.log

Token cache reset:
sudo rm -f /run/papsas/probe.token
sudo /usr/local/bin/probe_election_current.sh


Systemd timer
A systemd timer runs the script every 5 minutes.
Check status:
systemctl status --no-pager election-probe.timer

Restart timer (optional after edits):
sudo systemctl restart election-probe.timer


Log rotation
Logrotate config (on server): /etc/logrotate.d/papsas-probe
/var/log/papsas/probe.log {
  daily
  rotate 14
  compress
  missingok
  notifempty
  create 0640 root adm
}

Force a rotation (optional):
sudo logrotate -f /etc/logrotate.conf


(Optional) Create the probe user in Django
Use Django shell to ensure the PROBE_USER exists and has a strong password:
from django.contrib.auth import get_user_model
U = get_user_model()
u, created = U.objects.get_or_create(
    username='probe@papsasinc.com',
    defaults={'email':'probe@papsasinc.com', 'is_active': True}
)
u.is_active = True
u.set_password('**********')   # must match PROBE_PASS
u.save()
print("OK:", "created" if created else "updated")


Troubleshooting


401 (AUTH?)


Clear token cache: sudo rm -f /run/papsas/probe.token and re-run the script.


Verify credentials in /etc/papsas/probe.env.


Test auth manually:
curl -sS -H 'Content-Type: application/json' \
  -d '{"username":"probe@papsasinc.com","password":"**********"}' \
  https://api.papsasinc.com/api/auth/login/ | python3 -m json.tool

Confirm an access token is returned.




5xx (WARN)


Check the API service logs and Nginx for backend errors.




No logs


Ensure /var/log/papsas exists and is writable by root.


Confirm the timer is active: systemctl status election-probe.timer.




Security notes


Keep /etc/papsas/probe.env at 0600, owned by root. Never commit it.


Use a non-admin probe account with minimal permissions.


Rotate PROBE_PASS periodically, then clear /run/papsas/probe.token.


The script prints only status codes, no secrets.



Reverting the script
If you backed up the script (recommended):
ls -t /usr/local/bin/probe_election_current.sh.bak.*
sudo cp /usr/local/bin/probe_election_current.sh.bak.<TIMESTAMP> /usr/local/bin/probe_election_current.sh
sudo chmod +x /usr/local/bin/probe_election_current.sh


Acceptance checklist


sudo /usr/local/bin/probe_election_current.sh runs without errors


/var/log/papsas/probe.log shows 200 (OK) for /positions, /results, /ballot, /candidacies


systemctl status election-probe.timer shows active (waiting)


A manual 401 clears after token cache removal + rerun


Probe creds stored as /etc/papsas/probe.env with 0600 perms



Changelog


2025-11-04: Switch to token-aware probe that auto-logins and caches token; probes ballot and candidacies in addition to positions and results; add troubleshooting and security guidance.



**Then run in the integrated terminal:**

```bash
git add ops/README.probe.md
git commit -m "docs(ops): token-aware election probe + /etc/papsas/probe.env usage"
