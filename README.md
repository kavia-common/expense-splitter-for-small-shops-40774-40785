# expense-splitter-for-small-shops-40774-40785

Database container (SQLite) healthcheck
- SQLite is file-based and does not expose a TCP port. The expense_database container now uses a file-based healthcheck (healthcheck.sh) which:
  - Validates that the myapp.db file exists (or uses the path recorded in db_connection.txt).
  - Runs test_db.py to confirm SQLite connectivity.
- This means the container does NOT require port 3020 to be open to be considered healthy.

Optional: DB Visualizer (port 3020)
- An optional Node server exists at expense_database/db_visualizer that can show tables for various databases (including SQLite).
- It is NOT required for the database container readiness.
- To run it locally (optional):
  1) cd expense-splitter-for-small-shops-40774-40785/expense_database/db_visualizer
  2) Ensure sqlite.env contains a valid SQLITE_DB path (init_db.py writes this automatically).
  3) npm install && npm run start
  4) Access http://localhost:3020/health (for readiness) or http://localhost:3020 to see the viewer.

With this setup, expense_api (3001) and expense_frontend (3000) can start without waiting on any TCP port in the database container.