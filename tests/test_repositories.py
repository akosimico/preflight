from database.database import Database
from database.repositories import EndpointsRepository, LoadMetricsRepository, ProjectsRepository, ScenariosRepository, SecurityFindingsRepository, SettingsRepository, TestResultsRepository, TestRunsRepository

def test_database_initializes_all_planned_tables(tmp_path):
    db=Database(tmp_path/"storage"/"preflight.db"); db.initialize()
    with db.connection() as c: names={row[0] for row in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"projects","endpoints","scenarios","test_runs","test_results","load_metrics","security_findings","settings"} <= names
def test_repositories_crud_and_cascades(tmp_path):
    db=Database(tmp_path/"preflight.db"); project=ProjectsRepository(db).create("Demo",api_url="http://localhost:8000")
    assert ProjectsRepository(db).update(project["id"],name="Renamed")["name"]=="Renamed"
    endpoint=EndpointsRepository(db).create(project["id"],"get","/health",definition_json={"responses":[200]}); scenario=ScenariosRepository(db).create(project["id"],"Smoke",[{"path":"/health"}]); run=TestRunsRepository(db).create(project["id"],status="RUNNING")
    result=TestResultsRepository(db).create(run["id"],"GET /health","PASSED",endpoint_id=endpoint["id"]); metric=LoadMetricsRepository(db).create(run["id"],users=10,rps=12.5); finding=SecurityFindingsRepository(db).create(run["id"],"LOW","Header missing")
    assert endpoint["definition_json"]=={"responses":[200]} and scenario["steps_json"]==[{"path":"/health"}] and result["status"]=="PASSED" and metric["users"]==10 and finding["title"]=="Header missing"
    assert ProjectsRepository(db).delete(project["id"]) and TestRunsRepository(db).get(run["id"]) is None
def test_settings_persist_typed_values(tmp_path):
    settings=SettingsRepository(Database(tmp_path/"preflight.db")); settings.set("active_project_id",3); settings.set("enabled_suites",["api","load"])
    assert settings.get("active_project_id")==3 and settings.get("enabled_suites")==["api","load"] and settings.get("unknown","fallback")=="fallback"
