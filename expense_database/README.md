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
- Do not invoke npm start or node server.js from this container during build/startup.

Containerization guidance (no TCP port, file-based healthcheck)
- Do not EXPOSE or depend on TCP port 3020 (or any TCP port) for this container.
- Use a file-based healthcheck so the container reaches healthy without any port checks.
- Example Dockerfile snippet:
  FROM python:3.11-slim
  WORKDIR /app
  COPY . /app
  RUN chmod +x healthcheck.sh init_db.py && \
      python3 init_db.py
  HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD ["bash","healthcheck.sh"]
  CMD ["sleep","infinity"]

- Example docker-compose snippet:
  services:
    expense_database:
      build: ./expense_database
      # Do NOT expose any port here; SQLite is file-based
      healthcheck:
        test: ["CMD","bash","healthcheck.sh"]
        interval: 30s
        timeout: 5s
        retries: 3
      volumes:
        - ./expense_database:/app

Optional: local DB visualizer (manual-only)
- A local-only database viewer is available in db_visualizer/.
- This is NOT part of the container startup and is not required for readiness.
- To use locally:
  1) cd expense-splitter-for-small-shops-40774-40785/expense_database/db_visualizer
  2) Ensure sqlite.env (auto-written by init_db.py) has SQLITE_DB pointing to your database file
  3) npm ci (or npm install) — express is pinned to ^4.19.2
  4) npm run start
  5) Open http://localhost:3020

Notes
- Avoid adding any step in Dockerfile or compose that starts server.js automatically.
- The API service (3001) and frontend (3000) do not rely on any port from this container.
- If you previously had healthchecks or readiness probes against port 3020, remove them and use the file-based healthcheck shown above.
