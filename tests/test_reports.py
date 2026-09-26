from reports.generator import build_report,export
def test_report_exports_json_and_html(tmp_path):
 report=build_report({"name":"Demo"},{"id":7,"status":"COMPLETED"},[{"name":"GET /","status":"PASSED","duration_ms":10}],[],[])
 json_path,html_path=export(report,tmp_path);assert json_path.exists() and html_path.exists() and 'GET /' in html_path.read_text()
