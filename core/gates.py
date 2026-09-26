from dataclasses import dataclass
from typing import Any
@dataclass(frozen=True)
class GateResult: name:str; passed:bool; actual:float; limit:float
def evaluate(metrics:dict[str,Any],thresholds:dict[str,float])->list[GateResult]:
    rules={"api_pass_rate":(">=","pass_rate"),"avg_response_ms":("<=","average_ms"),"p95_ms":("<=","p95_ms"),"p99_ms":("<=","p99_ms"),"error_rate":("<=","error_rate")}
    return [GateResult(name,(metrics.get(key,0)>=limit if op==">=" else metrics.get(key,0)<=limit),metrics.get(key,0),limit) for name,limit in thresholds.items() if name in rules for op,key in [rules[name]]]
