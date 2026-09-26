from __future__ import annotations
import customtkinter as ctk
from core.dashboard_analytics import recent_series
from core.projects import ProjectService
from database.repositories import LoadMetricsRepository, SecurityFindingsRepository, TestRunsRepository
from gui.components.metric_card import MetricCard
from gui.components.status_card import StatusCard
from gui.components.trend_chart import TrendChart
from gui.theme import MUTED, PRIMARY, SUCCESS

class DashboardView(ctk.CTkFrame):
 def __init__(self,master,projects:ProjectService,runs:TestRunsRepository,metrics:LoadMetricsRepository,findings:SecurityFindingsRepository,open_suite):
  super().__init__(master,fg_color="transparent");self.projects,self.runs,self.metrics,self.findings=projects,runs,metrics,findings;self.grid_columnconfigure((0,1,2),weight=1)
  title=ctk.CTkFrame(self,fg_color="transparent");title.grid(row=0,column=0,columnspan=3,padx=28,pady=(30,4),sticky="ew");title.grid_columnconfigure(0,weight=1);ctk.CTkLabel(title,text="Dashboard",font=ctk.CTkFont(size=30,weight="bold")).grid(row=0,column=0,sticky="w");ctk.CTkButton(title,text="REFRESH",width=100,command=self.refresh).grid(row=0,column=1,sticky="e")
  self.subtitle=ctk.CTkLabel(self,text="A current overview of the active project's latest checks.",text_color=MUTED);self.subtitle.grid(row=1,column=0,columnspan=3,padx=28,pady=(0,18),sticky="w");self.status_cards=[]
  for column,label in enumerate(("API checks","Load test","Security")):
   card=StatusCard(self,label,"Not run");card.grid(row=2,column=column,padx=8 if column else 28,pady=6,sticky="ew");self.status_cards.append(card)
  self.metric_cards=[]
  for column,label in enumerate(("Requests","Average","Errors")):
   card=MetricCard(self,label);card.grid(row=3,column=column,padx=8 if column else 28,pady=6,sticky="ew");self.metric_cards.append(card)
  self.action_note=ctk.CTkLabel(self,text="",text_color=MUTED);self.action_note.grid(row=4,column=0,columnspan=3,padx=28,pady=(8,4),sticky="w");self.run_button=ctk.CTkButton(self,text="RUN API PREFLIGHT",height=38,command=open_suite);self.run_button.grid(row=5,column=0,columnspan=3,padx=28,pady=(4,14),sticky="ew");self.chart_area=ctk.CTkFrame(self,fg_color="transparent");self.chart_area.grid(row=6,column=0,columnspan=3,padx=28,pady=(0,28),sticky="ew");self.chart_area.grid_columnconfigure((0,1),weight=1);self.refresh()
 def set_empty(self):
  for card in self.status_cards:card.set_status("Not run")
  for card in self.metric_cards:card.set_value("—")
 def refresh(self):
  project=self.projects.active()
  for child in self.chart_area.winfo_children():child.destroy()
  if not project:
   self.subtitle.configure(text="Create and select a project to begin.");self.action_note.configure(text="Next step: create a project and add its API Base URL.");self.set_empty();self.charts({});return
  history=self.runs.list(project_id=project["id"])
  if not history:
   self.subtitle.configure(text=f"{project['name']} · No checks have run yet.");self.action_note.configure(text="Next step: discover endpoints, then run an API preflight.");self.set_empty();self.charts({});return
  latest=history[-1];recent=list(reversed(history));series=recent_series(history,lambda run_id:self.metrics.list(test_run_id=run_id));api=series["api"];load=series["load"];security=series["security"]
  self.subtitle.configure(text=f"{project['name']} · Most recent activity: run #{latest['id']} is {latest['status']}.");self.status_cards[0].set_status(f"{api[-1]['value']}% pass" if api else "Not run");self.status_cards[1].set_status("Recorded" if load else "Not run");self.status_cards[2].set_status(f"{security[-1]['findings']} finding(s)" if security else "Not run")
  metric=load[-1] if load else {};values=(str(self.metrics.list(test_run_id=metric.get("run_id"))[0]["requests"]) if metric else "—",f"{metric.get('average','—')} ms",f"{100-metric.get('success_rate',100) if metric else '—'} %")
  for card,value in zip(self.metric_cards,values):card.set_value(value)
  self.action_note.configure(text="Analytics use the latest 10 relevant saved runs. Run a load test to start performance trends." if not load else "Click a chart point to inspect its saved run timestamp.");self.charts(series)
 def charts(self,series):
  load=series.get("load",[]);api=series.get("api",[])
  TrendChart(self.chart_area,"Response time trend","ms",[("Average","average",load,"#2B7FC0"),("P95","p95",load,"#E0A93B")]).grid(row=0,column=0,padx=(0,8),pady=6,sticky="ew")
  reliability_load=[{**item,"reliability":item["success_rate"]} for item in load];TrendChart(self.chart_area,"Reliability trend","%",[("API pass rate","value",api,"#46B77A"),("Load success rate","reliability",reliability_load,"#2B7FC0")]).grid(row=0,column=1,padx=(8,0),pady=6,sticky="ew")
