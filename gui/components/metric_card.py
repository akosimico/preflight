from __future__ import annotations

import customtkinter as ctk


class MetricCard(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, label: str, value: str = "—", **kwargs: object) -> None:
        super().__init__(master, corner_radius=12, **kwargs)
        ctk.CTkLabel(self, text=label.upper(), text_color=("#65758B", "#9BA9B8"), font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=16, pady=(14, 2))
        self.value_label = ctk.CTkLabel(self, text=value, font=ctk.CTkFont(size=24, weight="bold"))
        self.value_label.pack(anchor="w", padx=16, pady=(0, 14))

    def set_value(self, value: str) -> None:
        self.value_label.configure(text=value)

