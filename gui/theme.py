"""Shared visual tokens for Preflight's refined dark desktop UI."""
from __future__ import annotations

BG = ("#F5F7FB", "#0B141D")
SURFACE = ("#FFFFFF", "#14212C")
SURFACE_ALT = ("#EDF2F7", "#1B2A36")
MUTED = ("#5F7185", "#9FB0C2")
PRIMARY = ("#1976C2", "#2B7FC0")
SUCCESS = ("#218A5A", "#46B77A")
WARNING = ("#9A6700", "#E0A93B")
DANGER = ("#B33A3A", "#E06A6A")
INFO = ("#356EA6", "#78AEE8")

STATUS_COLORS = {"PASSED": SUCCESS, "FAILED": DANGER, "SKIPPED": WARNING, "HIGH": DANGER, "MEDIUM": WARNING, "LOW": WARNING, "INFO": INFO}
