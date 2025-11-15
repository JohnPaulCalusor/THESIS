#!/usr/bin/env bash
set -euo pipefail

# ========= CONFIG =========
API_BASE="${API_BASE:-https://api.papsasinc.com/api}"

ADMIN_USER="${ADMIN_USER:-admin}"
ADMIN_PASS="${ADMIN_PASS:-ChangeMe_Admin_2025!}"

OFFICER_USER="${OFFICER_USER:-officer}"
OFFICER_PASS="${OFFICER_PASS:-ChangeMe_Officer_2025!}"

MEMBER_USER="${MEMBER_USER:-member2}"
MEMBER_PASS="${MEMBER_PASS:-memberpass}"

# Optional: skip vote flow in prod (safe default)
CHECK_VOTE_FLOW="${CHECK_VOTE_FLOW:-0}"   # 0 = skip, 1 = run

# ========= HELPERS =========
log() {
  printf '[GA] %s\n' "$*" >&2
}

fail() {
  printf '[GA][FAIL] %s\n' "$*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Required command '$1' not found in PATH"
}

require_cmd curl
require_cmd jq

curl_json() {
  local method="$1" url="$2" data="${3:-}" token="${4:-}"
  local auth_header=()
  [ -n "$token" ] && auth_header=(-H "Authorization: Bearer $token")

  if [ "$method" = "GET" ]; then
    curl -sS -w '\n%{http_code}' "${auth_header[@]}" \
      -H 'Accept: application/json' \
      "$url"
  else
    curl -sS -w '\n%{http_code}' "${auth_header[@]}" \
      -H 'Accept: application/json' \
      -H 'Content-Type: application/json' \
      -d "$data" \
      "$url"
  fi
}

login() {
  local username="$1" password="$2"
  local url="${API_BASE%/}/auth/login"

  log "Logging in as '$username' against $url"

  # Try email payload
  local payload body http_code json access
  payload=$(jq -n --arg u "$username" --arg p "$password" '{email: $u, password: $p}')
  body=$(curl_json POST "$url" "$payload")
  http_code=$(tail -n1 <<< "$body")
  json=$(head -n-1 <<< "$body")

  if [ "$http_code" -ne 200 ]; then
    # Try username payload
    payload=$(jq -n --arg u "$username" --arg p "$password" '{username: $u, password: $p}')
    body=$(curl_json POST "$url" "$payload")
    http_code=$(tail -n1 <<< "$body")
    json=$(head -n-1 <<< "$body")
  fi

  [ "$http_code" -eq 200 ] || fail "Login for '$username' failed (HTTP $http_code): $json"

  access=$(jq -r '.access // empty' <<< "$json")
  [ -n "$access" ] || fail "Login for '$username' did not return 'access' token: $json"

  echo "$access"
}

check_me_groups() {
  local token="$1" role_label="$2"
  local url="${API_BASE%/}/auth/me"
  log "Checking /auth/me groups[] for $role_label"

  local body http_code json
  body=$(curl_json GET "$url" "" "$token")
  http_code=$(tail -n1 <<< "$body")
  json=$(head -n-1 <<< "$body")

  [ "$http_code" -eq 200 ] || fail "/auth/me ($role_label) expected 200, got $http_code: $json"

  jq -e '.groups and (.groups | type == "array")' <<< "$json" >/dev/null \
    || fail "/auth/me ($role_label) response missing groups[] array: $json"

  log "PASS: /auth/me has groups[] for $role_label"
}

resolve_current_election_id() {
  local url="${API_BASE%/}/elections/current"
  log "Resolving current election id from $url"

  local body http_code json
  body=$(curl_json GET "$url")
  http_code=$(tail -n1 <<< "$body")
  json=$(head -n-1 <<< "$body")

  [ "$http_code" -eq 200 ] || fail "/elections/current expected 200, got $http_code: $json"

  # Accept either object with id or array[0].id
  local eid
  eid=$(jq -r 'if type=="array" then (.[0].id // empty) else (.id // empty) end' <<< "$json")
  [ -n "$eid" ] || fail "Could not resolve election id from /elections/current payload: $json"

  log "Current election id = $eid"
  echo "$eid"
}

check_results_public() {
  local eid="$1"
  local url="${API_BASE%/}/elections/${eid}/results"
  log "Checking public results at $url"

  local body http_code
  body=$(curl_json GET "$url")
  http_code=$(tail -n1 <<< "$body")

  [ "$http_code" -eq 200 ] || fail "/elections/$eid/results expected 200 (public), got $http_code"
  log "PASS: /elections/$eid/results is public 200"
}

check_analytics_rbac() {
  local eid="$1" officer_token="$2" member_token="$3"
  local url="${API_BASE%/}/elections/${eid}/analytics"

  log "Checking analytics RBAC at $url"

  local body http_code

  # Officer/admin must see 200
  body=$(curl_json GET "$url" "" "$officer_token")
  http_code=$(tail -n1 <<< "$body")
  [ "$http_code" -eq 200 ] || fail "Analytics (officer) expected 200, got $http_code: $(head -n-1 <<< "$body")"
  log "PASS: /elections/$eid/analytics officer 200"

  # Member must see 403
  body=$(curl_json GET "$url" "" "$member_token")
  http_code=$(tail -n1 <<< "$body")
  [ "$http_code" -eq 403 ] || fail "Analytics (member) expected 403, got $http_code: $(head -n-1 <<< "$body")"
  log "PASS: /elections/$eid/analytics member 403"
}

check_csv_headers() {
  local eid="$1"
  local url="${API_BASE%/}/elections/${eid}/results/export.csv"
  log "Checking CSV headers at $url"

  # Dump headers + status, ignore body
  local resp headers http_code
  resp=$(curl -sS -D - -o /tmp/ga_results.csv -w '\n%{http_code}' "$url")
  http_code=$(tail -n1 <<< "$resp")
  headers=$(head -n-1 <<< "$resp")

  [ "$http_code" -eq 200 ] || fail "CSV export expected 200, got $http_code"

  local ct cd expected_filename
  ct=$(printf '%s\n' "$headers" | grep -i '^Content-Type:' | tr -d '\r')
  cd=$(printf '%s\n' "$headers" | grep -i '^Content-Disposition:' | tr -d '\r')

  expected_filename="results-election-${eid}.csv"

  [[ "$ct" == *"text/csv"* && "$ct" == *"charset=utf-8"* ]] \
    || fail "CSV Content-Type header missing text/csv; charset=utf-8. Got: $ct"

  [[ "$cd" == *"attachment"* && "$cd" == *"$expected_filename"* ]] \
    || fail "CSV Content-Disposition header missing $expected_filename. Got: $cd"

  log "PASS: CSV headers OK (Content-Type + filename)"
}

check_vote_flow_optional() {
  local eid="$1" member_token="$2"
  if [ "$CHECK_VOTE_FLOW" != "1" ]; then
    log "Skipping vote flow check (CHECK_VOTE_FLOW != 1)."
    return 0
  fi

  log "Running OPTIONAL vote flow check for election $eid (this should only be used on staging/test)."

  local url="${API_BASE%/}/elections/${eid}/vote"
  local payload body http_code json code

  # WARNING: This is disabled by default because it actually casts a vote.
  # Only enable on staging/test with a safe test election and a correct payload.
  payload='{}'  # Replace with a real payload if you ever enable this.

  # First vote
  body=$(curl_json POST "$url" "$payload" "$member_token")
  http_code=$(tail -n1 <<< "$body")
  json=$(head -n-1 <<< "$body")
  [ "$http_code" -eq 200 ] || fail "First vote expected 200, got $http_code: $json"

  # Second vote
  body=$(curl_json POST "$url" "$payload" "$member_token")
  http_code=$(tail -n1 <<< "$body")
  json=$(head -n-1 <<< "$body")
  [ "$http_code" -eq 409 ] || fail "Second vote expected 409, got $http_code: $json"

  code=$(jq -r '.code // empty' <<< "$json")
  [ "$code" = "ALREADY_VOTED" ] || fail "Second vote expected code=ALREADY_VOTED, got: $json"

  log "PASS: Optional vote flow 200 then 409 ALREADY_VOTED"
}

# ========= MAIN =========

log "Starting GA checks against $API_BASE"

ADMIN_TOKEN=$(login "$ADMIN_USER" "$ADMIN_PASS")
OFFICER_TOKEN=$(login "$OFFICER_USER" "$OFFICER_PASS")
MEMBER_TOKEN=$(login "$MEMBER_USER" "$MEMBER_PASS")

check_me_groups "$ADMIN_TOKEN" "admin"
check_me_groups "$OFFICER_TOKEN" "officer"
check_me_groups "$MEMBER_TOKEN" "member"

EID=$(resolve_current_election_id)

check_results_public "$EID"
check_analytics_rbac "$EID" "$OFFICER_TOKEN" "$MEMBER_TOKEN"
check_csv_headers "$EID"
check_vote_flow_optional "$EID" "$MEMBER_TOKEN"

log "ALL PASS: GA checks succeeded."
exit 0
