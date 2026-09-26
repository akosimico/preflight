"""Project management service with validation and active-project state."""
from __future__ import annotations
from typing import Any
from urllib.parse import urlparse
from database.repositories import ProjectsRepository, SettingsRepository

ENVIRONMENTS = ("Local", "Development", "Staging", "Production")

class ProjectService:
    def __init__(self, projects: ProjectsRepository, settings: SettingsRepository) -> None: self.projects=projects; self.settings=settings
    @staticmethod
    def validate(name: str, frontend_url: str, api_url: str, environment: str) -> None:
        if not name.strip(): raise ValueError("Project name is required.")
        if environment not in ENVIRONMENTS: raise ValueError("Choose a valid environment.")
        for label, url in (("Frontend URL",frontend_url),("API Base URL",api_url)):
            if url and (urlparse(url).scheme not in {"http","https"} or not urlparse(url).netloc): raise ValueError(f"{label} must be a complete http(s) URL.")
    def create(self, name: str, frontend_url: str, api_url: str, environment: str) -> dict[str, Any]:
        self.validate(name,frontend_url,api_url,environment); project=self.projects.create(name.strip(),frontend_url.strip(),api_url.strip(),environment); self.select(project["id"]); return project
    def update(self, project_id: int, name: str, frontend_url: str, api_url: str, environment: str) -> dict[str, Any]:
        self.validate(name,frontend_url,api_url,environment); project=self.projects.update(project_id,name=name.strip(),frontend_url=frontend_url.strip(),api_url=api_url.strip(),environment=environment)
        if project is None: raise ValueError("Project no longer exists.")
        return project
    def delete(self, project_id: int) -> bool:
        deleted=self.projects.delete(project_id)
        if deleted and self.settings.get("active_project_id") == project_id: self.settings.set("active_project_id",None)
        return deleted
    def select(self, project_id: int | None) -> None:
        if project_id is not None and self.projects.get(project_id) is None: raise ValueError("Project does not exist.")
        self.settings.set("active_project_id",project_id)
    def active(self) -> dict[str, Any] | None:
        project_id=self.settings.get("active_project_id")
        return self.projects.get(project_id) if project_id else None
