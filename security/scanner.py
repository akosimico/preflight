"""Controlled, non-destructive active checks for authorized non-production APIs."""
from __future__ import annotations
from dataclasses import dataclass
from threading import Event
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from uuid import uuid4
import httpx
from core.parameters import url_for

MAX_RESPONSE_BYTES=256*1024
@dataclass(frozen=True)
class ActiveFinding: severity:str; title:str; target:str; details:dict
def _same_host(base,url):return urlparse(base).netloc.lower()==urlparse(url).netloc.lower()
def _finding(severity,title,target,endpoint,details):
 return ActiveFinding(severity,title,target,{"scan_type":"active","confidence":"medium","method":endpoint["method"],"endpoint":endpoint["path"],**details})
def _replace_query(url,name,value):
 parts=list(urlparse(url));query=dict(parse_qsl(parts[4],keep_blank_values=True));query[name]=value;parts[4]=urlencode(query);return urlunparse(parts)
def _text(response):return response.content[:MAX_RESPONSE_BYTES].decode(response.encoding or "utf-8",errors="replace")

def active_scan(base_url,endpoints,cancel:Event|None=None,progress=lambda *_:None,environment="Local"):
 if environment=="Production":return [],0
 cancel=cancel or Event();findings=[];requests=0;eligible=[item for item in endpoints if item["method"]=="GET"]
 with httpx.Client(timeout=5,follow_redirects=False) as client:
  for index,endpoint in enumerate(eligible,1):
   if cancel.is_set():break
   definition=endpoint["definition_json"];baseline_url=url_for(base_url,endpoint["path"],definition)
   if not baseline_url or not _same_host(base_url,baseline_url):continue
   progress(index,len(eligible),endpoint["method"]+" "+endpoint["path"],requests,len(findings))
   try: baseline=client.get(baseline_url);requests+=1
   except httpx.HTTPError:continue
   body=_text(baseline);content=baseline.headers.get("content-type","").lower();params=definition.get("parameters",[])
   if baseline.status_code>=500 and any(token in body.lower() for token in ("traceback", "stack trace", "sqlalchemy", "exception at")):
    findings.append(_finding("MEDIUM","Sensitive error details exposed",baseline_url,endpoint,{"cwe":"CWE-209","description":"The response exposes implementation error details.","evidence":body[:500],"remediation":"Return generic client errors and keep stack traces in server-side logs only.","status_code":baseline.status_code}))
   for parameter in params:
    if cancel.is_set():break
    if parameter.get("in")!="query" or parameter.get("schema",{}).get("type","string")!="string":continue
    name=parameter.get("name","").lower()
    if name in {"next","url","redirect","return","return_url","continue"}:
     probe=_replace_query(baseline_url,parameter["name"],"https://preflight.invalid/redirect-check")
     try: response=client.get(probe);requests+=1
     except httpx.HTTPError:continue
     location=response.headers.get("location","")
     if response.is_redirect and location.startswith("https://preflight.invalid"):
      findings.append(_finding("MEDIUM","Open redirect candidate",probe,endpoint,{"cwe":"CWE-601","parameter":parameter["name"],"description":"The server returned a redirect to a supplied external URL.","evidence":f"Location: {location}","remediation":"Allow-list redirect destinations or use server-side route identifiers.","status_code":response.status_code}))
    if name in {"file","filename","name","path","filepath","document","download","template"}:
     marker="preflight-traversal-"+uuid4().hex[:10];probe=_replace_query(baseline_url,parameter["name"],"../"+marker)
     try: response=client.get(probe);requests+=1
     except httpx.HTTPError:continue
     probe_body=_text(response)
     # A candidate needs explicit evidence, never merely a 200 status.
     if response.is_success and marker in probe_body and "file not found" not in probe_body.lower():
      findings.append(_finding("MEDIUM","Path traversal handling candidate",probe,endpoint,{"cwe":"CWE-22","parameter":parameter["name"],"description":"A controlled parent-directory path influenced a successful response. Manual review is required.","evidence":probe_body[:500],"remediation":"Resolve paths and verify they remain under the intended base directory.","status_code":response.status_code}))
    marker="PREFLIGHTXSS"+uuid4().hex[:12].upper();probe=_replace_query(baseline_url,parameter["name"],marker)
    try: response=client.get(probe);requests+=1
    except httpx.HTTPError:continue
    probe_body=_text(response)
    if marker in probe_body and marker not in body and ("text/html" in content or "application/xhtml" in content):
     at=probe_body.find(marker);findings.append(_finding("MEDIUM","Potential reflected input (XSS candidate)",probe,endpoint,{"cwe":"CWE-79","parameter":parameter["name"],"description":"A unique inert marker was reflected verbatim in an HTML response. This is a candidate, not confirmation of executable XSS.","evidence":probe_body[max(0,at-100):at+len(marker)+100],"remediation":"Apply context-aware output encoding before inserting untrusted input into HTML.","status_code":response.status_code}))
  # OPTIONS is non-state-changing and only records advertised methods for review.
  for endpoint in eligible:
   if cancel.is_set():break
   target=url_for(base_url,endpoint["path"],endpoint["definition_json"])
   if not target or not _same_host(base_url,target):continue
   try: response=client.options(target);requests+=1
   except httpx.HTTPError:continue
   allowed=response.headers.get("allow","")
   if allowed:
    findings.append(_finding("INFO","HTTP methods advertised",target,endpoint,{"cwe":"","description":"The endpoint advertises HTTP methods for review.","evidence":f"Allow: {allowed}","remediation":"Ensure only intended methods are enabled for this endpoint.","status_code":response.status_code,"confidence":"high"}))
 return findings,requests
