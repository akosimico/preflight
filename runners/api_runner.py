from __future__ import annotations
from dataclasses import dataclass
from time import perf_counter
from typing import Any
import httpx

@dataclass(frozen=True)
class ApiResult:
    passed: bool; status_code: int|None; duration_ms: float|None; error: str|None; response_text: str
def run_request(method:str,url:str,expected_status:int=200,body:Any=None,headers:dict[str,str]|None=None,timeout:float=10,assertions:dict[str,Any]|None=None)->ApiResult:
    started=perf_counter()
    try:
        response=httpx.request(method,url,json=body,headers=headers,timeout=timeout); elapsed=round((perf_counter()-started)*1000,1); errors=[]
        if response.status_code!=expected_status: errors.append(f"expected HTTP {expected_status}, got {response.status_code}")
        data=response.json() if "json" in response.headers.get("content-type","") else None
        for key,value in (assertions or {}).items():
            if key=="max_response_ms" and elapsed>value: errors.append(f"response took {elapsed} ms (limit {value} ms)")
            elif key=="contains" and str(value) not in response.text: errors.append(f"response does not contain {value!r}")
            elif key.startswith("json."):
                actual=data
                for part in key[5:].split("."): actual=actual.get(part) if isinstance(actual,dict) else None
                if actual!=value: errors.append(f"{key} expected {value!r}, got {actual!r}")
        return ApiResult(not errors,response.status_code,elapsed,"; ".join(errors) or None,response.text)
    except httpx.HTTPError as error: return ApiResult(False,None,None,str(error),"")

def expected_success_status(definition: dict[str, Any]) -> int:
    """Choose the first documented successful OpenAPI response, falling back to 200."""
    for status in definition.get("responses", {}):
        if str(status).isdigit() and 200 <= int(status) < 300:
            return int(status)
    return 200

def redact(value: Any) -> Any:
    """Prevent common credentials from appearing in persisted results or the GUI."""
    sensitive={"authorization","token","password","secret","api_key","x-api-key"}
    if isinstance(value,dict): return {key:("[REDACTED]" if key.lower() in sensitive else redact(item)) for key,item in value.items()}
    if isinstance(value,list): return [redact(item) for item in value]
    return value
