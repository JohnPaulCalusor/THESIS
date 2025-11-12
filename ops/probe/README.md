# Election Probe (systemd)
Files:
- probe_election_current.sh -> /usr/local/bin/
- election-probe.service    -> /etc/systemd/system/
- election-probe.timer      -> /etc/systemd/system/
- papsas-probe.logrotate    -> /etc/logrotate.d/
- hardening.conf (optional) -> /etc/systemd/system/election-probe.service.d/

Install:
  ./ops/probe/install.sh
Then create /etc/papsas/probe.env from ops/probe/probe.env.example and start:
  sudo systemctl start election-probe.service
