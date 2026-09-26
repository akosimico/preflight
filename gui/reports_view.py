from __future__ import annotations
import customtkinter as ctk
from core.projects import ProjectService
from core.timezone import format_pht
from database.repositories import LoadMetricsRepository, SecurityFindingsRepository, TestResultsRepository, TestRunsRepository
from reports.generator import build_report, export

class ReportsView(ctk.CTkFrame):
 def __init__(self,master,projects:ProjectService,runs:TestRunsRepository,results:TestResultsRepository,metrics:LoadMetricsRepository,findings:SecurityFindingsRepository):
  super().__init__(master,fg_color="transparent");self.projects,self.runs,self.results,self.metrics,self.findings=projects,runs,results,metrics,findings;self.choices={};ctk.CTkLabel(self,text="Reports",font=ctk.CTkFont(size=30,weight="bold")).pack(anchor="w",padx=28,pady=(30,8));self.menu=ctk.CTkOptionMenu(self,values=["No saved runs"],width=500);self.menu.pack(anchor="w",padx=28);actions=ctk.CTkFrame(self,fg_color="transparent");actions.pack(anchor="w",padx=28,pady=12);ctk.CTkButton(actions,text="VIEW SELECTED REPORT",command=self.view).pack(side="left",padx=(0,8));ctk.CTkButton(actions,text="EXPORT SELECTED REPORT",command=self.export).pack(side="left");self.status=ctk.CTkLabel(self,text="Choose a saved run to review or export.");self.status.pack(anchor="w",padx=28);self.body=ctk.CTkScrollableFrame(self,label_text="Report preview");self.body.pack(fill="both",expand=True,padx=28,pady=14);self.refresh()
 def refresh(self):
  project=self.projects.active();history=self.runs.list(project_id=project["id"]) if project else [];self.choices={}
  choices=[]
  for run in reversed(history):
   s=run.get("summary_json",{});kind="Security scan" if s.get("security_check") else "API test" if self.results.list(test_run_id=run["id"]) else "Load test";label=f"Run #{run['id']} · {kind} · {format_pht(run.get('created_at'))}";choices.append(label);self.choices[label]=run["id"]
  self.menu.configure(values=choices or ["No saved runs"]);self.menu.set(choices[0] if choices else "No saved runs")
 def report(self):
  project=self.projects.active();run_id=self.choices.get(self.menu.get());run=self.runs.get(run_id) if run_id else None
  return build_report(project,run,self.results.list(test_run_id=run_id),self.metrics.list(test_run_id=run_id),[],self.findings.list(test_run_id=run_id)) if project and run else None
 def view(self):
  report=self.report()
  if not report:self.status.configure(text="Choose a saved run first.");return
  self.show(report)
 def export(self):
  report=self.report()
  if not report:self.status.configure(text="Choose a saved run first.");return
  paths=export(report);self.status.configure(text=f"Saved report: {paths[1]}");self.show(report)
 def show(self,report):
  for child in self.body.winfo_children():child.destroy()
  run=report["run"];ctk.CTkLabel(self.body,text=f"Run #{run['id']} · {run['status']}",font=ctk.CTkFont(size=20,weight="bold")).pack(anchor="w",padx=10,pady=10)
  for heading,key in (("API results","api_results"),("Load metrics","load_metrics"),("Security findings","security_findings")):
   items=report[key]
   if not items:continue
   ctk.CTkLabel(self.body,text=heading,font=ctk.CTkFont(weight="bold")).pack(anchor="w",padx=10,pady=(10,4))
   for item in items:ctk.CTkLabel(self.body,text=str(item.get("title") or item.get("name") or item),anchor="w",wraplength=850).pack(fill="x",padx=10)
