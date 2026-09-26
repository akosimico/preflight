"""Repositories keep SQL outside UI and runner code."""
from __future__ import annotations
import json
from typing import Any
from database.database import Database

class Repository:
    table: str; columns: frozenset[str]
    def __init__(self, database: Database) -> None: self.database = database; database.initialize()
    def get(self, record_id: int) -> dict[str, Any] | None:
        with self.database.connection() as c: row = c.execute(f"SELECT * FROM {self.table} WHERE id=?", (record_id,)).fetchone()
        return self._row(row)
    def list(self, **filters: Any) -> list[dict[str, Any]]:
        self._validate(filters); where = "" if not filters else " WHERE " + " AND ".join(f"{k}=?" for k in filters)
        with self.database.connection() as c: rows = c.execute(f"SELECT * FROM {self.table}{where} ORDER BY id", tuple(filters.values())).fetchall()
        return [self._row(row) for row in rows]
    def delete(self, record_id: int) -> bool:
        with self.database.connection() as c: return c.execute(f"DELETE FROM {self.table} WHERE id=?", (record_id,)).rowcount == 1
    def update(self, record_id: int, **values: Any) -> dict[str, Any] | None:
        self._validate(values)
        if not values: return self.get(record_id)
        assignments = ", ".join(f"{k}=?" for k in values)
        if "updated_at" in self.columns: assignments += ", updated_at=CURRENT_TIMESTAMP"
        with self.database.connection() as c: c.execute(f"UPDATE {self.table} SET {assignments} WHERE id=?", (*self._encode(values).values(), record_id))
        return self.get(record_id)
    def _insert(self, **values: Any) -> dict[str, Any]:
        self._validate(values); values = self._encode(values); keys = ", ".join(values); marks = ", ".join("?" for _ in values)
        with self.database.connection() as c: record_id = c.execute(f"INSERT INTO {self.table} ({keys}) VALUES ({marks})", tuple(values.values())).lastrowid
        result = self.get(record_id); assert result is not None; return result
    def _validate(self, values: dict[str, Any]) -> None:
        unknown = set(values) - self.columns
        if unknown: raise ValueError(f"Unsupported {self.table} columns: {', '.join(sorted(unknown))}")
    @staticmethod
    def _encode(values: dict[str, Any]) -> dict[str, Any]: return {k: json.dumps(v) if k.endswith("_json") and not isinstance(v, str) else int(v) if isinstance(v, bool) else v for k, v in values.items()}
    @staticmethod
    def _row(row: Any) -> dict[str, Any] | None:
        if row is None: return None
        data = dict(row)
        for key, value in data.items():
            if key.endswith("_json") and isinstance(value, str): data[key] = json.loads(value)
            elif key in {"enabled", "is_destructive"}: data[key] = bool(value)
        return data

class ProjectsRepository(Repository):
    table="projects"; columns=frozenset({"name","frontend_url","api_url","environment","updated_at"})
    def create(self, name: str, frontend_url: str="", api_url: str="", environment: str="Local") -> dict[str, Any]: return self._insert(name=name, frontend_url=frontend_url, api_url=api_url, environment=environment)
class EndpointsRepository(Repository):
    table="endpoints"; columns=frozenset({"project_id","method","path","enabled","is_destructive","definition_json","updated_at"})
    def create(self, project_id: int, method: str, path: str, **values: Any) -> dict[str, Any]: return self._insert(project_id=project_id, method=method.upper(), path=path, **values)
class ScenariosRepository(Repository):
    table="scenarios"; columns=frozenset({"project_id","name","enabled","steps_json","updated_at"})
    def create(self, project_id: int, name: str, steps_json: list[Any] | None=None) -> dict[str, Any]: return self._insert(project_id=project_id, name=name, steps_json=steps_json or [])
class TestRunsRepository(Repository):
    __test__ = False
    table="test_runs"; columns=frozenset({"project_id","status","gate_status","started_at","finished_at","duration_ms","summary_json"})
    def create(self, project_id: int, status: str="PENDING", **values: Any) -> dict[str, Any]: return self._insert(project_id=project_id, status=status, **values)
class TestResultsRepository(Repository):
    __test__ = False
    table="test_results"; columns=frozenset({"test_run_id","endpoint_id","suite","name","status","duration_ms","details_json"})
    def create(self, test_run_id: int, name: str, status: str, **values: Any) -> dict[str, Any]: return self._insert(test_run_id=test_run_id, name=name, status=status, **values)
class LoadMetricsRepository(Repository):
    table="load_metrics"; columns=frozenset({"test_run_id","recorded_at","users","requests","successes","failures","rps","average_ms","p50_ms","p95_ms","p99_ms","error_rate"})
    def create(self, test_run_id: int, **values: Any) -> dict[str, Any]: return self._insert(test_run_id=test_run_id, **values)
class SecurityFindingsRepository(Repository):
    table="security_findings"; columns=frozenset({"test_run_id","severity","title","target","details_json"})
    def create(self, test_run_id: int, severity: str, title: str, **values: Any) -> dict[str, Any]: return self._insert(test_run_id=test_run_id, severity=severity, title=title, **values)
class SettingsRepository:
    def __init__(self, database: Database) -> None: self.database=database; database.initialize()
    def get(self, key: str, default: Any=None) -> Any:
        with self.database.connection() as c: row=c.execute("SELECT value_json FROM settings WHERE key=?", (key,)).fetchone()
        return default if row is None else json.loads(row["value_json"])
    def set(self, key: str, value: Any) -> None:
        with self.database.connection() as c: c.execute("INSERT INTO settings(key,value_json) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json,updated_at=CURRENT_TIMESTAMP", (key,json.dumps(value)))
    def delete(self, key: str) -> bool:
        with self.database.connection() as c: return c.execute("DELETE FROM settings WHERE key=?", (key,)).rowcount == 1
