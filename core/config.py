from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from database.repositories import SettingsRepository
DEFAULT_CONFIG_PATH=Path("config")/"default.json"
DEFAULT_SETTINGS: dict[str, Any]={"theme":"system","active_project_id":None}
def ensure_default_config(path: str | Path=DEFAULT_CONFIG_PATH) -> Path:
    target=Path(path); target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists(): target.write_text(json.dumps(DEFAULT_SETTINGS,indent=2)+"\n",encoding="utf-8")
    return target
class Settings:
    def __init__(self, repository: SettingsRepository) -> None: self.repository=repository
    def get(self,key: str) -> Any: return self.repository.get(key,DEFAULT_SETTINGS.get(key))
    def set(self,key: str,value: Any) -> None: self.repository.set(key,value)
