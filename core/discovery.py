from database.repositories import EndpointsRepository
from discovery.openapi import discover
def discover_and_store(project_id:int,api_url:str,endpoints:EndpointsRepository):
    found=discover(api_url)
    for item in found:
        old=endpoints.list(project_id=project_id,method=item.method,path=item.path); values={"enabled":True,"is_destructive":item.destructive,"definition_json":item.definition}
        endpoints.update(old[0]["id"],**values) if old else endpoints.create(project_id,item.method,item.path,**values)
    return found
