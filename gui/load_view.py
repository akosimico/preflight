from __future__ import annotations
from threading import Thread
import customtkinter as ctk
from core.projects import ProjectService
from core.workflows import run_and_store_load
from database.repositories import LoadMetricsRepository,TestRunsRepository
class LoadView(ctk.CTkFrame):
 def __init__(self,master,projects:ProjectService,runs:TestRunsRepository,metrics:LoadMetricsRepository):
  super().__init__(master,fg_color="transparent");self.projects=projects;self.runs=runs;self.metrics=metrics;ctk.CTkLabel(self,text="Load Testing",font=ctk.CTkFont(size=30,weight="bold")).pack(anchor="w",padx=28,pady=(30,8));form=ctk.CTkFrame(self);form.pack(fill="x",padx=28);self.users=ctk.CTkEntry(form,placeholder_text="Users (5)");self.users.pack(side="left",padx=8,pady=10);self.count=ctk.CTkEntry(form,placeholder_text="Requests (20)");self.count.pack(side="left",padx=8,pady=10);ctk.CTkButton(form,text="START LOAD TEST",command=self.start).pack(side="left",padx=8);self.status=ctk.CTkLabel(self,text="Configure a project API URL.");self.status.pack(anchor="w",padx=28,pady=12)
 def start(self):
  project=self.projects.active()
  if not project or not project["api_url"]:self.status.configure(text="Select a project with an API URL first.");return
  self.status.configure(text="Running load test…")
  def work():
   run,summary=run_and_store_load(project["id"],project["api_url"],self.runs,self.metrics,int(self.users.get() or 5),int(self.count.get() or 20));self.after(0,lambda:self.status.configure(text=f"{summary.requests} requests · {summary.rps} RPS · P95 {summary.p95_ms} ms · {summary.error_rate}% errors"))
  Thread(target=work,daemon=True).start()
