from __future__ import annotations
import customtkinter as ctk
from core.history import runs_for_project
from core.projects import ProjectService
from core.timezone import format_pht
from database.repositories import TestRunsRepository


class HistoryView(ctk.CTkFrame):
    def __init__(self, master, projects: ProjectService, runs: TestRunsRepository):
        super().__init__(master, fg_color="transparent")
        self.projects, self.runs = projects, runs
        ctk.CTkLabel(self, text="Run History", font=ctk.CTkFont(size=30, weight="bold")).pack(anchor="w", padx=28, pady=(30, 8))
        ctk.CTkLabel(self, text="All dates and times are shown in Philippine Time (PHT).", text_color=("#65758B", "#9BA9B8")).pack(anchor="w", padx=28)
        ctk.CTkButton(self, text="REFRESH", command=self.refresh).pack(anchor="w", padx=28, pady=(10, 8))
        self.rows = ctk.CTkScrollableFrame(self)
        self.rows.pack(fill="both", expand=True, padx=28, pady=(0, 28))
        self.refresh()

    def refresh(self):
        for child in self.rows.winfo_children(): child.destroy()
        project = self.projects.active()
        history = runs_for_project(self.runs, project["id"]) if project else []
        if not history:
            ctk.CTkLabel(self.rows, text="No runs recorded for the active project.").pack(pady=20)
        for run in history:
            summary = run.get("summary_json", {})
            card = ctk.CTkFrame(self.rows); card.pack(fill="x", padx=6, pady=6)
            ctk.CTkLabel(card, text=f'Run #{run["id"]}  ·  {run["status"]}', font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", padx=12, pady=(9, 1))
            details = (f'Created: {format_pht(run.get("created_at"))}  ·  Finished: {format_pht(run.get("finished_at"))}\n'
                       f'Gate: {run["gate_status"] or "Not evaluated"}  ·  '
                       f'Passed: {summary.get("passed", "—")}/{summary.get("total", "—")}  ·  '
                       f'Requests: {summary.get("requests", "—")}  ·  Error rate: {summary.get("error_rate", "—")} %')
            ctk.CTkLabel(card, text=details, justify="left", anchor="w", text_color=("#65758B", "#9BA9B8")).pack(fill="x", padx=12, pady=(0, 9))
