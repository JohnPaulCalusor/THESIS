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

