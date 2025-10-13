#!/usr/bin/env bash
set -eo pipefail

API_BASE=${API_BASE:-http://127.0.0.1:8000}
TOK_FILE=${TOK_FILE:-.jwt.env}

jwt_save() {
  : >"$TOK_FILE"
  printf 'export ACCESS=%q\nexport REFRESH=%q\n' "${ACCESS:-}" "${REFRESH:-}" >>"$TOK_FILE"
  echo "Tokens saved to $TOK_FILE"
}

jwt_load() {
  if [ -f "$TOK_FILE" ]; then
    # shellcheck disable=SC1090
    . "$TOK_FILE" || true
  fi
}

jwt_login() {
  local user="${1:-admin}" pass="${2:-Papsas1234}"
  local resp code body
  resp=$(curl -sS -w '\n%{http_code}' -X POST "$API_BASE/api/auth/login/" \
         -H "Content-Type: application/json" \
         -d "{\"username\":\"$user\",\"password\":\"$pass\"}")
  code="${resp##*$'\n'}"; body="${resp%$'\n'*}"
  if [ "$code" != "200" ]; then
    echo "Login failed (HTTP $code): $body" >&2
    return 1
  fi
  ACCESS=$(echo "$body"  | python -c "import sys,json; print(json.load(sys.stdin).get('access',''))")
  REFRESH=$(echo "$body" | python -c "import sys,json; print(json.load(sys.stdin).get('refresh',''))")
  if [ -z "${ACCESS:-}" ] || [ -z "${REFRESH:-}" ]; then
    echo "Login parse failed. Body was: $body" >&2
    return 1
  fi
  export ACCESS REFRESH
  jwt_save
  echo "Logged in."
}

jwt_refresh() {
  if [ -z "${REFRESH:-}" ]; then
    echo "No REFRESH token; doing full login."
    jwt_login "$@"
    return
  fi
  local resp code body
  resp=$(curl -sS -w '\n%{http_code}' -X POST "$API_BASE/api/auth/refresh/" \
         -H "Content-Type: application/json" \
         -d "{\"refresh\":\"$REFRESH\"}")
  code="${resp##*$'\n'}"; body="${resp%$'\n'*}"
  if [ "$code" != "200" ]; then
    echo "Refresh failed (HTTP $code): $body" >&2
    jwt_login "$@"
    return
  fi
  ACCESS=$(echo "$body" | python -c "import sys,json; print(json.load(sys.stdin).get('access',''))")
  if [ -z "${ACCESS:-}" ]; then
    echo "Refresh parse failed. Body was: $body" >&2
    jwt_login "$@"
    return
  fi
  export ACCESS
  jwt_save
  echo "Access token refreshed."
}

jwt_valid() {
  [ -n "${ACCESS:-}" ] || return 1
  # Call a protected endpoint; treat 200 as valid
  local resp code
  resp=$(curl -sS -w '\n%{http_code}' \
         -H "Accept: application/json" \
         -H "Authorization: Bearer $ACCESS" \
         "$API_BASE/api/elections/1/ballot" || true)
  code="${resp##*$'\n'}"
  [ "$code" = "200" ]
}

jwt_login_if_needed() {
  jwt_load
  if jwt_valid; then
    echo "Token OK."
    return
  fi
  jwt_refresh "$@"
  if jwt_valid; then
    echo "Refreshed token OK."
    return
  fi
  jwt_login "$@"
  if jwt_valid; then
    echo "New login OK."
  else
    echo "Login still invalid." >&2
    return 1
  fi
}
