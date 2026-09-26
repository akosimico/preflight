"""Root window and view-routing for Preflight."""

from __future__ import annotations

import customtkinter as ctk

from gui.dashboard import DashboardView
from gui.sidebar import NAVIGATION_ITEMS, Sidebar


class PlaceholderView(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, name: str) -> None:
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(self, text=name, font=ctk.CTkFont(size=30, weight="bold")).pack(anchor="w", padx=28, pady=(30, 4))
        ctk.CTkLabel(self, text=f"{name} will be available in a later milestone.", text_color=("#65758B", "#9BA9B8")).pack(anchor="w", padx=28)


class PreflightApp(ctk.CTk):
    """The application shell; business logic is intentionally not owned here."""

    def __init__(self) -> None:
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        super().__init__()
        self.title("Preflight")
        self.geometry("1180x760")
        self.minsize(900, 600)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, self.show_view)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color=("#FFFFFF", "#101820"))
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        self.views: dict[str, ctk.CTkFrame] = {}
        self._build_views()
        self.current_view = ""
        self.show_view("Dashboard")

    def _build_views(self) -> None:
        for name in NAVIGATION_ITEMS:
            view = DashboardView(self.content) if name == "Dashboard" else PlaceholderView(self.content, name)
            view.grid(row=0, column=0, sticky="nsew")
            self.views[name] = view

    def show_view(self, view_name: str) -> None:
        if view_name not in self.views:
            raise ValueError(f"Unknown view: {view_name}")
        self.views[view_name].tkraise()
        self.current_view = view_name
        self.sidebar.set_active(view_name)

