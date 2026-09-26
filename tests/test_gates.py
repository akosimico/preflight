from core.gates import evaluate
def test_gates_evaluate_limits():
 results=evaluate({"pass_rate":99,"average_ms":120,"p95_ms":400,"p99_ms":500,"error_rate":1},{"api_pass_rate":98,"avg_response_ms":100,"p95_ms":450,"p99_ms":500,"error_rate":2})
 assert [item.passed for item in results]==[True,False,True,True,True]
