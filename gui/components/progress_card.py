from __future__ import annotations

import customtkinter as ctk


class ProgressCard(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, label: str, **kwargs: object) -> None:
        super().__init__(master, corner_radius=12, **kwargs)
        ctk.CTkLabel(self, text=label, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=16, pady=(14, 8))
        self.bar = ctk.CTkProgressBar(self)
        self.bar.pack(fill="x", padx=16, pady=(0, 14))
        self.bar.set(0)

    def set_progress(self, value: float) -> None:
        self.bar.set(max(0.0, min(1.0, value)))

