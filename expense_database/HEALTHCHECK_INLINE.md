This project prefers the script-based healthcheck:
  bash expense_database/healthcheck.sh

If a platform requires an inline healthcheck command string instead of a script:
  test -f expense_database/myapp.db && echo OK

Either approach ensures no TCP port readiness is required for the SQLite database container.
