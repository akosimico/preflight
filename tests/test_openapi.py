from discovery.openapi import parse_openapi
from core.parameters import baseline_body
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

def test_parse_openapi_merges_and_resolves_parameters():
    spec={"components":{"parameters":{"Query":{"name":"q","in":"query","schema":{"type":"string","default":"ok"}}}},"paths":{"/items/{id}":{"parameters":[{"name":"id","in":"path","schema":{"type":"integer","example":7}}],"get":{"parameters":[{"$ref":"#/components/parameters/Query"}]}}}}
    endpoint=parse_openapi(spec)[0]
    assert {(item["name"],item["in"]) for item in endpoint.definition["parameters"]} == {("id","path"),("q","query")}

def test_parse_openapi_resolves_request_body_schema_for_baseline_requests():
    spec={"components":{"schemas":{"Task":{"type":"object","properties":{"title":{"type":"string"},"completed":{"type":"boolean","default":False}}}}},"paths":{"/tasks":{"post":{"requestBody":{"content":{"application/json":{"schema":{"$ref":"#/components/schemas/Task"}}}}}}}}
    endpoint=parse_openapi(spec)[0]
    assert baseline_body(endpoint.definition)=={"title":"preflight-test","completed":False}
