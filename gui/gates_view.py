from __future__ import annotations
import customtkinter as ctk
from core.gates import evaluate
from core.projects import ProjectService
from database.repositories import SettingsRepository,TestRunsRepository
class GatesView(ctk.CTkFrame):
 def __init__(self,master,projects:ProjectService,runs:TestRunsRepository,settings:SettingsRepository):
  super().__init__(master,fg_color="transparent");self.projects=projects;self.runs=runs;self.settings=settings;ctk.CTkLabel(self,text="Deployment Gates",font=ctk.CTkFont(size=30,weight="bold")).pack(anchor="w",padx=28,pady=(30,8));self.entries={};form=ctk.CTkFrame(self);form.pack(fill="x",padx=28);defaults={"api_pass_rate":95,"avg_response_ms":500,"p95_ms":800,"p99_ms":1200,"error_rate":2}
  saved=settings.get("gate_thresholds",defaults)
  for name,value in saved.items():
   row=ctk.CTkFrame(form,fg_color="transparent");row.pack(fill="x",padx=8,pady=4);ctk.CTkLabel(row,text=name.replace("_"," ").title(),width=180,anchor="w").pack(side="left");entry=ctk.CTkEntry(row);entry.insert(0,str(value));entry.pack(side="left",fill="x",expand=True);self.entries[name]=entry
  ctk.CTkButton(form,text="SAVE & EVALUATE LATEST RUN",command=self.evaluate).pack(padx=8,pady=10);self.result=ctk.CTkTextbox(self,height=260,state="disabled");self.result.pack(fill="both",expand=True,padx=28,pady=16)
 def evaluate(self):
  project=self.projects.active()
  if not project:return
  thresholds={name:float(entry.get()) for name,entry in self.entries.items()};self.settings.set("gate_thresholds",thresholds);runs=self.runs.list(project_id=project["id"])
  if not runs:self.show("No completed runs.");return
  summary=runs[-1]["summary_json"];metrics={**summary,"pass_rate":100-summary.get("error_rate",0)};items=evaluate(metrics,thresholds);self.runs.update(runs[-1]["id"],gate_status="PASSED" if all(item.passed for item in items) else "FAILED");self.show("\n".join(f"{'PASS' if item.passed else 'FAIL'}  {item.name}: {item.actual} (limit {item.limit})" for item in items))
 def show(self,text):self.result.configure(state="normal");self.result.delete("1.0","end");self.result.insert("end",text);self.result.configure(state="disabled")
