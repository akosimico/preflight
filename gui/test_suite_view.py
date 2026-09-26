from __future__ import annotations
from threading import Thread
import customtkinter as ctk
from core.projects import ProjectService
from database.repositories import EndpointsRepository,TestResultsRepository,TestRunsRepository
from runners.api_runner import run_request
from runners.api_runner import expected_success_status,redact
class TestSuiteView(ctk.CTkFrame):
    def __init__(self,master,projects:ProjectService,endpoints:EndpointsRepository,runs:TestRunsRepository,results:TestResultsRepository):
        super().__init__(master,fg_color="transparent");self.projects=projects;self.endpoints=endpoints;self.runs=runs;self.results=results
        ctk.CTkLabel(self,text="API Test Suite",font=ctk.CTkFont(size=30,weight="bold")).pack(anchor="w",padx=28,pady=(30,6));self.status=ctk.CTkLabel(self,text="Run enabled discovered endpoints.");self.status.pack(anchor="w",padx=28,pady=(0,14));ctk.CTkButton(self,text="RUN API TESTS",command=self.run).pack(anchor="w",padx=28,pady=(0,10)); manual=ctk.CTkFrame(self);manual.pack(fill="x",padx=28,pady=(0,10));self.manual_method=ctk.CTkOptionMenu(manual,values=["GET","POST","PUT","PATCH","DELETE"],width=90);self.manual_method.pack(side="left",padx=8,pady=8);self.manual_path=ctk.CTkEntry(manual,placeholder_text="Manual path, e.g. /health");self.manual_path.pack(side="left",fill="x",expand=True,padx=4,pady=8);ctk.CTkButton(manual,text="RUN MANUAL",command=self.run_manual).pack(side="left",padx=8,pady=8); self.rows=ctk.CTkScrollableFrame(self,label_text="Results");self.rows.pack(fill="both",expand=True,padx=28,pady=(0,28))
    def run(self):
        project=self.projects.active()
        if not project or not project["api_url"]:self.status.configure(text="Select a project with an API URL first.");return
        self.status.configure(text="Running API tests…")
        def worker():
            run=self.runs.create(project["id"],status="RUNNING"); records=self.endpoints.list(project_id=project["id"],enabled=1); passed=0
            self.after(0,self.clear_rows)
            for endpoint in records:
                name=f'{endpoint["method"]} {endpoint["path"]}'
                if "{" in endpoint["path"]:
                    self.results.create(run["id"],name,"SKIPPED",endpoint_id=endpoint["id"],details_json={"error":"Path parameters need values. Add this as a manual API test."});self.after(0,lambda n=name:self.add_row(n,"SKIPPED",None,"Path parameters need values."));continue
                definition=endpoint["definition_json"]; result=run_request(endpoint["method"],project["api_url"].rstrip("/")+endpoint["path"],expected_status=expected_success_status(definition)); passed+=result.passed; status="PASSED" if result.passed else "FAILED"; details={"error":result.error,"status_code":result.status_code,"response":redact(result.response_text)};self.results.create(run["id"],name,status,endpoint_id=endpoint["id"],duration_ms=result.duration_ms,details_json=details);self.after(0,lambda n=name,s=status,r=result:self.add_row(n,s,r.duration_ms,r.error))
            self.runs.update(run["id"],status="COMPLETED",summary_json={"passed":passed,"total":len(records)});self.after(0,lambda:self.status.configure(text=f"Completed: {passed}/{len(records)} passed."))
        Thread(target=worker,daemon=True).start()
    def clear_rows(self):
        for child in self.rows.winfo_children(): child.destroy()
    def add_row(self,name,status,duration,error):
        color={"PASSED":"#2E9B65","FAILED":"#C65353","SKIPPED":"#B58329"}[status]; row=ctk.CTkFrame(self.rows);row.pack(fill="x",padx=4,pady=3);ctk.CTkLabel(row,text=status,width=70,text_color=color,font=ctk.CTkFont(weight="bold")).pack(side="left",padx=8,pady=7);ctk.CTkLabel(row,text=name,anchor="w").pack(side="left",fill="x",expand=True);ctk.CTkLabel(row,text=(f"{duration} ms" if duration is not None else error or ""),width=280,anchor="w",wraplength=280).pack(side="left",padx=8)
    def run_manual(self):
        project=self.projects.active(); path=self.manual_path.get().strip()
        if not project or not project["api_url"] or not path: self.status.configure(text="Select a project and enter a manual path."); return
        name=f"{self.manual_method.get()} {path}"; self.status.configure(text=f"Running {name}…")
        def worker():
            run=self.runs.create(project["id"],status="RUNNING"); result=run_request(self.manual_method.get(),project["api_url"].rstrip("/")+path); status="PASSED" if result.passed else "FAILED";self.results.create(run["id"],name,status,duration_ms=result.duration_ms,details_json={"error":result.error,"response":redact(result.response_text)});self.runs.update(run["id"],status="COMPLETED",summary_json={"passed":int(result.passed),"total":1});self.after(0,lambda:(self.clear_rows(),self.add_row(name,status,result.duration_ms,result.error),self.status.configure(text=f"{name}: {status}")))
        Thread(target=worker,daemon=True).start()
