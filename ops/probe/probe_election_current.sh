#!/usr/bin/env bash
set -euo pipefail
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

API="${API:-https://api.papsasinc.com/api}"
RUNDIR="${RUNTIME_DIRECTORY:-/run/papsas}"
TOKEN_FILE="$RUNDIR/probe.token"
LAST_USER_FILE="$RUNDIR/.last_user"

log(){ printf '%s %s\n' "$(date '+%F %T')" "$*" >&2; }

mkdir -p "$RUNDIR" 2>/dev/null || true

# Auto cache-bust if PROBE_USER changed
CUR_USER="${PROBE_USER:-}"
PREV_USER="$(cat "$LAST_USER_FILE" 2>/dev/null || true)"
if [[ "${CUR_USER:-}" != "${PREV_USER:-}" ]]; then
  rm -f "$TOKEN_FILE"
  umask 077; printf '%s' "$CUR_USER" > "$LAST_USER_FILE"
fi

get_token(){
  if [[ -n "${ADMIN:-}" ]]; then printf '%s' "$ADMIN"; return 0; fi
  if [[ -f "$TOKEN_FILE" ]]; then
    local T; T="$(cat "$TOKEN_FILE")"
    if curl -sS -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $T" "$API/health" | grep -qE '^(200|204)$'; then
      printf '%s' "$T"; return 0
    fi
  fi
  if [[ -n "${PROBE_USER:-}" && -n "${PROBE_PASS:-}" ]]; then
    local JCODE T
    JCODE=$(curl -sS -o "$RUNDIR/login.json" -w '%{http_code}' \
      -H 'Content-Type: application/json' \
      -d "{\"username\":\"$PROBE_USER\",\"password\":\"$PROBE_PASS\"}" \
      "$API/auth/login" || true)
    T="$(python3 - <<'PY' "$RUNDIR/login.json" || true
import sys, json, pathlib
p=pathlib.Path(sys.argv[1])
try:
  d=json.loads(p.read_text()); print(d.get("access",""))
except Exception:
  print("")
PY
)"
    log "login -> ${JCODE} token_len=${#T}"
    if [[ -n "$T" ]]; then umask 077; printf '%s' "$T" > "$TOKEN_FILE"; printf '%s' "$T"; return 0; fi
  fi
  printf ''
}

TOKEN="$(get_token || true)"; AUTH=(); [[ -n "$TOKEN" ]] && AUTH=(-H "Authorization: Bearer $TOKEN")

set +o pipefail
CODE="$(curl -sS -H 'Accept: application/json' "${AUTH[@]}" -w '%{http_code}' -o "$RUNDIR/current.json" "$API/elections/current" || true)"
set -o pipefail
log "/elections/current -> $CODE (saved: $RUNDIR/current.json)"

EID="$(python3 - <<'PY' "$RUNDIR/current.json" || true
import sys, json, pathlib
p=pathlib.Path(sys.argv[1])
try:
  d=json.loads(p.read_text())
  print((d[0]["id"] if isinstance(d, list) and d else d.get("id") or ""))
except Exception:
  print("")
PY
)"
if [[ -z "$EID" ]]; then log "WARN: could not resolve election id (continuing)"; exit 0; fi

probe(){ local path="$1"; local code; code="$(curl -sS -o /dev/null -w '%{http_code}' "${AUTH[@]}" "$API$path" || true)"; log "$path -> $code"; }

probe "/elections/$EID/positions"
probe "/elections/$EID/ballot"
probe "/elections/$EID/candidacies"
probe "/elections/$EID/results"
log "done eid=$EID"
