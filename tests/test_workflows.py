from http.server import BaseHTTPRequestHandler,HTTPServer
from threading import Thread
from database.database import Database
from database.repositories import LoadMetricsRepository,ProjectsRepository,TestRunsRepository
from core.workflows import run_and_store_load,evaluate_and_store
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):self.send_response(200);self.end_headers()
 def log_message(self,*_):pass
def test_load_workflow_persists_metrics_and_gate(tmp_path):
 server=HTTPServer(("127.0.0.1",0),Handler);Thread(target=server.serve_forever,daemon=True).start()
 try:
  db=Database(tmp_path/"x.db");project=ProjectsRepository(db).create("D");runs=TestRunsRepository(db);metrics=LoadMetricsRepository(db);run,summary=run_and_store_load(project["id"],f"http://127.0.0.1:{server.server_port}",runs,metrics,1,2);assert metrics.list(test_run_id=run["id"])[0]["requests"]==2;assert evaluate_and_store(run["id"],runs,vars(summary),{"error_rate":100})[0].passed
 finally:server.shutdown()
