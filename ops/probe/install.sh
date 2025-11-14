#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
sudo install -m 0755 "$SCRIPT_DIR/probe_election_current.sh" /usr/local/bin/probe_election_current.sh
sudo install -m 0644 "$SCRIPT_DIR/election-probe.service"    /etc/systemd/system/election-probe.service
sudo install -m 0644 "$SCRIPT_DIR/election-probe.timer"      /etc/systemd/system/election-probe.timer
sudo install -d -m 0755 /etc/systemd/system/election-probe.service.d || true
if [ -f "$SCRIPT_DIR/hardening.conf" ]; then
  sudo install -m 0644 "$SCRIPT_DIR/hardening.conf" /etc/systemd/system/election-probe.service.d/hardening.conf
fi
sudo install -d -o papsas -g papsas -m 0750 /var/log/papsas
sudo install -d -o papsas -g papsas -m 0750 /run/papsas || true
sudo install -m 0644 "$SCRIPT_DIR/papsas-probe.logrotate" /etc/logrotate.d/papsas-probe
sudo systemctl daemon-reload
sudo systemctl enable --now election-probe.timer
echo "Copy ops/probe/probe.env.example to /etc/papsas/probe.env and fill secrets, then: sudo systemctl start election-probe.service"
