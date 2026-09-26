from __future__ import annotations
from database.repositories import LoadMetricsRepository,TestRunsRepository
from datetime import datetime, timezone
from runners.load_runner import run_load
from core.gates import evaluate
def run_and_store_load(project_id:int,url:str,runs:TestRunsRepository,metrics:LoadMetricsRepository,users:int,requests:int):
    run=runs.create(project_id,status="RUNNING",started_at=datetime.now(timezone.utc).isoformat());summary=run_load(url,users,requests);metrics.create(run["id"],users=users,requests=summary.requests,successes=summary.successes,failures=summary.failures,rps=summary.rps,average_ms=summary.average_ms,p50_ms=summary.p50_ms,p95_ms=summary.p95_ms,p99_ms=summary.p99_ms,error_rate=summary.error_rate);runs.update(run["id"],status="COMPLETED",finished_at=datetime.now(timezone.utc).isoformat(),summary_json=vars(summary));return runs.get(run["id"]),summary
def evaluate_and_store(run_id:int,runs:TestRunsRepository,summary:dict,thresholds:dict):
    metrics={**summary,"pass_rate":100-summary.get("error_rate",0)};gates=evaluate(metrics,thresholds);runs.update(run_id,gate_status="PASSED" if all(item.passed for item in gates) else "FAILED");return gates
