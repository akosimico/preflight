from http.server import BaseHTTPRequestHandler,HTTPServer
from threading import Thread
from runners.load_runner import run_load
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):self.send_response(200);self.end_headers()
 def log_message(self,*_):pass
def test_load_runner_calculates_metrics():
 server=HTTPServer(("127.0.0.1",0),Handler);Thread(target=server.serve_forever,daemon=True).start()
 try:
  result=run_load(f"http://127.0.0.1:{server.server_port}",users=2,requests=4);assert result.requests==4 and result.successes==4 and result.error_rate==0
 finally:server.shutdown()
