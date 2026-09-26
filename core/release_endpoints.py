"""Choose safe discovered endpoints that contribute to release-gate load metrics."""
from __future__ import annotations
from core.parameters import url_for

# Fixtures remain available to the API and Security screens, but their
# deliberately bad behaviour must never decide production release readiness.
EXCLUDED_RELEASE_GATE_TAGS={"preflight-test-fixture","preflight-security-fixture"}

def include_in_release_gate(endpoint:dict)->bool:
    tags=set(endpoint.get("definition_json",{}).get("tags",[]))
    return not bool(tags & EXCLUDED_RELEASE_GATE_TAGS)

def release_urls(api_url:str,endpoints:list[dict])->list[str]:
    urls=[]
    for endpoint in endpoints:
        if not endpoint.get("enabled",True) or endpoint.get("method")!="GET" or not include_in_release_gate(endpoint):continue
        target=url_for(api_url,endpoint["path"],endpoint.get("definition_json",{}))
        if target:urls.append(target)
    return urls
