from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

import httpx

MAX_RESPONSE_CHARS = 20_000


@dataclass(frozen=True)
class ApiResult:
    passed: bool
    status_code: int | None
    duration_ms: float | None
    error: str | None
    response_text: str


def run_request(
    method: str,
    url: str,
    expected_status: int = 200,
    body: Any = None,
    headers: dict[str, str] | None = None,
    timeout: float = 10,
    assertions: dict[str, Any] | None = None,
    client: httpx.Client | None = None,
) -> ApiResult:
    """
    Execute one API request and measure HTTP request latency.

    A shared httpx.Client can be supplied by callers running multiple
    requests. If no client is supplied, a temporary client is created.

    trust_env=False prevents system/environment proxy configuration from
    interfering with local API measurements.
    """

    owns_client = client is None

    if client is None:
        client = httpx.Client(
            timeout=timeout,
            trust_env=False,
        )

    try:
        # ---------------------------------------------------------
        # Start timing immediately before the HTTP request.
        # ---------------------------------------------------------

        started = perf_counter()

        response = client.request(
            method=method,
            url=url,
            json=body,
            headers=headers,
        )

        # ---------------------------------------------------------
        # Stop timing immediately after the response is received.
        # ---------------------------------------------------------

        elapsed = round(
            (perf_counter() - started) * 1000,
            1,
        )

        errors: list[str] = []

        # ---------------------------------------------------------
        # Status assertion
        # ---------------------------------------------------------

        if response.status_code != expected_status:
            errors.append(
                f"expected HTTP {expected_status}, " f"got {response.status_code}"
            )

        # ---------------------------------------------------------
        # Parse JSON only AFTER timing has finished.
        # ---------------------------------------------------------

        data = None

        content_type = response.headers.get(
            "content-type",
            "",
        ).lower()

        if "json" in content_type:
            try:
                data = response.json()
            except ValueError:
                data = None

        # ---------------------------------------------------------
        # Additional assertions
        # ---------------------------------------------------------

        for key, value in (assertions or {}).items():

            if key == "max_response_ms":
                if elapsed > float(value):
                    errors.append(f"response took {elapsed} ms " f"(limit {value} ms)")

            elif key == "contains":
                if str(value) not in response.text:
                    errors.append(f"response does not contain {value!r}")

            elif key.startswith("json."):
                actual = data

                for part in key[5:].split("."):
                    if isinstance(actual, dict):
                        actual = actual.get(part)
                    else:
                        actual = None
                        break

                if actual != value:
                    errors.append(f"{key} expected {value!r}, " f"got {actual!r}")

        return ApiResult(
            passed=not errors,
            status_code=response.status_code,
            duration_ms=elapsed,
            error="; ".join(errors) or None,
            response_text=response.text,
        )

    except httpx.TimeoutException as error:
        return ApiResult(
            passed=False,
            status_code=None,
            duration_ms=None,
            error=f"Request timed out: {error}",
            response_text="",
        )

    except httpx.HTTPError as error:
        return ApiResult(
            passed=False,
            status_code=None,
            duration_ms=None,
            error=str(error),
            response_text="",
        )

    finally:
        if owns_client:
            client.close()


def expected_success_status(
    definition: dict[str, Any],
) -> int:
    """
    Choose the first documented successful OpenAPI response,
    falling back to HTTP 200.
    """

    for status in definition.get("responses", {}):
        if str(status).isdigit() and 200 <= int(status) < 300:
            return int(status)

    return 200


def redact(value: Any) -> Any:
    """
    Prevent common credentials from appearing in persisted
    results or the GUI.
    """

    sensitive = {
        "authorization",
        "token",
        "password",
        "secret",
        "api_key",
        "x-api-key",
    }

    if isinstance(value, dict):
        return {
            key: ("[REDACTED]" if key.lower() in sensitive else redact(item))
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [redact(item) for item in value]

    return value


def prepare_response(value: str) -> str:
    """
    Redact JSON responses when possible and cap local
    diagnostic storage.
    """

    try:
        import json

        value = json.dumps(
            redact(json.loads(value)),
            indent=2,
            ensure_ascii=False,
        )

    except (ValueError, TypeError):
        pass

    if len(value) > MAX_RESPONSE_CHARS:
        return (
            value[:MAX_RESPONSE_CHARS] + f"\n\n[Response truncated after "
            f"{MAX_RESPONSE_CHARS:,} characters]"
        )

    return value
