from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk


class EndpointRow(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, method: str, path: str, enabled: bool = True, command: Callable[[], None] | None = None, **kwargs: object) -> None:
        super().__init__(master, corner_radius=8, **kwargs)
        self.enabled = ctk.BooleanVar(value=enabled)
        ctk.CTkCheckBox(self, text="", variable=self.enabled, width=24, command=command).pack(side="left", padx=(12, 8), pady=8)
        ctk.CTkLabel(self, text=method.upper(), width=58, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(self, text=path, anchor="w").pack(side="left", fill="x", expand=True, padx=(0, 12))

