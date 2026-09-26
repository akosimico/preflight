from dataclasses import dataclass
from typing import Any
@dataclass(frozen=True)
class Event:
    kind:str; payload:dict[str,Any]
