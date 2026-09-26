from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
from typing import Any, Callable

RULES={"api_pass_rate":(">=","pass_rate"),"avg_response_ms":("<=","average_ms"),"p95_ms":("<=","p95_ms"),"p99_ms":("<=","p99_ms"),"error_rate":("<=","error_rate")}
@dataclass(frozen=True)
class GateResult:
    name:str; passed:bool; actual:float; limit:float; operator:str
    @property
    def margin(self)->float:return self.actual-self.limit if self.operator==">=" else self.limit-self.actual
def validate_thresholds(values:dict[str,str|float])->dict[str,float]:
    parsed={name:float(value) for name,value in values.items()}
    if any(not isfinite(value) or value<0 for value in parsed.values()):raise ValueError("Each release rule must be a finite non-negative number.")
    return parsed
def metrics_for_load(metric:dict[str,Any])->dict[str,float]:return {**metric,"pass_rate":100-float(metric.get("error_rate",0))}
def latest_compatible_run(runs:list[dict[str,Any]],metrics_for_run:Callable[[int],list[dict[str,Any]]],thresholds:dict[str,float]):
    required={RULES[name][1] for name in thresholds if name in RULES}
    for run in reversed(runs):
        metrics=metrics_for_run(run["id"])
        if not metrics:continue
        values=metrics_for_load(metrics[0])
        if required <= values.keys():return run,values
    return None,None

def latest_release_evidence(runs:list[dict[str,Any]],metrics_for_run:Callable[[int],list[dict[str,Any]]]):
    """Return the newest independent API and load evidence for release rules.

    API and load checks are saved as separate runs.  A release decision therefore
    combines the newest completed API summary with the newest saved load metrics,
    instead of incorrectly treating a load run as an API test run.
    """
    api_run = None
    load_run = None
    for run in reversed(runs):
        summary = run.get("summary_json") or {}
        if api_run is None and summary.get("total") is not None:
            total = float(summary.get("total") or 0)
            if total > 0:
                api_run = run
        if load_run is None:
            metrics = metrics_for_run(run["id"])
            if metrics:
                load_run = run
                load_values = metrics_for_load(metrics[0])
        if api_run and load_run:
            break
    if not api_run or not load_run:
        return api_run, load_run, None
    summary = api_run.get("summary_json") or {}
    # Skipped checks did not make a request and are neither passes nor
    # failures. New runs also persist gate_* counts that omit tagged fixtures.
    passed = float(summary.get("gate_passed", summary.get("passed", 0)))
    executed = float(summary.get("gate_executed", passed + float(summary.get("failed", 0))))
    return api_run, load_run, {
        **load_values,
        "pass_rate": round(passed / executed * 100, 1) if executed else 0,
    }
def evaluate(metrics:dict[str,Any],thresholds:dict[str,float])->list[GateResult]:
    items=[]
    for name,limit in thresholds.items():
        if name not in RULES:continue
        operator,key=RULES[name];actual=float(metrics.get(key,0));items.append(GateResult(name,actual>=limit if operator==">=" else actual<=limit,actual,limit,operator))
    return items
