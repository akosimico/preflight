from __future__ import annotations

import customtkinter as ctk


class StatusCard(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, label: str, status: str = "Not run", **kwargs: object) -> None:
        super().__init__(master, corner_radius=12, **kwargs)
        ctk.CTkLabel(self, text=label, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=16, pady=(14, 2))
        self.status_label = ctk.CTkLabel(self, text=status, text_color=("#65758B", "#9BA9B8"))
        self.status_label.pack(anchor="w", padx=16, pady=(0, 14))

    def set_status(self, status: str) -> None:
        self.status_label.configure(text=status)

