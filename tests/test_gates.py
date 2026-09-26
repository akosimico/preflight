import pytest
from core.gates import evaluate, latest_compatible_run, latest_release_evidence, validate_thresholds
def test_gates_evaluate_limits():
 results=evaluate({"pass_rate":99,"average_ms":120,"p95_ms":400,"p99_ms":500,"error_rate":1},{"api_pass_rate":98,"avg_response_ms":100,"p95_ms":450,"p99_ms":500,"error_rate":2})
 assert [item.passed for item in results]==[True,False,True,True,True]

def test_latest_compatible_run_skips_security_only_runs():
 runs=[{"id":1,"summary_json":{}},{"id":2,"summary_json":{"security_check":True}}]
 metric={1:[{"average_ms":100,"p95_ms":120,"p99_ms":150,"error_rate":1}]}
 run,values=latest_compatible_run(runs,lambda run_id:metric.get(run_id,[]),{"avg_response_ms":500,"api_pass_rate":95})
 assert run["id"]==1 and values["pass_rate"]==99

def test_threshold_validation_and_margins():
 with pytest.raises(ValueError):validate_thresholds({"error_rate":"-1"})
 item=evaluate({"pass_rate":97},{"api_pass_rate":95})[0]
 assert item.margin==2


def test_latest_release_evidence_combines_newest_api_and_load_runs():
 runs=[
  {"id":48,"summary_json":{"requests":20}},
  {"id":54,"summary_json":{"passed":8,"failed":2,"total":10}},
 ]
 metric={48:[{"average_ms":120,"p95_ms":200,"p99_ms":250,"error_rate":1}]}
 api_run,load_run,values=latest_release_evidence(runs,lambda run_id:metric.get(run_id,[]))
 assert api_run["id"]==54
 assert load_run["id"]==48
 assert values["pass_rate"]==80
 assert values["average_ms"]==120

def test_release_pass_rate_excludes_skips_and_uses_gate_counts():
 runs=[
  {"id":1,"summary_json":{"passed":7,"failed":2,"skipped":3,"total":12}},
  {"id":2,"summary_json":{"requests":20}},
 ]
 metric={2:[{"average_ms":120,"p95_ms":200,"p99_ms":250,"error_rate":1}]}
 _,_,values=latest_release_evidence(runs,lambda run_id:metric.get(run_id,[]))
 assert values["pass_rate"]==77.8

 runs[0]["summary_json"].update({"gate_passed":4,"gate_failed":0,"gate_executed":4})
 _,_,values=latest_release_evidence(runs,lambda run_id:metric.get(run_id,[]))
 assert values["pass_rate"]==100
