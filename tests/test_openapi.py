from discovery.openapi import parse_openapi
from database.database import Database
from database.repositories import EndpointsRepository, ProjectsRepository, SettingsRepository
from core.projects import ProjectService
def test_parse_openapi_extracts_methods_and_destructive_flag():
    result=parse_openapi({"paths":{"/rooms":{"get":{"tags":["rooms"]},"delete":{}}}})
    assert [(item.method,item.path,item.destructive) for item in result]==[("GET","/rooms",False),("DELETE","/rooms",True)]

def test_endpoint_selection_is_persisted(tmp_path):
    db=Database(tmp_path/"preflight.db"); project=ProjectsRepository(db).create("Demo")
    endpoint=EndpointsRepository(db).create(project["id"],"DELETE","/rooms",enabled=True,is_destructive=True)
    EndpointsRepository(db).update(endpoint["id"],enabled=False)
    assert EndpointsRepository(db).get(endpoint["id"])["enabled"] is False
