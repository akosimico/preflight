"""Pure helpers that turn stored run records into dashboard chart series."""
from __future__ import annotations
from typing import Any

def recent_series(runs: list[dict[str, Any]], metrics_for_run, limit: int = 10) -> dict[str, list[dict[str, Any]]]:
    api, load, security = [], [], []
    for run in reversed(runs):
        summary = run.get("summary_json", {})
        metric = metrics_for_run(run["id"])
        label = run.get("created_at", "")
        if "total" in summary and len(api) < limit:
            total = summary.get("total", 0); api.append({"run_id": run["id"], "label": label, "value": round(summary.get("passed", 0) / total * 100, 1) if total else 0})
        if metric and len(load) < limit:
            item = metric[0]; load.append({"run_id": run["id"], "label": label, "average": item.get("average_ms") or 0, "p95": item.get("p95_ms") or 0, "success_rate": round(100 - (item.get("error_rate") or 0), 1)})
        if summary.get("security_check") and len(security) < limit: security.append({"run_id": run["id"], "label": label, "findings": summary.get("findings", 0)})
    return {"api": list(reversed(api)), "load": list(reversed(load)), "security": list(reversed(security))}
