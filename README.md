# expense-splitter-for-small-shops-40774-40785

Database container (SQLite) healthcheck
- SQLite is file-based and does not expose a TCP port. The expense_database container uses a file-based healthcheck (healthcheck.sh) which:
  - Validates that the myapp.db file exists (or uses the path recorded in db_connection.txt).
  - Runs test_db.py to confirm SQLite connectivity.
- The container does NOT bind or require any TCP port (including 3020) to be considered healthy.
- IMPORTANT: The container does not run any npm start or node server.js during build or startup.

Startup/Preview behavior
- Start command for expense_database is: `python init_db.py`
- Healthcheck is command-based: `bash expense_database/healthcheck.sh` (with inline fallback `test -f expense_database/myapp.db && echo OK` where needed)
- No readiness checks or port mappings are configured for expense_database.
- Builds no longer wait on TCP port 3020.

Optional: DB Visualizer (local-only, not started in container)
- An optional Node server exists at expense_database/db_visualizer that can show tables for various databases (including SQLite).
- It is NOT required for the database container readiness and is NOT launched by the container.
- To run it locally (optional):
  1) cd expense-splitter-for-small-shops-40774-40785/expense_database/db_visualizer
  2) Ensure sqlite.env contains a valid SQLITE_DB path (init_db.py writes this automatically).
  3) npm ci (or npm install) — express is pinned to ^4.19.2 for compatibility
  4) npm run start
  5) Access http://localhost:3020/health (for readiness) or http://localhost:3020 to see the viewer.

Notes
- The database container does not launch any Node server, avoiding MODULE_NOT_FOUND errors related to Express.
- expense_api (3001) and expense_frontend (3000) start and function independently of any port exposed by the database container.