from __future__ import annotations
import customtkinter as ctk
from core.history import runs_for_project
from core.projects import ProjectService
from core.timezone import format_pht
from database.repositories import LoadMetricsRepository, SecurityFindingsRepository, TestResultsRepository, TestRunsRepository
from gui.components.expandable_result import ExpandableResult
from gui.theme import MUTED

class HistoryView(ctk.CTkFrame):
 def __init__(self,master,projects:ProjectService,runs:TestRunsRepository,results:TestResultsRepository,metrics:LoadMetricsRepository,findings:SecurityFindingsRepository):
  super().__init__(master,fg_color="transparent");self.projects,self.runs,self.results,self.metrics,self.findings=projects,runs,results,metrics,findings
  ctk.CTkLabel(self,text="Run History",font=ctk.CTkFont(size=30,weight="bold")).pack(anchor="w",padx=28,pady=(30,4));ctk.CTkLabel(self,text="Open a run to inspect the saved API, load, or security evidence. Times use Philippine Time (PHT).",text_color=MUTED).pack(anchor="w",padx=28);ctk.CTkButton(self,text="REFRESH",command=self.refresh).pack(anchor="w",padx=28,pady=(10,8));self.rows=ctk.CTkScrollableFrame(self);self.rows.pack(fill="both",expand=True,padx=28,pady=(0,28));self.refresh()
 def refresh(self):
  for child in self.rows.winfo_children():child.destroy()
  project=self.projects.active();history=runs_for_project(self.runs,project["id"]) if project else []
  if not history:ctk.CTkLabel(self.rows,text="No runs recorded for the active project.").pack(pady=20)
  for run in history:self.add_run(run)
 def add_run(self,run):
  summary=run.get("summary_json",{});kind="Security" if summary.get("security_check") else "API" if "total" in summary else "Load" if self.metrics.list(test_run_id=run["id"]) else "Run"
  card=ctk.CTkFrame(self.rows,corner_radius=10);card.pack(fill="x",padx=5,pady=5);header=ctk.CTkButton(card,text=f"Run #{run['id']} · {kind} · {run['status']}    View details ›",anchor="w",fg_color="transparent",command=lambda r=run,c=card:self.toggle(r,c));header.pack(fill="x",padx=5,pady=4);ctk.CTkLabel(card,text=f"Created {format_pht(run.get('created_at'))} · Gate: {run.get('gate_status') or 'Not evaluated'}",text_color=MUTED,anchor="w").pack(fill="x",padx=14,pady=(0,8))
 def toggle(self,run,card):
  existing=getattr(card,"details_frame",None)
  if existing and existing.winfo_manager():existing.pack_forget();return
  if not existing:card.details_frame=ctk.CTkFrame(card,fg_color="transparent");existing=card.details_frame;self.populate(run,existing)
  existing.pack(fill="x",padx=8,pady=(0,8))
 def populate(self,run,frame):
  results=self.results.list(test_run_id=run["id"])
  if results:
   for item in results:
    detail=item.get("details_json",{});ExpandableResult(frame,item["name"],item["status"],f"{item.get('duration_ms') or '—'} ms",[("HTTP status",detail.get("status_code")),("Duration",f"{item.get('duration_ms') or 'Not recorded'} ms"),("Error / reason",detail.get("error"))],detail.get("response")).pack(fill="x",pady=2)
   return
  metrics=self.metrics.list(test_run_id=run["id"])
  if metrics:
   item=metrics[0];ExpandableResult(frame,"Load-test summary","FAILED" if item["error_rate"] else "PASSED",f"P95 {item.get('p95_ms')} ms",[("Virtual users",item["users"]),("Requests",item["requests"]),("Successful",item["successes"]),("Failed",item["failures"]),("RPS",item["rps"]),("Average",f"{item.get('average_ms')} ms"),("P95",f"{item.get('p95_ms')} ms"),("P99",f"{item.get('p99_ms')} ms"),("Error rate",f"{item['error_rate']}%")]).pack(fill="x");return
  findings=self.findings.list(test_run_id=run["id"])
  for item in findings:
   detail=item.get("details_json",{});ExpandableResult(frame,item["title"],item["severity"],"View finding",[("Target",item["target"]),("Response status",detail.get("status_code")),("Why this matters",detail.get("detail"))]).pack(fill="x",pady=2)
  if not findings:ctk.CTkLabel(frame,text="No detailed records are available for this older run.",text_color=MUTED).pack(anchor="w",padx=10,pady=8)
