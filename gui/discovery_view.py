from __future__ import annotations
from threading import Thread
import customtkinter as ctk
from core.discovery import discover_and_store
from core.projects import ProjectService
from database.repositories import EndpointsRepository
from gui.components.endpoint_row import EndpointRow

class DiscoveryView(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, projects: ProjectService, endpoints: EndpointsRepository) -> None:
        super().__init__(master,fg_color="transparent"); self.projects=projects; self.endpoints=endpoints
        ctk.CTkLabel(self,text="API Discovery",font=ctk.CTkFont(size=30,weight="bold")).pack(anchor="w",padx=28,pady=(30,4))
        self.status=ctk.CTkLabel(self,text="Choose a project with an API URL to discover its OpenAPI endpoints."); self.status.pack(anchor="w",padx=28,pady=(0,12))
        controls=ctk.CTkFrame(self,fg_color="transparent"); controls.pack(fill="x",padx=28,pady=(0,10))
        ctk.CTkButton(controls,text="DISCOVER API",command=self.discover).pack(side="left",padx=(0,8))
        ctk.CTkButton(controls,text="SELECT ALL",fg_color="transparent",border_width=1,command=lambda:self.set_all(True)).pack(side="left",padx=4)
        ctk.CTkButton(controls,text="DESELECT ALL",fg_color="transparent",border_width=1,command=lambda:self.set_all(False)).pack(side="left",padx=4)
        self.rows=ctk.CTkScrollableFrame(self,label_text="Discovered endpoints"); self.rows.pack(fill="both",expand=True,padx=28,pady=(0,28)); self.refresh()
    def refresh(self):
        for child in self.rows.winfo_children(): child.destroy()
        project=self.projects.active()
        if not project: ctk.CTkLabel(self.rows,text="No active project.").pack(pady=20); return
        records=self.endpoints.list(project_id=project["id"])
        if not records: ctk.CTkLabel(self.rows,text="No endpoints discovered yet.").pack(pady=20); return
        for record in records:
            label=f'{record["method"]} {record["path"]}' + ("  ⚠ destructive" if record["is_destructive"] else "")
            row=EndpointRow(self.rows,record["method"],label,record["enabled"],command=lambda r=record:self.toggle(r))
            row.pack(fill="x",padx=4,pady=3)
    def toggle(self, record): self.endpoints.update(record["id"],enabled=not record["enabled"]); self.refresh()
    def set_all(self, enabled: bool):
        project=self.projects.active()
        if project:
            for record in self.endpoints.list(project_id=project["id"]): self.endpoints.update(record["id"],enabled=enabled)
        self.refresh()
    def discover(self):
        project=self.projects.active()
        if not project or not project["api_url"]: self.status.configure(text="Select a project with an API Base URL first."); return
        self.status.configure(text="Discovering /openapi.json…")
        def run():
            try: count=len(discover_and_store(project["id"],project["api_url"],self.endpoints)); text=f"Discovered {count} endpoints."
            except Exception as error: text=f"Discovery failed: {error}"
            self.after(0,lambda:(self.status.configure(text=text),self.refresh()))
        Thread(target=run,daemon=True).start()
