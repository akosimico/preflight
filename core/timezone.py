"""Display helpers for timestamps stored by SQLite in UTC."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone

# Philippine Time is UTC+08:00 year-round. A fixed offset keeps the desktop
# app self-contained on Windows installations without the optional tzdata set.
PHT = timezone(timedelta(hours=8), name="PHT")

def format_pht(value: str | None) -> str:
    if not value:
        return "Not recorded"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(PHT).strftime("%d %b %Y, %I:%M:%S %p PHT")
    except ValueError:
        return value
