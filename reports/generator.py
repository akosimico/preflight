from __future__ import annotations
import json
from html import escape
from pathlib import Path
from typing import Any
def build_report(project:dict[str,Any],run:dict[str,Any],results:list[dict[str,Any]],metrics:list[dict[str,Any]],gates:list[Any],security_findings:list[dict[str,Any]]|None=None)->dict[str,Any]:
    return {"project":project,"run":run,"api_results":results,"load_metrics":metrics,"security_findings":security_findings or [],"gates":[vars(gate) if hasattr(gate,"__dict__") else gate for gate in gates]}
def export(report:dict[str,Any],directory:str|Path="storage/reports")->tuple[Path,Path]:
    target=Path(directory);target.mkdir(parents=True,exist_ok=True);stem=f"run-{report['run']['id']}";json_path=target/f"{stem}.json";html_path=target/f"{stem}.html";json_path.write_text(json.dumps(report,indent=2,default=str),encoding="utf-8")
    rows="".join(f"<tr><td>{escape(str(item['name']))}</td><td>{escape(str(item['status']))}</td><td>{item.get('duration_ms') or ''}</td></tr>" for item in report["api_results"]);html_path.write_text(f"<!doctype html><title>Preflight report</title><h1>Preflight: {escape(report['project']['name'])}</h1><p>Run {report['run']['id']} — {escape(report['run']['status'])}</p><table border=1><tr><th>Test</th><th>Status</th><th>ms</th></tr>{rows}</table>",encoding="utf-8");return json_path,html_path
