from __future__ import annotations
import tkinter.messagebox as messagebox
from threading import Thread
import customtkinter as ctk
from core.projects import ENVIRONMENTS, ProjectService
from core.connections import check_project

class ProjectsView(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, service: ProjectService, on_project_changed) -> None:
        super().__init__(master,fg_color="transparent"); self.service=service; self.on_project_changed=on_project_changed; self.editing_id: int|None=None
        self.grid_columnconfigure(1,weight=1); self.grid_rowconfigure(2,weight=1)
        ctk.CTkLabel(self,text="Projects",font=ctk.CTkFont(size=30,weight="bold")).grid(row=0,column=0,columnspan=2,padx=28,pady=(30,18),sticky="w")
        form=ctk.CTkFrame(self,corner_radius=12); form.grid(row=1,column=0,padx=(28,10),pady=8,sticky="new")
        ctk.CTkLabel(form,text="Project details",font=ctk.CTkFont(size=16,weight="bold")).pack(anchor="w",padx=16,pady=(16,10))
        self.name=self._field(form,"Project Name"); self.frontend=self._field(form,"Frontend URL"); self.api=self._field(form,"API Base URL")
        self.environment=ctk.CTkOptionMenu(form,values=list(ENVIRONMENTS)); self.environment.pack(fill="x",padx=16,pady=(0,10)); self.environment.set("Local")
        self.connection_status=ctk.CTkLabel(form,text="Connection checks have not run.",wraplength=260,justify="left"); self.connection_status.pack(anchor="w",padx=16,pady=(2,8))
        ctk.CTkButton(form,text="TEST CONNECTION",fg_color="transparent",border_width=1,command=self.test_connection).pack(fill="x",padx=16,pady=(4,6)); self.save=ctk.CTkButton(form,text="CREATE PROJECT",command=self.save_project); self.save.pack(fill="x",padx=16,pady=(4,10)); ctk.CTkButton(form,text="CLEAR",fg_color="transparent",border_width=1,command=self.clear_form).pack(fill="x",padx=16,pady=(0,16))
        self.list_frame=ctk.CTkScrollableFrame(self,corner_radius=12,label_text="Your projects"); self.list_frame.grid(row=1,column=1,rowspan=2,padx=(10,28),pady=8,sticky="nsew")
        self.refresh()
    def _field(self, master, label):
        ctk.CTkLabel(master,text=label).pack(anchor="w",padx=16,pady=(4,2)); entry=ctk.CTkEntry(master,placeholder_text=label); entry.pack(fill="x",padx=16,pady=(0,8)); return entry
    def refresh(self):
        for child in self.list_frame.winfo_children(): child.destroy()
        projects=self.service.projects.list()
        if not projects: ctk.CTkLabel(self.list_frame,text="No projects yet. Create your first target.").pack(padx=16,pady=24); return
        active=self.service.active(); active_id=active["id"] if active else None
        for project in projects:
            row=ctk.CTkFrame(self.list_frame); row.pack(fill="x",padx=6,pady=5); marker="  ACTIVE" if project["id"]==active_id else ""
            ctk.CTkButton(row,text=f'{project["name"]} · {project["environment"]}{marker}',anchor="w",fg_color="transparent",command=lambda p=project:self.select(p)).pack(side="left",fill="x",expand=True,padx=6,pady=8)
            ctk.CTkButton(row,text="Edit",width=54,command=lambda p=project:self.load(p)).pack(side="left",padx=3,pady=8); ctk.CTkButton(row,text="Delete",width=62,fg_color="#B34141",hover_color="#8D3030",command=lambda p=project:self.delete(p)).pack(side="left",padx=(3,6),pady=8)
    def select(self, project): self.service.select(project["id"]); self.on_project_changed(project["name"]); self.refresh()
    def load(self, project):
        self.editing_id=project["id"]; self.save.configure(text="SAVE CHANGES")
        for entry,value in ((self.name,project["name"]),(self.frontend,project["frontend_url"]),(self.api,project["api_url"])): entry.delete(0,"end"); entry.insert(0,value)
        self.environment.set(project["environment"])
    def clear_form(self):
        self.editing_id=None; self.save.configure(text="CREATE PROJECT"); self.environment.set("Local")
        for entry in (self.name,self.frontend,self.api): entry.delete(0,"end")
    def save_project(self):
        try:
            args=(self.name.get(),self.frontend.get(),self.api.get(),self.environment.get())
            project=self.service.update(self.editing_id,*args) if self.editing_id else self.service.create(*args)
        except ValueError as error: messagebox.showerror("Cannot save project",str(error)); return
        self.on_project_changed(project["name"]); self.clear_form(); self.refresh()
    def test_connection(self):
        self.connection_status.configure(text="Checking frontend and API…")
        def run():
            results=check_project(self.frontend.get(),self.api.get())
            text="\n".join(f"{name.title()}: {'✓' if item.reachable else '✗'} {item.message}" for name,item in results.items())
            self.after(0,lambda:self.connection_status.configure(text=text))
        Thread(target=run,daemon=True).start()
    def delete(self, project):
        if messagebox.askyesno("Delete project",f'Delete “{project["name"]}” and its stored results?'):
            self.service.delete(project["id"]); active=self.service.active(); self.on_project_changed(active["name"] if active else None); self.clear_form(); self.refresh()
