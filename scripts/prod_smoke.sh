#!/usr/bin/env bash
set -euo pipefail

BASE="https://api.papsasinc.com"

# Allow overriding via env:
LOGIN_USER="${LOGIN_USER:-alice@example.com}"   # or 'alice' if username login
LOGIN_PASS="${LOGIN_PASS:-P@ssw0rd!}"

# Choose Python: prefer venv, then system python3
PYBIN="/srv/papsas/app/venv/bin/python"
if [ ! -x "$PYBIN" ]; then
  PYBIN="$(command -v python3)"
fi
if [ -z "${PYBIN:-}" ]; then
  echo "No python3 found." >&2; exit 2
fi

echo "== Health =="
curl -fsS "$BASE/api/health" && echo

echo "== Login =="
curl -fsS -X POST "$BASE/api/auth/login" \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d "{\"username\":\"$LOGIN_USER\",\"password\":\"$LOGIN_PASS\"}" | tee /tmp/prod-login.json

ACCESS=$("$PYBIN" - <<'PY'
import json,sys
d=json.load(open('/tmp/prod-login.json','r',encoding='utf-8'))
print(d.get('access') or d.get('accessToken') or d.get('token') or d.get('key') or d.get('jwt',''))
PY
)

if [ -z "$ACCESS" ]; then
  echo "!! No access token in login response"; cat /tmp/prod-login.json; exit 1
fi
echo "access: ${ACCESS:0:16}..."

echo "== /users/me =="
curl -fsS "$BASE/api/users/me" \
  -H "Accept: application/json" -H "Authorization: Bearer $ACCESS" && echo

echo "== /elections/ =="
curl -fsS "$BASE/api/elections/" \
  -H "Accept: application/json" -H "Authorization: Bearer $ACCESS" && echo

echo "OK ✅"
