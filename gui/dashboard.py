from __future__ import annotations

import customtkinter as ctk

from gui.components.metric_card import MetricCard
from gui.components.status_card import StatusCard


class DashboardView(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkLabel(self, text="Dashboard", font=ctk.CTkFont(size=30, weight="bold")).grid(row=0, column=0, columnspan=3, padx=28, pady=(30, 4), sticky="w")
        ctk.CTkLabel(self, text="Start by creating a project and configuring its validation checks.", text_color=("#65758B", "#9BA9B8")).grid(row=1, column=0, columnspan=3, padx=28, pady=(0, 24), sticky="w")
        for column, (label, status) in enumerate((("API", "Not run"), ("Load", "Not run"), ("Security", "Not run"))):
            StatusCard(self, label, status).grid(row=2, column=column, padx=8 if column else 28, pady=8, sticky="ew")
        for column, label in enumerate(("Requests", "Average", "Errors")):
            MetricCard(self, label).grid(row=3, column=column, padx=8 if column else 28, pady=8, sticky="ew")
        self.run_button = ctk.CTkButton(self, text="RUN PREFLIGHT", height=42, state="disabled")
        self.run_button.grid(row=4, column=0, columnspan=3, padx=28, pady=28, sticky="ew")

