# expense_database

Purpose
- Provides a SQLite database file (myapp.db) used by the API.
- Health is determined via file existence and connectivity check, not via any TCP port.

Startup behavior
- On container start, the database is initialized via init_db.py if needed.
- Health is reported by healthcheck.sh which:
  - Locates the DB file via db_connection.txt or defaults to myapp.db
  - Runs test_db.py to verify SQLite connectivity
- No Node/Express server is started by this container.

Optional: local DB visualizer
- A local-only database viewer is available in db_visualizer/.
- This is NOT part of the container startup and is not required for readiness.
- To use locally:
  1) cd expense-splitter-for-small-shops-40774-40785/expense_database/db_visualizer
  2) Ensure sqlite.env (auto-written by init_db.py) has SQLITE_DB pointing to your database file
  3) npm install && npm run start
  4) Open http://localhost:3020

Notes
- Avoid adding any step in Dockerfile or compose that starts server.js automatically.
- The API service (3001) and frontend (3000) do not rely on any port from this container.
