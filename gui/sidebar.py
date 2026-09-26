"""Sidebar navigation for the main application shell."""

from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk


NAVIGATION_ITEMS = (
    "Dashboard",
    "Projects",
    "Discovery",
    "Test Suite",
    "Scenarios",
    "Reports",
    "History",
    "Settings",
)


class Sidebar(ctk.CTkFrame):
    """Persistent navigation with an accessible active-view indicator."""

    def __init__(self, master: ctk.CTkBaseClass, on_navigate: Callable[[str], None]) -> None:
        super().__init__(master, width=210, corner_radius=0, fg_color=("#F7F9FC", "#17212B"))
        self.grid_rowconfigure(10, weight=1)
        self._on_navigate = on_navigate
        self._buttons: dict[str, ctk.CTkButton] = {}

        ctk.CTkLabel(self, text="PREFLIGHT", font=ctk.CTkFont(size=22, weight="bold")).grid(
            row=0, column=0, padx=24, pady=(28, 2), sticky="w"
        )
        ctk.CTkLabel(self, text="DEPLOY WITH CONFIDENCE", text_color=("#65758B", "#9BA9B8"), font=ctk.CTkFont(size=10)).grid(
            row=1, column=0, padx=24, pady=(0, 24), sticky="w"
        )
        for row, name in enumerate(NAVIGATION_ITEMS, start=2):
            button = ctk.CTkButton(
                self,
                text=name,
                anchor="w",
                height=38,
                corner_radius=8,
                fg_color="transparent",
                hover_color=("#E3EAF4", "#273746"),
                command=lambda view=name: self._on_navigate(view),
            )
            button.grid(row=row, column=0, padx=12, pady=2, sticky="ew")
            self._buttons[name] = button

        self.project_label = ctk.CTkLabel(
            self, text="No project selected", anchor="w", text_color=("#65758B", "#9BA9B8"), wraplength=165
        )
        self.project_label.grid(row=11, column=0, padx=24, pady=(8, 24), sticky="ew")

    def set_active(self, view_name: str) -> None:
        for name, button in self._buttons.items():
            button.configure(fg_color=("#DCEBFF", "#1E4D7B") if name == view_name else "transparent")

    def set_project_name(self, name: str | None) -> None:
        self.project_label.configure(text=name or "No project selected")

