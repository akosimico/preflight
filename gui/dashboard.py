from __future__ import annotations
import customtkinter as ctk
from core.projects import ProjectService
from database.repositories import LoadMetricsRepository, SecurityFindingsRepository, TestRunsRepository
from gui.components.metric_card import MetricCard
from gui.components.status_card import StatusCard


class DashboardView(ctk.CTkFrame):
 def __init__(self,master,projects:ProjectService,runs:TestRunsRepository,metrics:LoadMetricsRepository,findings:SecurityFindingsRepository,open_suite):
  super().__init__(master,fg_color="transparent");self.projects,self.runs,self.metrics,self.findings=projects,runs,metrics,findings;self.grid_columnconfigure((0,1,2),weight=1)
  title=ctk.CTkFrame(self,fg_color="transparent");title.grid(row=0,column=0,columnspan=3,padx=28,pady=(30,4),sticky="ew");title.grid_columnconfigure(0,weight=1);ctk.CTkLabel(title,text="Dashboard",font=ctk.CTkFont(size=30,weight="bold")).grid(row=0,column=0,sticky="w");ctk.CTkButton(title,text="REFRESH",width=100,command=self.refresh).grid(row=0,column=1,sticky="e")
  self.subtitle=ctk.CTkLabel(self,text="A current overview of the active project's latest checks.",text_color=("#65758B", "#9BA9B8"));self.subtitle.grid(row=1,column=0,columnspan=3,padx=28,pady=(0,24),sticky="w")
  self.status_cards=[]
  for column,label in enumerate(("API","Load","Security")):
   card=StatusCard(self,label,"Not run");card.grid(row=2,column=column,padx=8 if column else 28,pady=8,sticky="ew");self.status_cards.append(card)
  self.metric_cards=[]
  for column,label in enumerate(("Requests","Average","Errors")):
   card=MetricCard(self,label);card.grid(row=3,column=column,padx=8 if column else 28,pady=8,sticky="ew");self.metric_cards.append(card)
  self.run_button=ctk.CTkButton(self,text="RUN API PREFLIGHT",height=42,command=open_suite);self.run_button.grid(row=4,column=0,columnspan=3,padx=28,pady=28,sticky="ew");self.refresh()

 def set_empty(self):
  for card in self.status_cards:card.set_status("Not run")
  for card in self.metric_cards:card.set_value("—")

 def refresh(self):
  project=self.projects.active()
  if not project:
   self.subtitle.configure(text="Create and select a project to begin.");self.set_empty();return
  history=self.runs.list(project_id=project["id"])
  if not history:
   self.subtitle.configure(text=f"{project['name']} · No checks have run yet. Start with an API preflight.");self.set_empty();return
  latest=history[-1];recent=list(reversed(history))
  api_run=next((item for item in recent if "total" in item.get("summary_json",{})),None)
  load_run=None;load=[]
  for item in recent:
   candidate=self.metrics.list(test_run_id=item["id"])
   if candidate:load_run,load=item,candidate;break
  security_run=next((item for item in recent if item.get("summary_json",{}).get("security_check")),None)
  self.subtitle.configure(text=f"{project['name']} · Most recent activity: run #{latest['id']} is {latest['status']}.")
  self.status_cards[0].set_status(api_run["status"] if api_run else "Not run")
  self.status_cards[1].set_status("Recorded" if load_run else "Not run")
  self.status_cards[2].set_status(f"{security_run['summary_json'].get('findings', 0)} finding(s)" if security_run else "Not run")
  metric=load[0] if load else {}
  values=(str(metric.get("requests","—")),f"{metric.get('average_ms','—')} ms",f"{metric.get('error_rate','—')} %")
  for card,value in zip(self.metric_cards,values):card.set_value(value)
