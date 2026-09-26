from http.server import BaseHTTPRequestHandler,HTTPServer
from threading import Thread
from core.parameters import baseline_body
from runners.api_runner import expected_success_status,redact,run_request
class Handler(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.send_header("content-type","application/json"); self.end_headers(); self.wfile.write(b'{"ok":true}')
    def log_message(self,*_): pass
def test_api_runner_supports_status_and_json_assertions():
    server=HTTPServer(("127.0.0.1",0),Handler); Thread(target=server.serve_forever,daemon=True).start()
    try:
        result=run_request("GET",f"http://127.0.0.1:{server.server_port}",assertions={"json.ok":True,"max_response_ms":5000})
        assert result.passed and result.status_code==200
    finally: server.shutdown()

def test_openapi_status_and_secrets_are_handled_safely():
    assert expected_success_status({"responses":{"201":{}}})==201
    assert redact({"Authorization":"abc","nested":{"token":"x"}})=={"Authorization":"[REDACTED]","nested":{"token":"[REDACTED]"}}

def test_baseline_body_uses_openapi_schema_values():
    definition={"requestBody":{"content":{"application/json":{"schema":{"type":"object","properties":{"title":{"type":"string"},"completed":{"type":"boolean","default":False}}}}}}}
    assert baseline_body(definition)=={"title":"preflight-test","completed":False}
