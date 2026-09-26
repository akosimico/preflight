"""OpenAPI parameter normalization and safe baseline request values."""
from __future__ import annotations
from typing import Any
from urllib.parse import quote, urlencode

def safe_value(parameter: dict[str, Any]) -> str | None:
    schema = parameter.get("schema", {})
    for source in (parameter, schema):
        if source.get("example") is not None: return str(source["example"])
        if source.get("default") is not None: return str(source["default"])
        if source.get("enum"): return str(source["enum"][0])
    if parameter.get("in") == "path": return None
    kind=schema.get("type", "string"); fmt=schema.get("format")
    if fmt == "email": return "preflight@example.test"
    if fmt == "uuid": return "00000000-0000-4000-8000-000000000001"
    return {"integer":"1","number":"1","boolean":"true"}.get(kind,"preflight_test")

def request_path(path: str, definition: dict[str, Any]) -> tuple[str | None, dict[str, str]]:
    query: dict[str,str] = {}
    for parameter in definition.get("parameters", []):
        value=safe_value(parameter);location=parameter.get("in");name=parameter.get("name","")
        if location == "path":
            if value is None: return None, {}
            path=path.replace("{"+name+"}",quote(value,safe=""))
        elif location == "query" and value is not None: query[name]=value
    return path,query

def url_for(base_url: str, path: str, definition: dict[str, Any]) -> str | None:
    path,query=request_path(path,definition)
    if path is None:return None
    result=base_url.rstrip("/")+path
    return result+("?"+urlencode(query) if query else "")

def baseline_body(definition: dict[str, Any]) -> Any:
    """Build a conservative JSON example from a discovered request schema.

    It is intended for non-destructive baseline API checks, not as realistic
    production data.  If the OpenAPI operation has no JSON body, ``None`` is
    returned and callers send no body.
    """
    request_body = definition.get("requestBody") or {}
    content = request_body.get("content") or {}
    media_type = next((key for key in content if "json" in key.lower()), None)
    if not media_type:
        return None
    return _schema_value(content[media_type].get("schema") or {})

def _schema_value(schema: dict[str, Any]) -> Any:
    if schema.get("example") is not None:
        return schema["example"]
    if schema.get("default") is not None:
        return schema["default"]
    if schema.get("enum"):
        return schema["enum"][0]
    kind = schema.get("type")
    if kind == "object" or schema.get("properties"):
        return {name: _schema_value(value) for name, value in schema.get("properties", {}).items()}
    if kind == "array":
        return [_schema_value(schema.get("items") or {})]
    if kind == "integer":
        return 1
    if kind == "number":
        return 1.0
    if kind == "boolean":
        return False
    return "preflight-test"
