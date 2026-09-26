"""Safe, non-intrusive HTTP security configuration checks."""
from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import urlparse
import httpx

@dataclass(frozen=True)
class SecurityFinding:
    severity: str
    title: str
    detail: str

RECOMMENDED_HEADERS = {
    "content-security-policy": ("MEDIUM", "Content-Security-Policy header is missing", "Helps browsers limit which content the page may load."),
    "x-content-type-options": ("LOW", "X-Content-Type-Options header is missing", "Use 'nosniff' to reduce content-type sniffing."),
    "x-frame-options": ("LOW", "X-Frame-Options header is missing", "Helps protect browser pages from clickjacking."),
    "referrer-policy": ("LOW", "Referrer-Policy header is missing", "Controls which referrer information browsers share."),
    "permissions-policy": ("LOW", "Permissions-Policy header is missing", "Limits access to browser features such as camera and microphone."),
}

def inspect_headers(url: str, timeout: float = 10) -> tuple[int | None, list[SecurityFinding]]:
    """Fetch a URL once and return only passive configuration findings."""
    findings: list[SecurityFinding] = []
    try:
        response = httpx.get(url, timeout=timeout, follow_redirects=True)
    except httpx.HTTPError as error:
        return None, [SecurityFinding("HIGH", "Security check could not reach the API", str(error))]
    headers = {key.lower(): value for key, value in response.headers.items()}
    if urlparse(url).scheme != "https":
        findings.append(SecurityFinding("MEDIUM", "API is not using HTTPS", "Use HTTPS in staging and production so traffic is encrypted in transit."))
    elif "strict-transport-security" not in headers:
        findings.append(SecurityFinding("LOW", "Strict-Transport-Security header is missing", "Tell browsers to use HTTPS for future visits."))
    for header, (severity, title, detail) in RECOMMENDED_HEADERS.items():
        if header not in headers:
            findings.append(SecurityFinding(severity, title, detail))
    origin = headers.get("access-control-allow-origin")
    credentials = headers.get("access-control-allow-credentials", "").lower() == "true"
    if origin == "*":
        severity = "HIGH" if credentials else "MEDIUM"
        findings.append(SecurityFinding(severity, "CORS allows every origin", "Review whether any website should be allowed to call this API."))
    for cookie in response.headers.get_list("set-cookie"):
        lowered=cookie.lower(); missing=[]
        if "secure" not in lowered: missing.append("Secure")
        if "httponly" not in lowered: missing.append("HttpOnly")
        if "samesite" not in lowered: missing.append("SameSite")
        if missing: findings.append(SecurityFinding("MEDIUM", "Cookie is missing security flags", f"A response cookie is missing: {', '.join(missing)}."))
    if "server" in headers:
        findings.append(SecurityFinding("INFO", "Server technology header is exposed", f"The response includes Server: {headers['server']}."))
    return response.status_code, findings
