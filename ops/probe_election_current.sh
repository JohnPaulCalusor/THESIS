#!/usr/bin/env bash
set -euo pipefail

API="${API:-https://api.papsasinc.com/api}"
LOG="${LOG:-/var/log/papsas/probe.log}"
AUTH=()
[ -n "${ADMIN:-}" ] && AUTH=(-H "Authorization: Bearer $ADMIN")

ts() { date --iso-8601=seconds; }
code_of() { curl -sS "${AUTH[@]}" -o /dev/null -w "%{http_code}" "$1" || echo "ERR"; }

current="$API/elections/current"
c=$(code_of "$current")
echo "$(ts) GET /elections/current -> $c"

if [ "$c" = "200" ]; then
  EID=$(curl -sS "${AUTH[@]}" "$current" | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
  p=$(code_of "$API/elections/$EID/positions")
  r=$(code_of "$API/elections/$EID/results")
  echo "$(ts) GET /elections/$EID/positions -> $p"
  echo "$(ts) GET /elections/$EID/results  -> $r"
fi

