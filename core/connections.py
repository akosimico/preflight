"""Non-GUI reachability checks for configured application targets."""
from __future__ import annotations
from dataclasses import dataclass
from time import perf_counter
import httpx

@dataclass(frozen=True)
class ConnectionResult:
    target: str
    reachable: bool
    status_code: int | None
    elapsed_ms: float | None
    message: str

def check_target(target: str, timeout: float = 5.0) -> ConnectionResult:
    if not target: return ConnectionResult(target, False, None, None, "No URL configured.")
    started=perf_counter()
    try:
        response=httpx.get(target,timeout=timeout,follow_redirects=True)
        elapsed=round((perf_counter()-started)*1000,1)
        return ConnectionResult(target,True,response.status_code,elapsed,f"HTTP {response.status_code} in {elapsed} ms")
    except httpx.ConnectError: return ConnectionResult(target,False,None,None,"Connection refused. Check that the target is running and its port is correct.")
    except httpx.TimeoutException: return ConnectionResult(target,False,None,None,"Connection timed out. Check the URL, network, or firewall.")
    except httpx.HTTPError as error: return ConnectionResult(target,False,None,None,f"Request failed: {error}")

def check_project(frontend_url: str, api_url: str, timeout: float = 5.0) -> dict[str, ConnectionResult]:
    return {"frontend":check_target(frontend_url,timeout),"api":check_target(api_url,timeout)}
