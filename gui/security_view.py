from __future__ import annotations
from datetime import datetime, timezone
from threading import Thread
import customtkinter as ctk
from core.projects import ProjectService
from core.test_manager import TestManager, TestState
from database.repositories import EndpointsRepository, SecurityFindingsRepository, TestRunsRepository
from runners.security_runner import inspect_headers
from security.scanner import active_scan
from gui.components.expandable_result import ExpandableResult
from gui.theme import MUTED, SURFACE

class SecurityView(ctk.CTkFrame):
 def __init__(self,master,projects:ProjectService,runs:TestRunsRepository,findings:SecurityFindingsRepository,endpoints:EndpointsRepository):
  super().__init__(master,fg_color="transparent");self.projects,self.runs,self.findings,self.endpoints=projects,runs,findings,endpoints;self.manager=TestManager();self.filter="All"
  ctk.CTkLabel(self,text="Security Checks",font=ctk.CTkFont(size=30,weight="bold")).pack(anchor="w",padx=28,pady=(30,4));ctk.CTkLabel(self,text="Run a safe configuration review or an opt-in, controlled reflected-input scan.",text_color=MUTED).pack(anchor="w",padx=28,pady=(0,12))
  safe=ctk.CTkFrame(self,fg_color=SURFACE,corner_radius=12);safe.pack(fill="x",padx=28,pady=(0,10));ctk.CTkLabel(safe,text="Safe Configuration Scan",font=ctk.CTkFont(size=16,weight="bold")).pack(anchor="w",padx=14,pady=(12,1));ctk.CTkLabel(safe,text="Non-invasive HTTPS, headers, CORS, and information-disclosure review.",text_color=MUTED).pack(anchor="w",padx=14);ctk.CTkButton(safe,text="RUN SAFE SECURITY CHECK",command=self.run_safe).pack(anchor="w",padx=14,pady=12)
  active=ctk.CTkFrame(self,fg_color=SURFACE,corner_radius=12);active.pack(fill="x",padx=28,pady=(0,10));ctk.CTkLabel(active,text="Active Vulnerability Scan",font=ctk.CTkFont(size=16,weight="bold")).pack(anchor="w",padx=14,pady=(12,1));ctk.CTkLabel(active,text="Controlled GET/OPTIONS checks: reflected input, redirect handling, safe traversal handling, error exposure, and advertised methods. Local, Development, and Staging only.",wraplength=880,justify="left",text_color=MUTED).pack(anchor="w",padx=14);self.authorized=ctk.CTkCheckBox(active,text="I own or am authorized to test this target");self.authorized.pack(anchor="w",padx=14,pady=(8,4));buttons=ctk.CTkFrame(active,fg_color="transparent");buttons.pack(anchor="w",padx=14,pady=(0,12));ctk.CTkButton(buttons,text="RUN ACTIVE SECURITY SCAN",command=self.run_active).pack(side="left",padx=(0,8));ctk.CTkButton(buttons,text="STOP SCAN",fg_color="transparent",border_width=1,command=self.manager.cancel).pack(side="left")
  self.status=ctk.CTkLabel(self,text="Select a project with an API Base URL.",text_color=MUTED);self.status.pack(anchor="w",padx=28,pady=(0,8));self.progress=ctk.CTkProgressBar(self);self.progress.set(0);self.progress.pack(fill="x",padx=28,pady=(0,8));filters=ctk.CTkFrame(self,fg_color="transparent");filters.pack(anchor="w",padx=28,pady=(0,4));
  for name in ("All","Active","Passive") : ctk.CTkButton(filters,text=name,width=72,fg_color="transparent",border_width=1,command=lambda value=name:self.set_filter(value)).pack(side="left",padx=(0,5))
  self.rows=ctk.CTkScrollableFrame(self,label_text="Findings — click a row for details");self.rows.pack(fill="both",expand=True,padx=28,pady=(0,28));self.after(150,self.poll)
 def set_filter(self,value):self.filter=value;self.refresh_latest()
 def run_safe(self):
  project=self.projects.active()
  if not project or not project["api_url"]:self.status.configure(text="Select a project with an API Base URL first.");return
  self.status.configure(text="Checking response headers…")
  def work():
   run=self.runs.create(project["id"],status="RUNNING",started_at=datetime.now(timezone.utc).isoformat());status,items=inspect_headers(project["api_url"]);saved=[]
   for item in items:saved.append(self.findings.create(run["id"],item.severity,item.title,target=project["api_url"],details_json={"scan_type":"passive","detail":item.detail,"status_code":status,"confidence":"high"}))
   self.runs.update(run["id"],status="COMPLETED",finished_at=datetime.now(timezone.utc).isoformat(),summary_json={"security_check":True,"scan_type":"passive","status_code":status,"findings":len(items)});self.after(0,lambda:(self.show(saved),self.status.configure(text=f"Completed safe scan: {len(items)} finding(s).")))
  Thread(target=work,daemon=True).start()
 def run_active(self):
  project=self.projects.active()
  if not project or not project["api_url"]:self.status.configure(text="Select a project with an API Base URL first.");return
  if project["environment"]=="Production":self.status.configure(text="Active scanning is blocked for Production projects.");return
  if not self.authorized.get():self.status.configure(text="Confirm that you own or are authorized to test this target.");return
  self.progress.set(0);self.status.configure(text="Preparing active scan…")
  def task(cancel,log):
   run=self.runs.create(project["id"],status="RUNNING",started_at=datetime.now(timezone.utc).isoformat());records=self.endpoints.list(project_id=project["id"],enabled=1)
   def update(current,total,target,requests,findings):self.after(0,lambda:(self.progress.set(current/max(total,1)),self.status.configure(text=f"Scanning {current}/{total}: {target} · Requests: {requests} · Findings: {findings}")))
   items,requests=active_scan(project["api_url"],records,cancel,update,project["environment"]);saved=[]
   for item in items:saved.append(self.findings.create(run["id"],item.severity,item.title,target=item.target,details_json=item.details))
   state="CANCELLED" if cancel.is_set() else "COMPLETED";self.runs.update(run["id"],status=state,finished_at=datetime.now(timezone.utc).isoformat(),summary_json={"security_check":True,"scan_type":"active","requests":requests,"findings":len(items)});self.after(0,lambda:(self.show(saved),self.status.configure(text=f"{state.title()}: {requests} requests, {len(items)} finding(s)."),self.progress.set(1 if not cancel.is_set() else 0)))
  try:self.manager.start(TestState.RUNNING_SECURITY,task)
  except RuntimeError as error:self.status.configure(text=str(error))
 def poll(self):
  for event in self.manager.poll():
   if event.kind=="log":self.status.configure(text=event.payload["message"])
  self.after(150,self.poll)
 def refresh_latest(self):
  project=self.projects.active()
  if not project:return
  history=self.runs.list(project_id=project["id"])
  if history:self.show(self.findings.list(test_run_id=history[-1]["id"]))
 def show(self,items):
  for child in self.rows.winfo_children():child.destroy()
  visible=[item for item in items if self.filter=="All" or item.get("details_json",{}).get("scan_type","passive").title()==self.filter]
  if not visible:ctk.CTkLabel(self.rows,text="No findings match this filter.",text_color=MUTED).pack(anchor="w",padx=10,pady=14);return
  for item in visible:
   detail=item.get("details_json",{});scan=detail.get("scan_type","passive").upper();ExpandableResult(self.rows,item["title"],item["severity"],f"{scan} · {detail.get('confidence','Not recorded')} confidence",[("Scan type",scan),("Confidence",detail.get("confidence")),("CWE",detail.get("cwe")),("Endpoint",f"{detail.get('method','')} {detail.get('endpoint',item['target'])}"),("Parameter",detail.get("parameter")),("Response status",detail.get("status_code")),("Description",detail.get("description",detail.get("detail"))),("Evidence",detail.get("evidence")),("Recommendation",detail.get("remediation",detail.get("detail")))]).pack(fill="x",padx=5,pady=4)
