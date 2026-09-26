from __future__ import annotations
import json
import tkinter as tk
import customtkinter as ctk
from gui.theme import MUTED, STATUS_COLORS, SURFACE_ALT


class ExpandableResult(ctk.CTkFrame):
    """A compact result summary that reveals diagnostic content when clicked."""
    def __init__(self, master, title: str, status: str, summary: str = "", details: list[tuple[str, object]] | None = None, response: str | None = None, **kwargs):
        super().__init__(master, corner_radius=10, **kwargs)
        self.details, self.response, self.expanded = details or [], response, False
        self.header = ctk.CTkFrame(self, fg_color="transparent", cursor="hand2")
        self.header.pack(fill="x", padx=3, pady=3)
        self.header.grid_columnconfigure(1, weight=1)
        color = STATUS_COLORS.get(status, MUTED)
        ctk.CTkLabel(self.header, text=status, width=78, text_color=color, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=(8, 8), pady=8)
        ctk.CTkLabel(self.header, text=title, anchor="w").grid(row=0, column=1, sticky="ew", pady=8)
        ctk.CTkLabel(self.header, text=summary, width=230, anchor="w", text_color=MUTED, wraplength=230).grid(row=0, column=2, padx=8)
        self.hint = ctk.CTkLabel(self.header, text="View details ›", width=90, text_color=MUTED)
        self.hint.grid(row=0, column=3, padx=(0, 8))
        self.detail_frame = ctk.CTkFrame(self, fg_color=SURFACE_ALT, corner_radius=8)
        for widget in (self.header, *self.header.winfo_children()): widget.bind("<Button-1>", lambda _: self.toggle())

    def toggle(self):
        self.expanded = not self.expanded
        self.hint.configure(text="Hide details ˅" if self.expanded else "View details ›")
        if self.expanded:
            self.render_details(); self.detail_frame.pack(fill="x", padx=10, pady=(0, 10))
        else: self.detail_frame.pack_forget()

    def render_details(self):
        if self.detail_frame.winfo_children(): return
        for label, value in self.details:
            row = ctk.CTkFrame(self.detail_frame, fg_color="transparent"); row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(row, text=f"{label}:", width=150, anchor="w", text_color=MUTED).pack(side="left")
            ctk.CTkLabel(row, text=str(value if value not in (None, "") else "Not recorded"), anchor="w", justify="left", wraplength=620).pack(side="left", fill="x", expand=True)
        if self.response is not None:
            ctk.CTkLabel(self.detail_frame, text="Response body", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 3))
            box = ctk.CTkTextbox(self.detail_frame, height=140, font=("Consolas", 11)); box.pack(fill="x", padx=10, pady=(0, 6)); box.insert("1.0", self.response or "No response body was returned."); box.configure(state="disabled")
            ctk.CTkButton(self.detail_frame, text="COPY RESPONSE", width=130, fg_color="transparent", border_width=1, command=lambda: self.clipboard_append(self.response or "")).pack(anchor="e", padx=10, pady=(0, 10))
