from __future__ import annotations

from datetime import datetime

import customtkinter as ctk


class LogConsole(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, **kwargs: object) -> None:
        super().__init__(master, corner_radius=12, **kwargs)
        self.output = ctk.CTkTextbox(self, height=180, state="disabled", font=("Consolas", 12))
        self.output.pack(fill="both", expand=True, padx=10, pady=10)

    def write(self, message: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        self.output.configure(state="normal")
        self.output.insert("end", f"{stamp}  {message}\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def clear(self) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")

