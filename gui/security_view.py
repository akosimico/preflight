from __future__ import annotations
from datetime import datetime, timezone
from threading import Thread
import customtkinter as ctk
from core.projects import ProjectService
from database.repositories import SecurityFindingsRepository, TestRunsRepository
from runners.security_runner import inspect_headers

class SecurityView(ctk.CTkFrame):
 def __init__(self,master,projects:ProjectService,runs:TestRunsRepository,findings:SecurityFindingsRepository):
  super().__init__(master,fg_color="transparent");self.projects,self.runs,self.findings=projects,runs,findings
  ctk.CTkLabel(self,text="Security Checks",font=ctk.CTkFont(size=30,weight="bold")).pack(anchor="w",padx=28,pady=(30,8))
  ctk.CTkLabel(self,text="Safe check: sends one normal GET request and reviews HTTPS, response headers, and CORS. It does not try to exploit your API or change data.",wraplength=880,justify="left",text_color=("#65758B", "#9BA9B8")).pack(anchor="w",padx=28,pady=(0,12))
  ctk.CTkButton(self,text="RUN SAFE SECURITY CHECK",command=self.run).pack(anchor="w",padx=28,pady=(0,12));self.status=ctk.CTkLabel(self,text="Select a project with an API Base URL.");self.status.pack(anchor="w",padx=28,pady=(0,8));self.rows=ctk.CTkScrollableFrame(self,label_text="Findings");self.rows.pack(fill="both",expand=True,padx=28,pady=(0,28))
 def run(self):
  project=self.projects.active()
  if not project or not project["api_url"]:self.status.configure(text="Select a project with an API Base URL first.");return
  self.status.configure(text="Checking response headers…")
  def work():
   run=self.runs.create(project["id"],status="RUNNING",started_at=datetime.now(timezone.utc).isoformat());status,items=inspect_headers(project["api_url"])
   for item in items:self.findings.create(run["id"],item.severity,item.title,target=project["api_url"],details_json={"detail":item.detail})
   self.runs.update(run["id"],status="COMPLETED",finished_at=datetime.now(timezone.utc).isoformat(),summary_json={"security_check":True,"status_code":status,"findings":len(items)})
   self.after(0,lambda:(self.show(items),self.status.configure(text=f"Completed safe security check: {len(items)} finding(s).")))
  Thread(target=work,daemon=True).start()
 def show(self,items):
  for child in self.rows.winfo_children():child.destroy()
  if not items:ctk.CTkLabel(self.rows,text="No configuration findings from this safe check. This is not a guarantee that the API has no vulnerabilities.").pack(anchor="w",padx=10,pady=14);return
  colors={"HIGH":"#C65353","MEDIUM":"#B58329","LOW":"#D5A832","INFO":"#6799C8"}
  for item in items:
   row=ctk.CTkFrame(self.rows);row.pack(fill="x",padx=5,pady=4);ctk.CTkLabel(row,text=item.severity,width=75,text_color=colors[item.severity],font=ctk.CTkFont(weight="bold")).pack(side="left",padx=10,pady=9);ctk.CTkLabel(row,text=f"{item.title}\n{item.detail}",justify="left",anchor="w",wraplength=760).pack(side="left",fill="x",expand=True,padx=6,pady=7)
