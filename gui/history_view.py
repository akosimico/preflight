from __future__ import annotations
import customtkinter as ctk
from core.history import runs_for_project
from core.projects import ProjectService
from database.repositories import TestRunsRepository
class HistoryView(ctk.CTkFrame):
 def __init__(self,master,projects:ProjectService,runs:TestRunsRepository):
  super().__init__(master,fg_color="transparent");self.projects=projects;self.runs=runs;ctk.CTkLabel(self,text="Run History",font=ctk.CTkFont(size=30,weight="bold")).pack(anchor="w",padx=28,pady=(30,8));ctk.CTkButton(self,text="REFRESH",command=self.refresh).pack(anchor="w",padx=28,pady=(0,8));self.rows=ctk.CTkScrollableFrame(self);self.rows.pack(fill="both",expand=True,padx=28,pady=(0,28));self.refresh()
 def refresh(self):
  for child in self.rows.winfo_children():child.destroy()
  project=self.projects.active(); history=runs_for_project(self.runs,project["id"]) if project else []
  if not history:ctk.CTkLabel(self.rows,text="No runs recorded for the active project.").pack(pady=20)
  for run in history:ctk.CTkLabel(self.rows,text=f'Run #{run["id"]} · {run["status"]} · Gates: {run["gate_status"] or "not evaluated"} · {run["created_at"]}',anchor="w").pack(fill="x",padx=10,pady=8)
