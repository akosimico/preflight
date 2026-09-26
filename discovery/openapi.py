from dataclasses import dataclass
from typing import Any
import httpx
@dataclass(frozen=True)
class DiscoveredEndpoint: method:str; path:str; tags:tuple[str,...]; destructive:bool; definition:dict[str,Any]
def _resolve(value:dict[str,Any],spec:dict[str,Any])->dict[str,Any]:
    ref=value.get("$ref","")
    if not ref.startswith("#/components/"):return value
    target:Any=spec
    for part in ref[2:].split("/"):target=target.get(part,{})
    return {**target,**{key:item for key,item in value.items() if key!="$ref"}}
def _parameters(path_item,operation,spec):
    merged={}
    for raw in [*path_item.get("parameters",[]),*operation.get("parameters",[])]:
        param=_resolve(raw,spec);param={**param,"schema":_resolve(param.get("schema",{}),spec)};merged[(param.get("name"),param.get("in"))]=param
    return list(merged.values())

def _request_body(operation,spec):
    body=_resolve(operation.get("requestBody",{}),spec)
    content={}
    for media_type,item in body.get("content",{}).items():
        content[media_type]={**item,"schema":_resolve(item.get("schema",{}),spec)}
    return {**body,"content":content} if body else {}
def parse_openapi(spec:dict[str,Any])->list[DiscoveredEndpoint]:
    found=[]
    for path,item in spec.get("paths",{}).items():
      for method,data in item.items():
        if method.lower() not in {"get","post","put","patch","delete","head","options"}:continue
        found.append(DiscoveredEndpoint(method.upper(),path,tuple(data.get("tags",[])),method.lower() in {"put","patch","delete"},{**data,"parameters":_parameters(item,data,spec),"requestBody":_request_body(data,spec)}))
    return found
def discover(base_url:str,timeout:float=5)->list[DiscoveredEndpoint]:
    response=httpx.get(base_url.rstrip("/")+"/openapi.json",timeout=timeout);response.raise_for_status();return parse_openapi(response.json())
