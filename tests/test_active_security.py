from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from security.scanner import active_scan

class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  value=self.path.split("q=")[-1] if "q=" in self.path else "baseline"
  self.send_response(200);self.send_header("Content-Type","text/html");self.end_headers();self.wfile.write(f"<html>{value}</html>".encode())
 def log_message(self,*_):pass

def test_active_scan_creates_only_html_reflection_candidate():
 server=HTTPServer(("127.0.0.1",0),Handler);Thread(target=server.serve_forever,daemon=True).start()
 try:
  base=f"http://127.0.0.1:{server.server_port}";endpoints=[{"method":"GET","path":"/search","definition_json":{"parameters":[{"name":"q","in":"query","schema":{"type":"string"}}]}}]
  findings,requests=active_scan(base,endpoints)
  assert requests==3 and len(findings)==1 and findings[0].details["cwe"]=="CWE-79"
 finally:server.shutdown()

def test_active_scan_ignores_non_get_and_non_query_parameters():
 findings,requests=active_scan("http://127.0.0.1:1",[{"method":"POST","path":"/x","definition_json":{"parameters":[{"name":"q","in":"query","schema":{"type":"string"}}]}}])
 assert findings==[] and requests==0

def test_active_scan_blocks_production_at_runner_boundary():
 findings,requests=active_scan("http://127.0.0.1:1",[],environment="Production")
 assert findings==[] and requests==0
