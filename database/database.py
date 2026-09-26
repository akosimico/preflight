"""SQLite lifecycle and schema migrations."""
from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path
import sqlite3
from collections.abc import Iterator

DEFAULT_DATABASE_PATH = Path("storage") / "preflight.db"
SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY, name TEXT NOT NULL, frontend_url TEXT NOT NULL DEFAULT '', api_url TEXT NOT NULL DEFAULT '', environment TEXT NOT NULL DEFAULT 'Local', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS endpoints (id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE, method TEXT NOT NULL, path TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1, is_destructive INTEGER NOT NULL DEFAULT 0, definition_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(project_id, method, path));
CREATE TABLE IF NOT EXISTS scenarios (id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE, name TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1, steps_json TEXT NOT NULL DEFAULT '[]', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS test_runs (id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE, status TEXT NOT NULL DEFAULT 'PENDING', gate_status TEXT, started_at TEXT, finished_at TEXT, duration_ms REAL, summary_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS test_results (id INTEGER PRIMARY KEY, test_run_id INTEGER NOT NULL REFERENCES test_runs(id) ON DELETE CASCADE, endpoint_id INTEGER REFERENCES endpoints(id) ON DELETE SET NULL, suite TEXT NOT NULL DEFAULT 'api', name TEXT NOT NULL, status TEXT NOT NULL, duration_ms REAL, details_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS load_metrics (id INTEGER PRIMARY KEY, test_run_id INTEGER NOT NULL REFERENCES test_runs(id) ON DELETE CASCADE, recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, users INTEGER NOT NULL DEFAULT 0, requests INTEGER NOT NULL DEFAULT 0, successes INTEGER NOT NULL DEFAULT 0, failures INTEGER NOT NULL DEFAULT 0, rps REAL NOT NULL DEFAULT 0, average_ms REAL, p50_ms REAL, p95_ms REAL, p99_ms REAL, error_rate REAL NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS security_findings (id INTEGER PRIMARY KEY, test_run_id INTEGER NOT NULL REFERENCES test_runs(id) ON DELETE CASCADE, severity TEXT NOT NULL, title TEXT NOT NULL, target TEXT NOT NULL DEFAULT '', details_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value_json TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_endpoints_project ON endpoints(project_id); CREATE INDEX IF NOT EXISTS idx_runs_project ON test_runs(project_id, created_at DESC); CREATE INDEX IF NOT EXISTS idx_results_run ON test_results(test_run_id);
"""

class Database:
    def __init__(self, path: str | Path = DEFAULT_DATABASE_PATH) -> None: self.path = Path(path)
    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as conn:
            if conn.execute("PRAGMA user_version").fetchone()[0] < 1:
                conn.executescript(SCHEMA); conn.execute("PRAGMA user_version = 1")
    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path); conn.row_factory = sqlite3.Row; conn.execute("PRAGMA foreign_keys = ON")
        try: yield conn; conn.commit()
        except Exception: conn.rollback(); raise
        finally: conn.close()
