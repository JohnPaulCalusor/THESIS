#!/usr/bin/env bash
set -euo pipefail

cd /srv/papsas/app
source venv/bin/activate
git pull --ff-only
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
deactivate

# Try to restart the service if this user has sudo; otherwise, print instruction.
if command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then
  sudo systemctl restart papsas
else
  echo "Note: no sudo privileges in this shell. Please run: sudo systemctl restart papsas"
fi

sleep 2

# Smoke: pass creds via env when calling this script
LOGIN_USER="${LOGIN_USER:-smokebot@example.com}"
LOGIN_PASS="${LOGIN_PASS:-ChangeMe123!}"
LOGIN_FIELD="${LOGIN_FIELD:-username}"

LOGIN_USER="$LOGIN_USER" LOGIN_PASS="$LOGIN_PASS" LOGIN_FIELD="$LOGIN_FIELD" \
  make -C /srv/papsas/app smoke
