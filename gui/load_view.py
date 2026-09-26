from __future__ import annotations
from threading import Thread
import customtkinter as ctk
from core.projects import ProjectService
from core.workflows import run_and_store_load
from database.repositories import EndpointsRepository, LoadMetricsRepository, TestRunsRepository
from core.release_endpoints import release_urls
from gui.components.expandable_result import ExpandableResult
from gui.theme import MUTED, SURFACE

class LoadView(ctk.CTkFrame):
 def __init__(self,master,projects:ProjectService,runs:TestRunsRepository,metrics:LoadMetricsRepository,endpoints:EndpointsRepository):
  super().__init__(master,fg_color="transparent");self.projects=projects;self.runs=runs;self.metrics=metrics;self.endpoints=endpoints
  ctk.CTkLabel(self,text="Load Testing",font=ctk.CTkFont(size=30,weight="bold")).pack(anchor="w",padx=28,pady=(30,4));ctk.CTkLabel(self,text="Measure how your API behaves when several people make requests at once.",text_color=MUTED).pack(anchor="w",padx=28,pady=(0,14))
  form=ctk.CTkFrame(self,fg_color=SURFACE,corner_radius=12);form.pack(fill="x",padx=28)
  self.users=self.field(form,"Virtual users","People simulated at once","Example: 5");self.count=self.field(form,"Total requests","Requests sent in this test","Example: 20");ctk.CTkButton(form,text="START LOAD TEST",command=self.start).pack(side="left",padx=14,pady=28)
  self.status=ctk.CTkLabel(self,text="Choose values, then start a test. Click the result to inspect its metrics.",justify="left",text_color=MUTED);self.status.pack(anchor="w",padx=28,pady=14);self.result_box=ctk.CTkFrame(self,fg_color="transparent");self.result_box.pack(fill="x",padx=28,pady=(0,14))
 def field(self,master,label,help_text,placeholder):
  box=ctk.CTkFrame(master,fg_color="transparent");box.pack(side="left",padx=12,pady=10);ctk.CTkLabel(box,text=label,font=ctk.CTkFont(weight="bold")).pack(anchor="w");ctk.CTkLabel(box,text=help_text,text_color=MUTED).pack(anchor="w");entry=ctk.CTkEntry(box,width=190,placeholder_text=placeholder);entry.pack(pady=(4,0));return entry
 def start(self):
  project=self.projects.active()
  if not project or not project["api_url"]:self.status.configure(text="Select a project with an API URL first.");return
  try:users,count=int(self.users.get() or 5),int(self.count.get() or 20)
  except ValueError:self.status.configure(text="Virtual users and total requests must be whole numbers.");return
  self.status.configure(text="Running load test…")
  def work():
   urls=release_urls(project["api_url"],self.endpoints.list(project_id=project["id"])) or [project["api_url"]]
   _,summary=run_and_store_load(project["id"],urls,self.runs,self.metrics,users,count);self.after(0,lambda:self.show_summary(f"{len(urls)} release endpoint(s)",users,summary))
  Thread(target=work,daemon=True).start()
 def show_summary(self,target,users,summary):
  for child in self.result_box.winfo_children():child.destroy()
  outcome="All requests failed—check the API URL, authentication, and server logs." if summary.error_rate==100 else f"{summary.error_rate}% of requests failed."
  self.status.configure(text=f"Finished: {summary.requests} requests from {users} virtual users. {outcome}")
  status="FAILED" if summary.error_rate else "PASSED";details=[("Target",target),("Virtual users",users),("Requests",summary.requests),("Successful",summary.successes),("Failed",summary.failures),("Requests / second",summary.rps),("Average",f"{summary.average_ms} ms"),("P50",f"{summary.p50_ms} ms"),("P95",f"{summary.p95_ms} ms"),("P99",f"{summary.p99_ms} ms"),("Error rate",f"{summary.error_rate}%")]
  ExpandableResult(self.result_box,"Latest load-test summary",status,f"P95 {summary.p95_ms} ms · {summary.error_rate}% errors",details).pack(fill="x")
