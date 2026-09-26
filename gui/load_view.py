from __future__ import annotations
from threading import Thread
import customtkinter as ctk
from core.projects import ProjectService
from core.workflows import run_and_store_load
from database.repositories import LoadMetricsRepository, TestRunsRepository

class LoadView(ctk.CTkFrame):
 def __init__(self,master,projects:ProjectService,runs:TestRunsRepository,metrics:LoadMetricsRepository):
  super().__init__(master,fg_color="transparent");self.projects=projects;self.runs=runs;self.metrics=metrics
  ctk.CTkLabel(self,text="Load Testing",font=ctk.CTkFont(size=30,weight="bold")).pack(anchor="w",padx=28,pady=(30,8));ctk.CTkLabel(self,text="Check how your API behaves when several people send requests at the same time.",text_color=("#65758B", "#9BA9B8")).pack(anchor="w",padx=28,pady=(0,12));form=ctk.CTkFrame(self);form.pack(fill="x",padx=28)
  user_box=ctk.CTkFrame(form,fg_color="transparent");user_box.pack(side="left",padx=8,pady=8);ctk.CTkLabel(user_box,text="Virtual users",font=ctk.CTkFont(weight="bold")).pack(anchor="w");ctk.CTkLabel(user_box,text="People simulated at once",text_color=("#65758B", "#9BA9B8")).pack(anchor="w");self.users=ctk.CTkEntry(user_box,width=170,placeholder_text="Example: 5");self.users.pack(pady=(3,0))
  request_box=ctk.CTkFrame(form,fg_color="transparent");request_box.pack(side="left",padx=8,pady=8);ctk.CTkLabel(request_box,text="Total requests",font=ctk.CTkFont(weight="bold")).pack(anchor="w");ctk.CTkLabel(request_box,text="Requests sent in this test",text_color=("#65758B", "#9BA9B8")).pack(anchor="w");self.count=ctk.CTkEntry(request_box,width=170,placeholder_text="Example: 20");self.count.pack(pady=(3,0))
  ctk.CTkButton(form,text="START LOAD TEST",command=self.start).pack(side="left",padx=14,pady=28);self.status=ctk.CTkLabel(self,text="Choose values, then start a test. Results will explain speed and failures.",justify="left");self.status.pack(anchor="w",padx=28,pady=14)
 def start(self):
  project=self.projects.active()
  if not project or not project["api_url"]:self.status.configure(text="Select a project with an API URL first.");return
  try:users,count=int(self.users.get() or 5),int(self.count.get() or 20)
  except ValueError:self.status.configure(text="Virtual users and total requests must be whole numbers.");return
  self.status.configure(text="Running load test…")
  def work():
   _,summary=run_and_store_load(project["id"],project["api_url"],self.runs,self.metrics,users,count);outcome="All requests failed—check the API URL, authentication, and server logs." if summary.error_rate==100 else f"{summary.error_rate}% of requests failed."
   self.after(0,lambda:self.status.configure(text=f"Finished: {summary.requests} requests from {users} virtual users. Average speed: {summary.rps} requests/second. 95% finished within {summary.p95_ms} ms. {outcome}"))
  Thread(target=work,daemon=True).start()
