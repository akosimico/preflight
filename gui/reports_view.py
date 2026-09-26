from __future__ import annotations
import customtkinter as ctk
from core.projects import ProjectService
from core.timezone import format_pht
from database.repositories import LoadMetricsRepository, TestResultsRepository, TestRunsRepository
from reports.generator import build_report, export


class ReportsView(ctk.CTkFrame):
 def __init__(self, master, projects: ProjectService, runs: TestRunsRepository, results: TestResultsRepository, metrics: LoadMetricsRepository):
  super().__init__(master, fg_color="transparent"); self.projects,self.runs,self.results,self.metrics=projects,runs,results,metrics;self.run_choices={}
  ctk.CTkLabel(self,text="Reports",font=ctk.CTkFont(size=30,weight="bold")).pack(anchor="w",padx=28,pady=(30,8))
  ctk.CTkLabel(self,text="Choose any saved run to review it here, then export a shareable HTML and JSON copy.",text_color=("#65758B", "#9BA9B8")).pack(anchor="w",padx=28)
  selector=ctk.CTkFrame(self,fg_color="transparent");selector.pack(fill="x",padx=28,pady=(14,8));ctk.CTkLabel(selector,text="Report run",font=ctk.CTkFont(weight="bold")).pack(side="left",padx=(0,10));self.run_menu=ctk.CTkOptionMenu(selector,values=["No saved runs"],command=lambda _:self.view_selected(),width=430);self.run_menu.pack(side="left")
  actions=ctk.CTkFrame(self,fg_color="transparent");actions.pack(anchor="w",padx=28,pady=(0,12));ctk.CTkButton(actions,text="VIEW SELECTED REPORT",command=self.view_selected).pack(side="left",padx=(0,8));ctk.CTkButton(actions,text="EXPORT SELECTED REPORT",command=self.generate).pack(side="left")
  self.status=ctk.CTkLabel(self,text="Select a project and run a test to create a report.",wraplength=850,justify="left");self.status.pack(anchor="w",padx=28,pady=(0,10));self.body=ctk.CTkScrollableFrame(self,label_text="Report preview");self.body.pack(fill="both",expand=True,padx=28,pady=(0,28));self.refresh()

 def refresh(self):
  project=self.projects.active();history=self.runs.list(project_id=project["id"]) if project else [];self.run_choices={}
  if not history:self.run_menu.configure(values=["No saved runs"]);self.run_menu.set("No saved runs");return
  choices=[]
  for run in reversed(history):
   api=self.results.list(test_run_id=run["id"]);load=self.metrics.list(test_run_id=run["id"]);kind="API test" if api else "Load test" if load else "Empty run";choice=f"Run #{run['id']} · {kind} · {format_pht(run.get('created_at'))}";choices.append(choice);self.run_choices[choice]=run["id"]
  self.run_menu.configure(values=choices);self.run_menu.set(choices[0])

 def selected_report(self):
  project=self.projects.active();run_id=self.run_choices.get(self.run_menu.get())
  if not project or not run_id:return None
  run=self.runs.get(run_id)
  return build_report(project,run,self.results.list(test_run_id=run_id),self.metrics.list(test_run_id=run_id),[]) if run else None

 def generate(self):
  report=self.selected_report()
  if not report:self.status.configure(text="Choose a saved run first.");return
  paths=export(report);self.status.configure(text=f"Saved report for run #{report['run']['id']}.\n{paths[0]}\n{paths[1]}");self.show(report)

 def view_selected(self):
  report=self.selected_report()
  if not report:self.status.configure(text="Choose a saved run first.");return
  self.status.configure(text=f"Showing run #{report['run']['id']} inside Preflight.");self.show(report)

 def show(self,report):
  for child in self.body.winfo_children():child.destroy()
  run,results,metrics=report["run"],report["api_results"],report["load_metrics"];summary=run.get("summary_json",{});kind="API test" if results else "Load test" if metrics else "run"
  header=ctk.CTkFrame(self.body);header.pack(fill="x",padx=6,pady=8);ctk.CTkLabel(header,text=f"Run #{run['id']} · {run['status']} · {kind}",font=ctk.CTkFont(size=20,weight="bold")).pack(anchor="w",padx=12,pady=(10,2));ctk.CTkLabel(header,text=f"Created {format_pht(run.get('created_at'))} · Gate: {run.get('gate_status') or 'Not evaluated'} · Passed: {summary.get('passed','—')}/{summary.get('total','—')}",anchor="w",wraplength=850).pack(fill="x",padx=12,pady=(0,10))
  if results:
   ctk.CTkLabel(self.body,text="API endpoint results",font=ctk.CTkFont(weight="bold")).pack(anchor="w",padx=10,pady=(10,4))
   for item in results:
    row=ctk.CTkFrame(self.body);row.pack(fill="x",padx=6,pady=2);color={"PASSED":"#2E9B65","FAILED":"#C65353","SKIPPED":"#B58329"}.get(item["status"],"white");ctk.CTkLabel(row,text=item["status"],text_color=color,width=75,font=ctk.CTkFont(weight="bold")).pack(side="left",padx=8,pady=7);ctk.CTkLabel(row,text=item["name"],anchor="w").pack(side="left",fill="x",expand=True);ctk.CTkLabel(row,text=f"{item.get('duration_ms') or '—'} ms",width=100).pack(side="left",padx=8)
  elif metrics:ctk.CTkLabel(self.body,text="This was a load-test run, so it has load metrics rather than individual API endpoint results.",wraplength=800,justify="left",text_color=("#65758B", "#9BA9B8")).pack(anchor="w",padx=10,pady=(10,4))
  else:ctk.CTkLabel(self.body,text="This run did not record API endpoint results or load metrics.").pack(anchor="w",padx=10,pady=(10,4))
  if metrics:
   ctk.CTkLabel(self.body,text="Load-test results",font=ctk.CTkFont(weight="bold")).pack(anchor="w",padx=10,pady=(16,4))
   for metric in metrics:ctk.CTkLabel(self.body,text=f"{metric['requests']} requests · {metric['rps']} requests/second · Average {metric.get('average_ms') or '—'} ms · 95% completed within {metric.get('p95_ms') or '—'} ms · {metric['error_rate']}% failed",wraplength=850,justify="left").pack(anchor="w",padx=10)
