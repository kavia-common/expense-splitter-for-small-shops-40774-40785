#!/usr/bin/env python3
"""Initialize SQLite database for expense_database with expense-specific schema.

This script:
- Ensures the database exists and is accessible
- Enables PRAGMA foreign_keys
- Creates demo tables (app_info, users) if not present
- Creates expense tables:
    members, expenses, expense_participants
- Adds indexes on expenses(payer_id), expense_participants(expense_id), expense_participants(member_id)
- Creates or replaces balances_view(member_id, name, net_cents) where:
    net_cents = credits (sum of expenses.amount_cents paid by member)
               - debits (sum of expense_participants.share_cents for member)
- Is idempotent and safe to re-run without dropping existing demo tables.
"""

import sqlite3
import os
from contextlib import closing

DB_NAME = "myapp.db"
DB_USER = "kaviasqlite"  # Not used for SQLite, but kept for consistency
DB_PASSWORD = "kaviadefaultpassword"  # Not used for SQLite, but kept for consistency
DB_PORT = "5000"  # Not used for SQLite, but kept for consistency

print("Starting SQLite setup...")

# Check if database already exists
db_exists = os.path.exists(DB_NAME)
if db_exists:
    print(f"SQLite database already exists at {DB_NAME}")
    # Verify it's accessible
    try:
        with closing(sqlite3.connect(DB_NAME)) as _tmp_conn:
            _tmp_conn.execute("SELECT 1")
        print("Database is accessible and working.")
    except Exception as e:
        print(f"Warning: Database exists but may be corrupted: {e}")
else:
    print("Creating new SQLite database...")

# Connect and initialize schema
with closing(sqlite3.connect(DB_NAME)) as conn:
    cursor = conn.cursor()

    # Ensure foreign keys are enabled
    cursor.execute("PRAGMA foreign_keys = ON")

    # Keep existing demo tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert/Upsert initial app_info data
    cursor.execute("INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)", ("project_name", "expense_database"))
    cursor.execute("INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)", ("version", "0.1.0"))
    cursor.execute("INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)", ("author", "John Doe"))
    cursor.execute("INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)", ("description", ""))

    # Expense-specific schema
    # 1) members
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2) expenses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount_cents INTEGER NOT NULL CHECK(amount_cents > 0),
            payer_id INTEGER NOT NULL REFERENCES members(id) ON DELETE RESTRICT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3) expense_participants
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expense_participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_id INTEGER NOT NULL REFERENCES expenses(id) ON DELETE CASCADE,
            member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE RESTRICT,
            share_cents INTEGER NOT NULL CHECK(share_cents >= 0),
            UNIQUE(expense_id, member_id)
        )
    """)

    # Indexes (CREATE IF NOT EXISTS supported in SQLite 3.8.0+)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_payer_id ON expenses(payer_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_exp_part_expense_id ON expense_participants(expense_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_exp_part_member_id ON expense_participants(member_id)")

    # Balances view: compute credits and debits per member, net = credits - debits
    # Use CREATE VIEW and drop existing if present to emulate create or replace behavior idempotently
    cursor.execute("DROP VIEW IF EXISTS balances_view")
    cursor.execute("""
        CREATE VIEW balances_view AS
        WITH
        credits AS (
            SELECT m.id AS member_id, IFNULL(SUM(e.amount_cents), 0) AS credits_cents
            FROM members m
            LEFT JOIN expenses e ON e.payer_id = m.id
            GROUP BY m.id
        ),
        debits AS (
            SELECT m.id AS member_id, IFNULL(SUM(ep.share_cents), 0) AS debits_cents
            FROM members m
            LEFT JOIN expense_participants ep ON ep.member_id = m.id
            GROUP BY m.id
        )
        SELECT
            m.id AS member_id,
            m.name AS name,
            CAST(IFNULL(c.credits_cents, 0) - IFNULL(d.debits_cents, 0) AS INTEGER) AS net_cents
        FROM members m
        LEFT JOIN credits c ON c.member_id = m.id
        LEFT JOIN debits d ON d.member_id = m.id
    """)

    # Commit all schema changes
    conn.commit()

    # Gather statistics for output
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    table_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM app_info")
    record_count = cursor.fetchone()[0]

# Save connection information to a file
current_dir = os.getcwd()
connection_string = f"sqlite:///{current_dir}/{DB_NAME}"

try:
    with open("db_connection.txt", "w") as f:
        f.write(f"# SQLite connection methods:\n")
        f.write(f"# Python: sqlite3.connect('{DB_NAME}')\n")
        f.write(f"# Connection string: {connection_string}\n")
        f.write(f"# File path: {current_dir}/{DB_NAME}\n")
    print("Connection information saved to db_connection.txt")
except Exception as e:
    print(f"Warning: Could not save connection info: {e}")

# Create environment variables file for Node.js viewer
db_path = os.path.abspath(DB_NAME)

# Ensure db_visualizer directory exists
if not os.path.exists("db_visualizer"):
    os.makedirs("db_visualizer", exist_ok=True)
    print("Created db_visualizer directory")

try:
    with open("db_visualizer/sqlite.env", "w") as f:
        f.write(f"export SQLITE_DB=\"{db_path}\"\n")
    print(f"Environment variables saved to db_visualizer/sqlite.env")
except Exception as e:
    print(f"Warning: Could not save environment variables: {e}")

print("\nSQLite setup complete!")
print(f"Database: {DB_NAME}")
print(f"Location: {current_dir}/{DB_NAME}")
print("")

print("To use with Node.js viewer, run: source db_visualizer/sqlite.env")

print("\nTo connect to the database, use one of the following methods:")
print(f"1. Python: sqlite3.connect('{DB_NAME}')")
print(f"2. Connection string: {connection_string}")
print(f"3. Direct file access: {current_dir}/{DB_NAME}")
print("")

print("Database statistics:")
print(f"  Tables: {table_count}")
print(f"  App info records: {record_count}")

# If sqlite3 CLI is available, show how to use it
try:
    import subprocess
    result = subprocess.run(['which', 'sqlite3'], capture_output=True, text=True)
    if result.returncode == 0:
        print("")
        print("SQLite CLI is available. You can also use:")
        print(f"  sqlite3 {DB_NAME}")
except Exception:
    # Avoid crashing on environments without sqlite3 client
    pass

# Exit successfully
print("\nScript completed successfully.")
