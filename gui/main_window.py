"""Root window and view-routing for Preflight."""

from __future__ import annotations

import ctypes
import sys
from pathlib import Path
import customtkinter as ctk

from gui.dashboard import DashboardView
from gui.projects_view import ProjectsView
from gui.discovery_view import DiscoveryView
from gui.test_suite_view import TestSuiteView
from gui.load_view import LoadView
from gui.gates_view import GatesView
from gui.history_view import HistoryView
from gui.reports_view import ReportsView
from gui.security_view import SecurityView
from gui.sidebar import NAVIGATION_ITEMS, Sidebar
from database.database import Database
from database.repositories import (
    EndpointsRepository,
    ProjectsRepository,
    SettingsRepository,
    TestResultsRepository,
    TestRunsRepository,
    LoadMetricsRepository,
    SecurityFindingsRepository,
)
from core.projects import ProjectService


def set_windows_app_id() -> None:
    """Give the running Python process its own Windows taskbar identity."""
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Preflight.Desktop.1")


class PlaceholderView(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, name: str) -> None:
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(self, text=name, font=ctk.CTkFont(size=30, weight="bold")).pack(
            anchor="w", padx=28, pady=(30, 4)
        )
        ctk.CTkLabel(
            self,
            text=f"{name} will be available in a later milestone.",
            text_color=("#65758B", "#9BA9B8"),
        ).pack(anchor="w", padx=28)


class PreflightApp(ctk.CTk):
    """The application shell; business logic is intentionally not owned here."""

    def __init__(self) -> None:
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        set_windows_app_id()
        super().__init__()

        icon_path = Path(__file__).resolve().parent.parent / "assets" / "preflight.ico"
        self.iconbitmap(str(icon_path))
        self.title("Preflight")
        self.geometry("1180x760")
        self.minsize(900, 600)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        database = Database()
        self.project_service = ProjectService(
            ProjectsRepository(database), SettingsRepository(database)
        )
        self.endpoints_repository = EndpointsRepository(database)
        self.runs_repository = TestRunsRepository(database)
        self.results_repository = TestResultsRepository(database)
        self.metrics_repository = LoadMetricsRepository(database)
        self.findings_repository = SecurityFindingsRepository(database)
        self.sidebar = Sidebar(self, self.show_view)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        active_project = self.project_service.active()
        self.sidebar.set_project_name(
            active_project["name"] if active_project else None
        )
        self.content = ctk.CTkFrame(
            self, corner_radius=0, fg_color=("#FFFFFF", "#101820")
        )
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        self.views: dict[str, ctk.CTkFrame] = {}
        self._build_views()
        self.current_view = ""
        self.show_view("Dashboard")

    def _build_views(self) -> None:
        for name in NAVIGATION_ITEMS:
            view = (
                DashboardView(
                    self.content,
                    self.project_service,
                    self.runs_repository,
                    self.metrics_repository,
                    self.findings_repository,
                    lambda: self.show_view("Test Suite"),
                )
                if name == "Dashboard"
                else (
                    ProjectsView(
                        self.content,
                        self.project_service,
                        self.sidebar.set_project_name,
                    )
                    if name == "Projects"
                    else (
                        DiscoveryView(
                            self.content,
                            self.project_service,
                            self.endpoints_repository,
                        )
                        if name == "Discovery"
                        else (
                            TestSuiteView(
                                self.content,
                                self.project_service,
                                self.endpoints_repository,
                                self.runs_repository,
                                self.results_repository,
                            )
                            if name == "Test Suite"
                            else (
                                LoadView(
                                    self.content,
                                    self.project_service,
                                    self.runs_repository,
                                    self.metrics_repository,
                                )
                                if name == "Scenarios"
                                else (
                                    SecurityView(
                                        self.content,
                                        self.project_service,
                                        self.runs_repository,
                                        self.findings_repository,
                                    )
                                    if name == "Security"
                                    else (
                                        GatesView(
                                            self.content,
                                            self.project_service,
                                            self.runs_repository,
                                            self.project_service.settings,
                                        )
                                        if name == "Deployment Gates"
                                        else (
                                            HistoryView(
                                                self.content,
                                                self.project_service,
                                                self.runs_repository,
                                            )
                                            if name == "History"
                                            else (
                                                ReportsView(
                                                    self.content,
                                                    self.project_service,
                                                    self.runs_repository,
                                                    self.results_repository,
                                                    self.metrics_repository,
                                                )
                                                if name == "Reports"
                                                else PlaceholderView(self.content, name)
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
            view.grid(row=0, column=0, sticky="nsew")
            self.views[name] = view

    def show_view(self, view_name: str) -> None:
        if view_name not in self.views:
            raise ValueError(f"Unknown view: {view_name}")
        self.views[view_name].tkraise()
        refresh = getattr(self.views[view_name], "refresh", None)
        if refresh:
            refresh()
        self.current_view = view_name
        self.sidebar.set_active(view_name)
