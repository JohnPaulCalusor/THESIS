#!/usr/bin/env bash
set -o pipefail   # no -e so errors don't kill the script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1090
source "$SCRIPT_DIR/jwt-helpers.sh"

API_BASE=${API_BASE:-http://127.0.0.1:8000}

# Optional: choose which user the smoke runs as
JWT_USER=${JWT_USER:-admin}
JWT_PASS=${JWT_PASS:-Papsas1234}

pretty(){ command -v jq >/dev/null 2>&1 && jq . || python -m json.tool; }

curl_json() {
  local method="$1"; shift
  local url="$1"; shift
  local data="${1:-}"

  local resp code body
  if [ -n "$data" ]; then
    resp=$(curl -sS -w '\n%{http_code}' -X "$method" \
      -H "Accept: application/json" -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS" \
      "$url" -d "$data")
  else
    resp=$(curl -sS -w '\n%{http_code}' -X "$method" \
      -H "Accept: application/json" \
      -H "Authorization: Bearer $ACCESS" \
      "$url")
  fi
  code="${resp##*$'\n'}"; body="${resp%$'\n'*}"
  echo "HTTP $code"
  printf '%s\n' "$body" | pretty || printf '%s\n' "$body"
  return 0  # never exit the script on HTTP errors
}

echo "== Smoke: ballot/vote/results =="
TOK_FILE=".jwt.${JWT_USER}.env"; export TOK_FILE; jwt_login "$JWT_USER" "$JWT_PASS" || echo "WARN: login failed, continuing"

echo "# Ballot"
curl_json GET "$API_BASE/api/elections/1/ballot"

echo "# Vote (candidacyId=1 by default)"
curl_json POST "$API_BASE/api/elections/1/vote" '{"candidacyId":1}'

echo "# Ballot after vote"
curl_json GET "$API_BASE/api/elections/1/ballot"

echo "# Results"
curl_json GET "$API_BASE/api/elections/1/results"
