# Preflight

**A local desktop app for deciding whether an API is ready to deploy.**

Preflight combines OpenAPI discovery, API checks, load testing, passive and controlled active security checks, release gates, run history, and shareable reports in one CustomTkinter application.

> Preflight is a local validation tool. It does not deploy your application and does not replace a professional security assessment.

## Features

| Area | What it does |
| --- | --- |
| Projects | Stores API targets, environment, and the active project. |
| Discovery | Reads `<API URL>/openapi.json` and saves endpoints with parameter and request-body definitions. |
| API Test Suite | Runs enabled endpoints, safely fills documented parameter values, creates baseline JSON bodies where possible, and saves expandable request details. |
| Load Testing | Simulates concurrent users against eligible `GET` endpoints and records RPS, latency percentiles, and error rate. |
| Security | Provides a passive configuration review plus an opt-in controlled active scan. |
| Deployment Gates | Combines the newest API and load evidence with saved release rules. |
| Dashboard, History, Reports | Shows local analytics, detailed historical runs, and exportable HTML/JSON reports. |

## How it works

```text
Project API URL
      |
      +--> Discovery --> enabled endpoints --> API Test Suite --> API evidence
      |
      +--> Load Testing -------------------> performance evidence
      |
      +--> Security -----------------------> passive / active findings
                                              |
                                              v
                                     Deployment Gates
                                              |
                                              v
                                  Dashboard, History, Reports
```

API checks, load tests, and security scans are stored as separate runs. Deployment Gates uses the newest API evidence for API pass rate and the newest load-test evidence for performance rules. The gate banner identifies both source runs.

## Requirements

- Python 3.12 or newer
- A desktop environment with Tkinter support
- An API URL you own or are authorized to test

## Installation

```bash
git clone https://github.com/your-username/preflight.git
cd preflight
python -m venv .venv
```

Activate the environment:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install dependencies and launch:

```bash
pip install -r requirements.txt
python app.py
```

## Quick start

1. In **Projects**, create and activate a project with an API URL, for example `http://localhost:8000`.
2. Use **Test Connection** to confirm that target is reachable.
3. In **Discovery**, select **Discover API**. Preflight expects `<API URL>/openapi.json`.
4. Review enabled endpoints. Disable any operation you do not want a functional test to call.
5. In **Test Suite**, run API checks. Preflight uses OpenAPI examples, defaults, enum values, safe query values, and JSON request schemas where available. Paths without a documented safe value are skipped rather than guessed.
6. In **Scenarios**, start a small load test, such as 2 virtual users and 10 requests.
7. In **Security**, run the Safe Configuration Scan. If appropriate, run the opt-in Active Vulnerability Scan.
8. In **Deployment Gates**, set your limits, press **Refresh**, then choose **Save Rules & Evaluate Latest Evidence**.
9. Review details in **Dashboard**, **History**, or **Reports**. Reports can be exported as HTML and JSON.

## Understanding results

### API Test Suite

- **Passed** — the endpoint returned its documented expected success status.
- **Failed** — the request failed or returned an unexpected status. Expand its row to see expected/actual status, duration, error, and a redacted response body.
- **Skipped** — Preflight could not resolve a safe path value. It made no request; use the manual runner with an appropriate real value if needed.

New API response details are stored locally, structured JSON is redacted for common credential fields, and response text is capped at 20 KB.

### Load Testing

- **Virtual users** — concurrent simulated clients.
- **Total requests** — requests included in the measured test.
- **RPS** — completed requests per second.
- **Average / P50 / P95 / P99** — request time statistics in milliseconds. P95 means 95% of measured requests completed no slower than that time.
- **Error rate** — percentage of measured requests that failed.

Connections are warmed before measurement and each virtual user uses its own client, avoiding artificial local request queueing. Load tests retain aggregate metrics only; individual response bodies are not saved.

### Deployment Gates

A release is **READY TO DEPLOY** only if every saved rule passes.

- The **API pass-rate** rule uses release-eligible executed checks: `passed / (passed + failed)`. Skipped checks do not count as failures.
- Average, P95, P99, and error-rate rules use the latest saved load metrics.
- Preflight excludes endpoints tagged `preflight-test-fixture` or `preflight-security-fixture` from deployment-gate API and load evidence. They remain available for API and Security testing.

Refresh after a new API or load run. The screen will show **Latest evidence available** with the relevant API and load run IDs; evaluate to save the final decision on the API run.

### Security

Security has two modes.

#### Safe Configuration Scan

The passive configuration review makes one ordinary request and checks:

- HTTPS and HSTS;
- recommended browser security headers;
- wildcard CORS settings;
- missing cookie flags: `Secure`, `HttpOnly`, and `SameSite`; and
- exposed server technology headers.

It does not send exploit payloads or modify data.

#### Active Vulnerability Scan

The active scan is opt-in. It only runs when:

- the environment is **Local**, **Development**, or **Staging** — Production is blocked in the UI and runner;
- you confirm **“I own or am authorized to test this target”** for that scan; and
- the target is a discovered, enabled endpoint on the selected API host.

The confirmation is not persisted. Version 1 is deliberately conservative: one sequential worker, `GET` and `OPTIONS` only, five-second request timeout, 256 KB maximum response processing, no followed redirects, and host checks for generated URLs.

Active findings are evidence-based review candidates for:

- reflected input in HTML/XHTML responses (**CWE-79**), using a unique inert alphanumeric marker rather than executable JavaScript;
- controlled parent-directory path handling (**CWE-22**);
- external open-redirect behaviour (**CWE-601**);
- sensitive stack-trace or implementation-error exposure (**CWE-209**); and
- methods advertised through `OPTIONS` (informational).

Use **STOP SCAN** to cancel. Filter the combined findings list by Active or Passive, then expand a finding to inspect severity, confidence, CWE, target, parameter, response status, sanitized evidence, and remediation guidance. Security run details are also retained in History and Reports.

A security finding is a review item. It is not proof of compromise, successful exploitation, or a complete vulnerability assessment.

## Safety notes

- Only test systems you own or are explicitly authorized to test.
- Start with small load tests, especially for shared or production systems.
- Review enabled API operations. `POST`, `PUT`, `PATCH`, and `DELETE` may change data.
- Use a Local, Development, or Staging environment for active security scanning.
- Do not use intentional vulnerable fixtures in a production service.

## Testing Preflight

Run the automated suite:

```bash
python -m pytest -q
```

For a manual end-to-end check, discover a local OpenAPI API, run API and load checks, run both security modes against an authorized non-production target, inspect expandable result details, evaluate the release gate, and confirm History and Reports contain the expected data.

## Data storage

Preflight stores its SQLite database at `storage/preflight.db` and exported reports at `storage/reports/`. These runtime files are local and should remain ignored by Git.

## Project status

Preflight is a local-first validation tool under active development. It focuses on API correctness, performance evidence, security configuration review, controlled non-destructive active checks, and explainable release decisions.

## License

Released under the [MIT License](LICENSE).
