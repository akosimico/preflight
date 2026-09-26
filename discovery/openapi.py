from dataclasses import dataclass
from typing import Any
import httpx
@dataclass(frozen=True)
class DiscoveredEndpoint:
    method:str; path:str; tags:tuple[str,...]; destructive:bool; definition:dict[str,Any]
def parse_openapi(spec:dict[str,Any])->list[DiscoveredEndpoint]:
    return [DiscoveredEndpoint(method.upper(),path,tuple(data.get("tags",[])),method.lower() in {"put","patch","delete"},data) for path,item in spec.get("paths",{}).items() for method,data in item.items() if method.lower() in {"get","post","put","patch","delete","head","options"}]
def discover(base_url:str,timeout:float=5)->list[DiscoveredEndpoint]:
    response=httpx.get(base_url.rstrip("/")+"/openapi.json",timeout=timeout); response.raise_for_status(); return parse_openapi(response.json())
