from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from core.connections import check_target

class Handler(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(204); self.end_headers()
    def log_message(self, *_): pass

def test_connection_check_reports_status_and_timing():
    server=HTTPServer(("127.0.0.1",0),Handler); Thread(target=server.serve_forever,daemon=True).start()
    try:
        result=check_target(f"http://127.0.0.1:{server.server_port}")
        assert result.reachable and result.status_code==204 and result.elapsed_ms is not None
    finally: server.shutdown()

def test_connection_check_explains_missing_url():
    result=check_target("")
    assert not result.reachable and "No URL" in result.message
