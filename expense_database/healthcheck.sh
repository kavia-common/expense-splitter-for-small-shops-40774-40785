#!/usr/bin/env bash
# Lightweight healthcheck for SQLite-based expense_database container.
# This script avoids any TCP port checks and validates the database file and connectivity.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_FILE_DEFAULT="${SCRIPT_DIR}/myapp.db"
DB_FILE=""

# Try to read db_connection.txt if present to detect DB path
CONN_FILE="${SCRIPT_DIR}/db_connection.txt"
if [[ -f "${CONN_FILE}" ]]; then
  # Parse the "File path: ..." line if present
  FILE_PATH_LINE="$(grep -E '^# File path:' "${CONN_FILE}" || true)"
  if [[ -n "${FILE_PATH_LINE}" ]]; then
    DB_FILE="$(echo "${FILE_PATH_LINE}" | sed 's/^# File path:[[:space:]]*//')"
  fi
fi

# Fallback to default if db_connection.txt not available or no path found
if [[ -z "${DB_FILE}" ]]; then
  DB_FILE="${DB_FILE_DEFAULT}"
fi

# Ensure DB file exists (init_db.py should have created it)
if [[ ! -f "${DB_FILE}" ]]; then
  echo "Database file not found at ${DB_FILE}"
  exit 1
fi

# Use the provided test_db.py to validate SQLite connectivity
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not available for healthcheck"
  exit 1
fi

# Run test_db.py from the database directory so it can locate myapp.db by default,
# but prefer explicit DB path if it differs.
pushd "${SCRIPT_DIR}" >/dev/null

# If DB_FILE is not the default name in this directory, create a temporary symlink so test_db.py can find it
TEMP_LINK_CREATED=0
if [[ "${DB_FILE}" != "${DB_FILE_DEFAULT}" ]]; then
  if [[ ! -f "${DB_FILE_DEFAULT}" ]]; then
    ln -s "${DB_FILE}" "${DB_FILE_DEFAULT}"
    TEMP_LINK_CREATED=1
  fi
fi

set +e
python3 test_db.py
STATUS=$?
set -e

# Cleanup symlink if created
if [[ "${TEMP_LINK_CREATED}" -eq 1 ]]; then
  rm -f "${DB_FILE_DEFAULT}"
fi

popd >/dev/null

if [[ "${STATUS}" -ne 0 ]]; then
  echo "SQLite connectivity test failed"
  exit 1
fi

echo "ok"
exit 0
