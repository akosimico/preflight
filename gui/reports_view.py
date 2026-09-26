from __future__ import annotations
import customtkinter as ctk
from core.projects import ProjectService
from database.repositories import LoadMetricsRepository,TestResultsRepository,TestRunsRepository
from reports.generator import build_report,export
class ReportsView(ctk.CTkFrame):
 def __init__(self,master,projects:ProjectService,runs:TestRunsRepository,results:TestResultsRepository,metrics:LoadMetricsRepository):
  super().__init__(master,fg_color="transparent");self.projects=projects;self.runs=runs;self.results=results;self.metrics=metrics;ctk.CTkLabel(self,text="Reports",font=ctk.CTkFont(size=30,weight="bold")).pack(anchor="w",padx=28,pady=(30,8));ctk.CTkButton(self,text="EXPORT LATEST REPORT",command=self.generate).pack(anchor="w",padx=28);self.status=ctk.CTkLabel(self,text="Exports JSON and HTML to storage/reports.",wraplength=700,justify="left");self.status.pack(anchor="w",padx=28,pady=16)
 def generate(self):
  project=self.projects.active()
  if not project:self.status.configure(text="Select an active project first.");return
  history=self.runs.list(project_id=project["id"])
  if not history:self.status.configure(text="Run a test first.");return
  run=history[-1];report=build_report(project,run,self.results.list(test_run_id=run["id"]),self.metrics.list(test_run_id=run["id"]),[]);paths=export(report);self.status.configure(text=f"Saved report:\n{paths[0]}\n{paths[1]}")
