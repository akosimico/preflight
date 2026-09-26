from __future__ import annotations
import customtkinter as ctk
from core.gates import evaluate
from core.projects import ProjectService
from database.repositories import SettingsRepository, TestRunsRepository

GATE_COPY = {
 "api_pass_rate": ("Minimum successful API tests (%)", "At least this percentage of API checks must pass."),
 "avg_response_ms": ("Maximum average response time (ms)", "The average time across requests must be at or below this."),
 "p95_ms": ("95% of requests must finish within (ms)", "Only the slowest 5% of requests may take longer."),
 "p99_ms": ("99% of requests must finish within (ms)", "Only the slowest 1% of requests may take longer."),
 "error_rate": ("Maximum failed requests (%)", "The percentage of failed requests must be at or below this."),
}

class GatesView(ctk.CTkFrame):
 def __init__(self,master,projects:ProjectService,runs:TestRunsRepository,settings:SettingsRepository):
  super().__init__(master,fg_color="transparent");self.projects=projects;self.runs=runs;self.settings=settings
  ctk.CTkLabel(self,text="Deployment Gates",font=ctk.CTkFont(size=30,weight="bold")).pack(anchor="w",padx=28,pady=(30,8))
  ctk.CTkLabel(self,text="These are your release rules—not general app settings. The latest run is approved only when it meets every rule below.",wraplength=900,justify="left",text_color=("#65758B", "#9BA9B8")).pack(anchor="w",padx=28,pady=(0,12));self.entries={};form=ctk.CTkFrame(self);form.pack(fill="x",padx=28);defaults={"api_pass_rate":95,"avg_response_ms":500,"p95_ms":800,"p99_ms":1200,"error_rate":2}
  saved=settings.get("gate_thresholds",defaults)
  for name,value in saved.items():
   label,help_text=GATE_COPY[name];row=ctk.CTkFrame(form,fg_color="transparent");row.pack(fill="x",padx=8,pady=5)
   ctk.CTkLabel(row,text=f"{label}\n{help_text}",justify="left",anchor="w",width=330,font=ctk.CTkFont(weight="bold"),text_color=("#E7EEF8", "#E7EEF8")).pack(side="left",padx=(0,10))
   entry=ctk.CTkEntry(row);entry.insert(0,str(value));entry.pack(side="left",fill="x",expand=True,pady=6);self.entries[name]=entry
  ctk.CTkButton(form,text="SAVE RULES & CHECK LATEST RUN",command=self.evaluate).pack(padx=8,pady=12);self.result=ctk.CTkTextbox(self,height=260,state="disabled");self.result.pack(fill="both",expand=True,padx=28,pady=16);self.show("Save the rules and check a run to see a plain-language release decision here.")
 def evaluate(self):
  project=self.projects.active()
  if not project:self.show("Select an active project before checking release rules.");return
  try:thresholds={name:float(entry.get()) for name,entry in self.entries.items()}
  except ValueError:self.show("Each release rule must be a number.");return
  self.settings.set("gate_thresholds",thresholds);runs=self.runs.list(project_id=project["id"])
  if not runs:self.show("There is no completed run to check yet.");return
  summary=runs[-1]["summary_json"];metrics={**summary,"pass_rate":100-summary.get("error_rate",0)};items=evaluate(metrics,thresholds);passed=all(item.passed for item in items);self.runs.update(runs[-1]["id"],gate_status="PASSED" if passed else "FAILED")
  lines=["READY TO DEPLOY" if passed else "NOT READY TO DEPLOY", ""]
  for item in items:
   label,_=GATE_COPY[item.name];comparison="meets" if item.passed else "does not meet";lines.append(f"{'PASS' if item.passed else 'FAIL'} — {label}: {item.actual} {comparison} the rule of {item.limit}.")
  self.show("\n".join(lines))
 def show(self,text):self.result.configure(state="normal");self.result.delete("1.0","end");self.result.insert("end",text);self.result.configure(state="disabled")
