Preflight
Desktop pre-deployment testing and validation platform built with Python and CustomTkinter.

Preflight is a local developer tool that tests a running web application before deployment.

The developer provides the application's URLs, selects what should be tested, configures the expected limits, and runs the complete validation suite from one desktop application.

Application URL
      ↓
Preflight
      ↓
Discover
      ↓
Configure
      ↓
Test
      ↓
Analyze
      ↓
Deployment Gates
      ↓
Report
The goal is simple:

One project. One configuration. One test run. One clear report.

1. Core Concept
Preflight does not replace the application or start by reading its source code.

The primary workflow tests a running application.

For example:

Frontend: http://localhost:3000
Backend/API: http://localhost:8000
or:

Frontend: https://staging.example.com
Backend/API: https://api-staging.example.com
Preflight connects to those targets and performs configured tests against them.

Different testing engines are responsible for different parts of the application:

                  APPLICATION
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
      FRONTEND                     API
http://localhost:3000    http://localhost:8000
          │                         │
          ▼                         ▼
     Playwright              HTTPX / Locust
          │                         │
   Browser / E2E            API + Load Tests
Security and performance tools may test either target depending on the selected configuration.

2. Project Goals
Preflight should allow developers to:

Create and manage projects.
Enter frontend and backend URLs.
Test whether targets are reachable.
Automatically discover supported APIs.
Detect FastAPI/OpenAPI specifications.
Import API specifications.
Manually define API tests.
Select which endpoints should be tested.
Test API functionality.
Simulate concurrent users.
Create realistic load scenarios.
Measure response times.
Measure throughput.
Detect failed requests.
Run browser-based E2E tests.
Run security checks.
Run frontend performance checks.
Configure deployment thresholds.
Watch tests execute in real time.
Cancel running tests.
Store previous test results.
Compare previous runs.
Generate reports.
Determine whether configured deployment gates passed.
3. Technology Stack
Layer	Tools
Desktop	Python 3.12+, CustomTkinter
Database	SQLite
API Testing	HTTPX, Pytest
API Discovery	OpenAPI, Swagger specification parsing
Load Testing	Locust
Browser / E2E	Playwright
Security	OWASP ZAP, Trivy, Custom HTTP security-header checks
Frontend Performance	Lighthouse CI
Reports	Python, Matplotlib, JSON, HTML
Packaging	PyInstaller
4. Main User Workflow
OPEN PREFLIGHT
      ↓
CREATE PROJECT
      ↓
ENTER TARGET URLs
      ↓
TEST CONNECTION
      ↓
DISCOVER API
      ↓
SELECT / CONFIGURE TESTS
      ↓
CONFIGURE LOAD
      ↓
CONFIGURE DEPLOYMENT GATES
      ↓
RUN PREFLIGHT
      ↓
WATCH LIVE RESULTS
      ↓
EVALUATE GATES
      ↓
VIEW REPORT
Example — Project: DropRoom, Frontend: http://localhost:3000, API: http://localhost:8000.

Preflight then checks both targets before testing begins.

5. Application Architecture
The GUI and testing engine must remain separated.

CustomTkinter GUI
        │
        ▼
   Test Manager
        │
        ├── Discovery Engine
        │      └── OpenAPI
        │
        ├── API Runner
        │      └── HTTPX / Pytest
        │
        ├── Load Runner
        │      └── Locust
        │
        ├── E2E Runner
        │      └── Playwright
        │
        ├── Security Runner
        │      ├── Security Headers
        │      ├── OWASP ZAP
        │      └── Trivy
        │
        └── Performance Runner
               └── Lighthouse
        │
        ▼
   Result Processor
        │
        ├── Deployment Gates
        ├── SQLite
        ├── JSON
        └── HTML
        │
        ▼
CustomTkinter Dashboard
The GUI should only:

collect configuration
trigger tests
display state
display logs
display progress
display results
Testing logic must not live inside GUI components.

6. Proposed Project Structure
preflight/
│
├── app.py
│
├── gui/
│   ├── main_window.py
│   ├── sidebar.py
│   ├── dashboard.py
│   ├── projects_view.py
│   ├── project_editor.py
│   ├── discovery_view.py
│   ├── api_view.py
│   ├── load_view.py
│   ├── scenarios_view.py
│   ├── e2e_view.py
│   ├── security_view.py
│   ├── reports_view.py
│   ├── history_view.py
│   ├── settings_view.py
│   │
│   └── components/
│       ├── metric_card.py
│       ├── status_card.py
│       ├── progress_card.py
│       ├── endpoint_row.py
│       └── log_console.py
│
├── core/
│   ├── test_manager.py
│   ├── process_manager.py
│   ├── discovery.py
│   ├── config.py
│   ├── events.py
│   └── gates.py
│
├── runners/
│   ├── api_runner.py
│   ├── load_runner.py
│   ├── e2e_runner.py
│   ├── security_runner.py
│   └── performance_runner.py
│
├── discovery/
│   ├── openapi.py
│   ├── swagger.py
│   └── importer.py
│
├── models/
│   ├── project.py
│   ├── endpoint.py
│   ├── scenario.py
│   ├── test_run.py
│   └── test_result.py
│
├── database/
│   ├── database.py
│   └── repositories.py
│
├── reports/
│   ├── generator.py
│   ├── charts.py
│   └── templates/
│
├── tests/
│   ├── api/
│   ├── load/
│   ├── e2e/
│   └── unit/
│
├── storage/
│   ├── reports/
│   └── preflight.db
│
├── config/
│   └── default.json
│
├── requirements.txt
├── pyproject.toml
├── .gitignore
├── README.md
└── PLAN.md
7. Main Navigation
Dashboard
Projects
API Discovery
Test Suite
API
Load
E2E
Security
Scenarios
Reports
History
Settings
The currently selected project should always be visible.

8. Create Project
The first step is creating a target project.

CREATE PROJECT

Project Name
[ DropRoom                              ]

Frontend URL
[ http://localhost:3000                 ]

API Base URL
[ http://localhost:8000                 ]

Environment
[ Local ▼ ]

          [ TEST CONNECTION ]

          [ CREATE PROJECT ]
Environment options: Local, Development, Staging, Production.

9. Connection Testing
Before running tests, Preflight should verify that the configured targets are reachable.

CHECKING TARGETS...

Frontend
http://localhost:3000

✓ Reachable
HTTP 200
84ms


API
http://localhost:8000

✓ Reachable
HTTP 200
31ms
Failures should provide useful information.

API CONNECTION FAILED

http://localhost:8000

Connection refused.

Possible causes:

• Backend is not running.
• Incorrect port.
• Incorrect URL.
• Firewall/network issue.
10. Automatic API Discovery
After confirming that the API is reachable, Preflight should attempt API discovery.

For FastAPI, first check: /openapi.json

GET http://localhost:8000/openapi.json
If available:

OpenAPI detected ✓

14 endpoints discovered.
The discovery engine parses: paths, methods, parameters, request bodies, response schemas, authentication requirements, tags.

11. API Discovery UI
API DISCOVERY

Source
http://localhost:8000/openapi.json

OpenAPI 3.1 ✓

14 endpoints discovered


☑ GET       /api/health
☑ POST      /api/auth/login
☑ POST      /api/rooms
☑ GET       /api/rooms/{room_id}
☑ DELETE    /api/rooms/{room_id}
☑ POST      /api/files
☑ GET       /api/files/{file_id}


[ SELECT ALL ]

[ DESELECT ALL ]

[ CONFIGURE SELECTED ]

[ RUN API TESTS ]
Developers should be able to disable endpoints they do not want Preflight to call.

This is especially important for DELETE, PATCH, PUT because those requests may modify data.

12. Manual API Tests
Automatic discovery will not always be available. Developers must therefore be able to manually create API tests.

ADD API TEST

Name
[ Create Room ]

Method
[ POST ▼ ]

Endpoint
[ /api/rooms ]

Headers

Content-Type: application/json

Body

{
    "name": "Preflight Test"
}

Expected Status
[ 201 ]

Expected Field
[ room_code ]

Maximum Response
[ 500 ] ms


              [ SAVE TEST ]
Supported methods: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS.

13. API Specification Import
Later versions should support importing: OpenAPI JSON, OpenAPI YAML, Swagger JSON, Postman Collection.

API DISCOVERY

[ AUTO DISCOVER ]

or

[ IMPORT OPENAPI ]

[ IMPORT POSTMAN ]
14. API Test Assertions
Each API test can define assertions.

Examples: expected status 201, maximum response 500ms, response contains room_code, JSON field success = true, header Content-Type = application/json.

Possible assertion types:

status code
response time
JSON property exists
JSON property equals value
response contains text
header exists
header value
schema validation
15. API Test Results
API TESTS

✓ GET     /api/health          200      42ms
✓ POST    /api/login           200      91ms
✓ POST    /api/rooms           201      87ms
✓ GET     /api/rooms/123       200      61ms
✗ POST    /api/files           500      402ms


Passed: 4
Failed: 1

Average: 136ms
Clicking a failed test should display: request, headers, body, response, status, response time, failed assertion.

Sensitive authorization values must be redacted.

16. Authentication
Many APIs require authentication. Preflight should eventually support: No Authentication, Bearer Token, API Key, Basic Authentication, Custom Headers.

AUTHENTICATION

Type
[ Bearer Token ▼ ]

Token
[ ••••••••••••••••••• ]

☑ Hide token in logs
Secrets must not be stored in plaintext logs or exported reports.

17. Load Testing Concept
API testing answers: Does the endpoint work?
Load testing answers: What happens when many users use the application simultaneously?
Locust should power load testing.

LOAD TEST

Target
http://localhost:8000

Scenario
[ Standard User ▼ ]

Concurrent Users
[ 100 ]

Spawn Rate
[ 10 ] users/sec

Duration
[ 5 ] minutes

P95 Limit
[ 500 ] ms

Maximum Error Rate
[ 1 ] %

             [ START LOAD TEST ]
18. Load Profiles
Profile	Users	Duration	Purpose
Smoke	5	30 seconds	Quick sanity check
Normal	50	2 minutes	Everyday validation
Load	100	5 minutes	Standard capacity check
Stress	500+	—	Discover system limits
Spike	10 → 500 → 10	—	Sudden traffic surges
Endurance	100	60 minutes	Memory leaks, connection leaks, DB pool exhaustion, gradual degradation
19. Simulated Users
A simulated Locust user is not necessarily a browser. Instead, it behaves like a user by making HTTP requests.

100 USERS

User 1 ────→ API
User 2 ────→ API
User 3 ────→ API
...
User 100 ──→ API
Each simulated user executes a configured scenario, allowing Preflight to simulate hundreds or thousands of users without opening hundreds of browsers.

20. User Scenarios
Example DropRoom scenario:

JOIN ROOM
    ↓
GET ROOM INFORMATION
    ↓
GET MESSAGES
    ↓
SEND MESSAGE
    ↓
GET FILE LIST
    ↓
DOWNLOAD FILE
    ↓
WAIT
    ↓
REPEAT
Scenario editor:

SCENARIO

Name
[ DropRoom Guest ]

Steps

1. POST /api/rooms/join
2. GET  /api/rooms/{room_id}
3. GET  /api/messages
4. POST /api/messages
5. GET  /api/files

Wait Between Requests

Minimum
[ 1 ] sec

Maximum
[ 3 ] sec
21. Weighted User Behavior
GET dashboard       40%
GET resources       25%
Create resource     15%
Update resource     10%
Authentication       5%
Delete resource      5%
This produces more realistic traffic.

22. Dynamic Scenario Data
Requests often depend on previous responses.

POST /rooms
      ↓
response:
{
    "room_id": "ABC123"
}
      ↓
store room_id
      ↓
GET /rooms/ABC123
Preflight should eventually allow extracting response.room_id, saving it as room_id, then using /api/rooms/{room_id} in subsequent requests.

23. Live Load Metrics
LIVE LOAD TEST

Users
100 / 100

Requests
18,421

Successful
18,389

Failed
32

Requests/sec
87.4

Average
142ms

P50
103ms

P95
387ms

P99
621ms

Errors
0.17%

████████████████████████░░  04:21 / 05:00

                    [ STOP ]
24. Browser / E2E Testing
Playwright handles actual browser behavior.

OPEN
http://localhost:3000

      ↓

CLICK
Create Room

      ↓

TYPE
Room Name

      ↓

CLICK
Create

      ↓

WAIT FOR
Room Page

      ↓

VERIFY
Room Code Exists
25. Playwright vs Locust
Playwright — Answers: Does the actual frontend work correctly? Use for buttons, forms, navigation, authentication flows, browser rendering, frontend/backend integration. Example: 5–20 browser scenarios.

Locust — Answers: Can the backend handle many simultaneous users? Use for 100 / 500 / 1,000 / 5,000 users.

Do not simulate large-scale load by opening hundreds of Playwright browsers unless specifically required.

26. E2E Results
E2E TESTS

✓ Homepage loads

✓ Login

✓ Create room

✓ Join room

✓ Upload file

✗ Delete room


5 / 6 passed
Failed E2E tests should optionally save: screenshot, error message, current URL, execution step.

27. Security Testing
Level 1 — Safe Checks (can run automatically): HTTPS, HTTP security headers, cookie flags, exposed server headers, CORS configuration indicators.

Level 2 — Active Security Scanning: OWASP ZAP may actively interact with the application. This should primarily target Local, Development, Staging. Production should require explicit confirmation.

28. Security Headers
Check: Content-Security-Policy, Strict-Transport-Security, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy.

SECURITY

HTTPS                         ✓
HSTS                          ✓
Content-Security-Policy       ✗
X-Content-Type-Options        ✓
X-Frame-Options               ✓
Referrer-Policy               ✓
29. OWASP ZAP
OWASP ZAP

Critical       0
High           0
Medium         2
Low            4
Informational  7
Each result should include: Severity, Title, Affected URL, Description, Evidence, Suggested remediation.

30. Trivy
Trivy normally scans project files, dependencies, images, or containers rather than simply testing a public URL.

SOURCE SECURITY

Project Directory
C:\Projects\DropRoom

Docker Image
droproom-api:latest
31. Frontend Performance
Lighthouse should target the frontend URL (e.g. http://localhost:3000).

Metrics: Performance, Accessibility, Best Practices, SEO.

Web metrics may include: First Contentful Paint, Largest Contentful Paint, Total Blocking Time, Cumulative Layout Shift.

32. Deployment Gates
DEPLOYMENT GATES

API Pass Rate
[ 100 ] %

Maximum Average Response
[ 300 ] ms

Maximum P95
[ 500 ] ms

Maximum P99
[ 800 ] ms

Maximum Error Rate
[ 1 ] %

Critical Vulnerabilities
[ 0 ]

High Vulnerabilities
[ 0 ]

E2E Pass Rate
[ 100 ] %
These are project-specific thresholds.

33. Gate Evaluation
DEPLOYMENT CHECK

API
48 / 48 passed                    ✓

LOAD
100 concurrent users             ✓
Average 142ms < 300ms            ✓
P95 387ms < 500ms                ✓
P99 621ms < 800ms                ✓
Errors 0.17% < 1%                ✓

SECURITY
Critical = 0                     ✓
High = 0                         ✓

E2E
12 / 12 passed                   ✓

Result:

✓ CONFIGURED CHECKS PASSED
Failure example:

✗ DEPLOYMENT CHECK FAILED

2 requirements failed.

P95 RESPONSE
Required  < 500ms
Actual    782ms

API PASS RATE
Required  100%
Actual    97.8%
Passing Preflight means the configured checks and thresholds passed. It must not imply that software is completely bug-free, secure, or guaranteed to succeed in production.

34. Run All Tests
▶ RUN PREFLIGHT

Checking Targets
        ↓
Discovering API
        ↓
API Tests
        ↓
Load Tests
        ↓
E2E Tests
        ↓
Security Tests
        ↓
Performance Tests
        ↓
Evaluate Gates
        ↓
Generate Report
Individual suites should also be runnable separately.

35. Dashboard
┌─────────────────────────────────────────────────────────┐
│ PREFLIGHT                                    ● READY    │
├──────────────┬──────────────────────────────────────────┤
│ Dashboard    │                                          │
│ Projects     │  DROPROOM                                │
│              │                                          │
│ Discovery    │  Frontend ✓                              │
│              │  API      ✓                              │
│ Test Suite   │                                          │
│  API         │  API        LOAD       SECURITY          │
│  Load        │  ✓ PASS     ✓ PASS      ✓ PASS           │
│  E2E         │                                          │
│  Security    │  Requests       18,421                   │
│              │  Users          100                      │
│ Scenarios    │  Average        142ms                    │
│ Reports      │  P95            387ms                    │
│ History      │  Errors         0.17%                    │
│ Settings     │                                          │
│              │          ✓ CHECKS PASSED                 │
│              │                                          │
│              │           [ RUN PREFLIGHT ]              │
└──────────────┴──────────────────────────────────────────┘
36. Test Manager
TestManager is the central orchestrator.

Responsibilities: validate project, check targets, start/stop tests, track state, launch runners, receive results, send GUI events, store results, evaluate gates, generate reports.

Possible states: IDLE, CONNECTING, DISCOVERING, RUNNING_API, RUNNING_LOAD, RUNNING_E2E, RUNNING_SECURITY, RUNNING_PERFORMANCE, EVALUATING, COMPLETED, FAILED, CANCELLED.

37. Background Execution
Never execute long-running tests directly on the CustomTkinter UI thread.

Use: threading, queue.Queue, subprocess.Popen.

CustomTkinter
Main Thread
     │
     ▼
Command Queue
     │
     ▼
Worker
     │
     ▼
Test Runner
     │
     ▼
Event Queue
     │
     ▼
CustomTkinter
Use .after() to process GUI events.

38. External Process Management
Tools such as Locust, Playwright, ZAP, Trivy, Lighthouse may run as external processes.

Create a centralized ProcessManager with: start(), stop(), kill(), read_stdout(), read_stderr(), get_exit_code(), cleanup().

This makes cancellation and cleanup reliable.

39. Live Console
00:00 Starting Preflight...

00:01 Checking frontend...
00:01 ✓ Frontend reachable

00:01 Checking API...
00:01 ✓ API reachable

00:02 Discovering OpenAPI...
00:02 ✓ 14 endpoints found

00:03 Running API tests...

00:03 ✓ GET /api/health
00:04 ✓ POST /api/rooms
00:04 ✓ GET /api/rooms/{id}

00:05 API tests complete.

00:06 Starting load test...

00:07 10 users
00:08 20 users
00:09 30 users

...

00:16 100 users active

Requests/sec: 87
P95: 387ms
Errors: 0.17%
Logs should support: timestamps, severity, source, auto-scroll, copy, clear, export.

40. Database
SQLite stores application configuration and test history.

Suggested tables: projects, endpoints, scenarios, test_runs, test_results, load_metrics, security_findings (see field lists in the original schema notes below each table name).

projects: id, name, frontend_url, api_url, environment, created_at, updated_at
endpoints: id, project_id, name, method, path, enabled, source, configuration
scenarios: id, project_id, name, description, configuration
test_runs: id, project_id, started_at, finished_at, status, duration, gate_status
test_results: id, test_run_id, test_type, name, status, duration, details
load_metrics: id, test_run_id, users, requests, failures, rps, average_response, p50, p95, p99, error_rate
security_findings: id, test_run_id, severity, title, description, affected_url, source
41. Test History
DROPROOM

Sep 27 2026
00:42

✓ PASSED

100 users
18,421 requests
P95 387ms
Errors 0.17%


────────────────────────


Sep 26 2026
22:18

✗ FAILED

100 users
16,182 requests
P95 812ms
Errors 3.4%
Clicking a test run opens its complete report.

42. Historical Comparison
PREVIOUS	CURRENT
Average Response	210ms	142ms
P50	141ms	103ms
P95	520ms	387ms
P99	890ms	621ms
Error Rate	1.20%	0.17%
Requests/sec	71	87
This makes regressions visible.

43. Reports
PREFLIGHT TEST REPORT

Project
DropRoom

Frontend
http://localhost:3000

API
http://localhost:8000

Date
September 27, 2026

Duration
6m 42s

────────────────────────────

API

48 / 48 passed

────────────────────────────

LOAD

Users             100
Requests          18,421
Successful        18,389
Failed            32

RPS               87.4

Average           142ms
P50               103ms
P95               387ms
P99               621ms

Error Rate        0.17%

────────────────────────────

SECURITY

Critical          0
High              0
Medium            2
Low               4

────────────────────────────

E2E

12 / 12 passed

────────────────────────────

DEPLOYMENT GATES

✓ PASSED
Support: JSON, HTML. PDF may be added later.

44. Stop / Cancel
STOP
 ↓
Request Cancellation
 ↓
Stop Worker
 ↓
Terminate Child Processes
 ↓
Collect Partial Results
 ↓
Mark Run CANCELLED
 ↓
Restore UI
Preflight must clean up: Locust, Chromium, ZAP, Lighthouse, temporary processes.

45. Production Safety
Preflight must clearly distinguish LOCAL, DEVELOPMENT, STAGING, PRODUCTION.

Production should require additional confirmation for: stress tests, spike tests, destructive API tests, active security scans, very high concurrency.

PRODUCTION WARNING

You are about to run:

500-user Stress Test

against:

https://api.example.com


This may affect real users.


[ CANCEL ]

[ I UNDERSTAND — CONTINUE ]
46. Destructive Endpoint Protection
Automatically flag DELETE, PUT, PATCH, POST as potentially state-changing.

Do not automatically load-test discovered destructive endpoints. Require the developer to explicitly enable them or place them inside a configured scenario.

DELETE /api/account

⚠ STATE-CHANGING ENDPOINT

Load testing disabled.

[ ENABLE ]
47. Configuration File
Later versions should support preflight.yml:

project:
  name: DropRoom

target:
  frontend: http://localhost:3000
  api: http://localhost:8000

tests:
  api: true
  load: true
  e2e: true
  security: true

load:
  users: 100
  spawn_rate: 10
  duration: 300

gates:
  api_pass_rate: 100
  max_average_response: 300
  max_p95: 500
  max_p99: 800
  max_error_rate: 1
  max_critical_vulnerabilities: 0
48. CLI Mode
After the desktop engine becomes stable:

preflight run
or:

preflight run --config preflight.yml
Exit codes: 0 = gates passed, 1 = gates failed, 2 = configuration error, 3 = internal/execution error.

49. CI/CD Integration
git push
   ↓
GitHub Actions
   ↓
Build
   ↓
Start Test Environment
   ↓
Preflight CLI
   ↓
API Tests
   ↓
Load Tests
   ↓
E2E
   ↓
Security
   ↓
Performance
   ↓
Deployment Gates
   ↓
       ┌─────────────┐
       │             │
      PASS          FAIL
       │             │
       ▼             ▼
   Continue       Stop
   Pipeline       Pipeline
The GUI and CLI should share the same testing engine.

50. MVP Scope
Required for v0.1.0:

Projects: create, edit, delete project; frontend URL, API URL, environment
Connectivity: test frontend URL, test API URL, show status, show response time
Discovery: detect /openapi.json, parse OpenAPI, discover endpoints, select endpoints
API Testing: GET, POST, PUT, PATCH, DELETE; expected status; response time; basic JSON assertions
Load Testing: Locust; user count, spawn rate, duration; basic scenarios
Metrics: requests, successful requests, failed requests, RPS, average, P50, P95, P99, error rate
Core Application: background workers, live console, stop tests, SQLite, test history, deployment gates, basic reports
Not required for MVP (add after the core application works reliably):

Playwright
OWASP ZAP
Trivy
Lighthouse
Postman Import
CI/CD
Distributed Load Testing
Cloud Accounts
51. MVP Development Order & Checklists
Each milestone below must be functionally complete and manually verified before moving to the next. Check off items as they're completed.

Milestone 1 — Application Shell
 [x] Initialize project repo, pyproject.toml, requirements.txt, .gitignore
 [x] Set up CustomTkinter app entry point (app.py)
 [x] Build Main Window shell (title bar, root frame, theme)
 [x] Build Sidebar navigation (Dashboard, Projects, Discovery, Test Suite, Scenarios, Reports, History, Settings)
 [x] Build empty Dashboard view
 [x] Implement view routing / frame-switching logic
 [x] Build reusable components: metric_card, status_card, progress_card, endpoint_row, log_console
 [x] Verify app launches, navigates between views, no frozen UI
Milestone 1 done when: the app opens, all nav items switch views, and the shell renders with no logic wired up yet.

Milestone 2 — Database
 [x] Design SQLite schema (projects, endpoints, scenarios, test_runs, test_results, load_metrics, security_findings)
 [x] Implement database.py (connection, migrations/init)
 [x] Implement repositories.py (CRUD per table)
 [x] Implement settings persistence (app-level config, e.g. config/default.json)
 [x] Write unit tests for repositories
 [x] Verify DB file is created under storage/preflight.db on first run
Milestone 2 done when: projects and settings can be written to and read back from SQLite reliably.

Milestone 3 — Project Management
 [x] Build Create Project form (name, frontend URL, API URL, environment)
 [x] Wire form to projects repository (create)
 [x] Build Projects list view
 [x] Build Edit Project flow
 [x] Build Delete Project flow (with confirmation)
 [x] Persist and restore "currently selected project" across sessions
 [x] Validate required fields and URL formatting
Milestone 3 done when: a developer can create, edit, delete, and switch between projects, and the active project is always visible.

Milestone 4 — Connection Testing
 [x] Implement frontend reachability check (HTTP GET, capture status + timing)
 [x] Implement API reachability check (HTTP GET, capture status + timing)
 Build "Test Connection" UI (loading state → ✓/✗ result)
 [x] Display HTTP status and response time per target
 [x] Build failure state with actionable guidance (backend not running, wrong port, wrong URL, firewall/network)
 [x] Run connection checks off the main thread
Milestone 4 done when:

URL
 ↓
TEST CONNECTION
 ↓
✓ / ✗
works reliably for both frontend and API targets, for both success and failure cases.

Milestone 5 — OpenAPI Discovery
 [x] Implement /openapi.json detection (discovery/openapi.py)
 [x] Parse OpenAPI specification (paths, methods, parameters, request bodies, response schemas, auth requirements, tags)
 [x] Build Discovery Engine orchestration (core/discovery.py)
 [x] Build API Discovery view listing all discovered endpoints
 [x] Implement per-endpoint enable/disable checkboxes
 [x] Implement Select All / Deselect All
 [x] Flag destructive methods (DELETE, PUT, PATCH) visually
 [x] Persist selected/enabled endpoints to the endpoints table
Milestone 5 done when:

http://localhost:8000
        ↓
/openapi.json
        ↓
14 endpoints
appears correctly in the Discovery view and selections persist.

Milestone 6 — API Testing
 [x] Build HTTPX-based API Runner (runners/api_runner.py)
 [x] Support GET, POST, PUT, PATCH, DELETE
 [x] Implement assertions: status code, response time, JSON property exists, JSON property equals, response contains text, header exists/value
 [x] Build manual "Add API Test" form
 [x] Build API Test Results view (pass/fail list, timing, averages)
 [x] Build failed-test detail view (request, headers, body, response, failed assertion) with secret redaction
 [x] Persist results to test_results
Milestone 6 done when: both discovered and manually-defined API tests run against a live target and produce a pass/fail report with timings.

Milestone 7 — Test Manager
 Implement TestManager orchestrator (core/test_manager.py)
 Implement state machine (IDLE, CONNECTING, DISCOVERING, RUNNING_API, RUNNING_LOAD, EVALUATING, COMPLETED, FAILED, CANCELLED)
 Implement background worker thread(s) + queue.Queue for commands/events
 Wire GUI to poll the event queue via .after()
 Build Live Console component (timestamps, severity, source, auto-scroll, copy, clear, export)
 Implement cancellation (Stop button → graceful worker shutdown)
 Implement ProcessManager (start, stop, kill, read_stdout, read_stderr, get_exit_code, cleanup)
Milestone 7 done when: any test suite can run in the background without freezing the UI, streams live logs, and can be cancelled cleanly.

Milestone 8 — Load Testing
 Integrate Locust as an external process via ProcessManager
 Build Load Test configuration UI (users, spawn rate, duration, target)
 Implement built-in Load Profiles (Smoke, Normal, Load, Stress, Spike, Endurance)
 Build Scenario editor (ordered request steps, wait time min/max)
 Implement live metrics streaming (users, requests, successful, failed, RPS, average, P50, P95, P99, error rate)
 Build Live Load Metrics view with progress bar
 Implement Stop for in-progress load tests
 Persist metrics to load_metrics
 Guard destructive endpoints from automatic load testing (require explicit enable)
Milestone 8 done when:

100 simulated users
        ↓
API
        ↓
live metrics
runs end-to-end with real-time updates and a clean stop.

Milestone 9 — Deployment Gates
 Build Deployment Gates configuration UI (API pass rate, avg response, P95, P99, error rate, and stubs for future security/E2E gates)
 Implement gate evaluation logic (core/gates.py)
 Build Gate Evaluation result view (per-gate ✓/✗ with required vs. actual)
 Persist gate status to test_runs.gate_status
 Add Production-environment confirmation dialog for risky test types
Milestone 9 done when: a completed run is automatically evaluated against configured thresholds and shows a clear PASS/FAIL per gate.

Milestone 10 — History
 Persist every test run (start/end time, status, duration, gate status) to test_runs
 Build History view (chronological list of past runs per project)
 Build run detail view (reopen a historical run's full results)
 Build Historical Comparison view (previous vs. current: avg, P50, P95, P99, error rate, RPS)
Milestone 10 done when: past runs are browsable, reopenable, and comparable against the most recent run.

Milestone 11 — Reports
 Build report generator (reports/generator.py)
 Build chart generation for load metrics (reports/charts.py, Matplotlib)
 Build HTML report template (reports/templates/)
 Build JSON report export
 Include: project info, API results, load results, gate results, duration
 Wire "View Report" action from Dashboard / History
 Save reports to storage/reports/
Milestone 11 done when: a finished run produces both a JSON and an HTML report containing full API, load, and gate results, viewable from the app.

Release Checklist — v0.1.0
 All Milestones 1–11 complete and manually smoke-tested end-to-end
 Full workflow verified: create project → test connection → discover API → select endpoints → configure load → configure gates → run Preflight → watch live results → view gate evaluation → view saved report
 No blocking operations on the CustomTkinter main thread anywhere in the app
 Cancel/Stop verified for both API and Load test runs, including subprocess cleanup
 Secrets (tokens, auth headers) confirmed redacted in logs and reports
 SQLite schema finalized and migration-safe
 README.md written (setup, usage, screenshots)
 PyInstaller build produces a working desktop executable
 Tag and publish v0.1.0
52. Version Roadmap & Checklists
v0.1 — Core (see Milestones 1–11 above)
 CustomTkinter shell
 Projects
 URL testing
 OpenAPI discovery
 API testing
 Locust load testing
 SQLite
 Deployment gates
 History
 Reports
v0.2 — Browser Testing
 Integrate Playwright via ProcessManager
 Build E2E Runner (runners/e2e_runner.py)
 Build E2E scenario/step definition UI
 Support core actions: open, click, type, wait for, verify
 Build E2E Results view (pass/fail per scenario)
 Capture and store screenshot, error message, current URL, and execution step on failure
 Add E2E pass rate to Deployment Gates
 Add E2E section to Reports
v0.3 — Security
 Implement Level 1 safe checks: HTTPS, HSTS, CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy
 Build Security Headers results view
 Integrate OWASP ZAP via ProcessManager (Level 2 active scanning)
 Require explicit confirmation for active scans against Production
 Build ZAP results view (Critical/High/Medium/Low/Informational, with per-finding detail)
 Integrate Trivy for project directory / Docker image / container scanning
 Build Source Security configuration UI (project directory, Docker image)
 Add Critical/High vulnerability counts to Deployment Gates
 Add Security section to Reports
v0.4 — Performance
 Integrate Lighthouse CI via ProcessManager (runners/performance_runner.py)
 Target frontend URL for Lighthouse runs
 Capture Performance, Accessibility, Best Practices, SEO scores
 Capture Core Web Vitals: FCP, LCP, TBT, CLS
 Build Performance results view
 Build performance history tracking per project
 Implement performance regression detection vs. previous runs
 Add Performance section to Reports
v0.5 — Automation
 Design and implement preflight.yml config schema
 Build CLI entry point (preflight run, preflight run --config preflight.yml)
 Ensure CLI reuses the same TestManager/runners as the GUI (no duplicated logic)
 Implement exit codes: 0 gates passed, 1 gates failed, 2 config error, 3 internal/execution error
 Write GitHub Actions example workflow
 Document CI/CD integration in README
 Verify pipeline: push → build → start test env → Preflight CLI → gates → continue/stop pipeline
v1.0 — Stable Release
 All v0.1–v0.5 features stable and documented
 Full test coverage across runners and core logic
 Packaging verified on target OS(es) via PyInstaller
 Documentation complete (README, configuration reference, CLI reference)
 Upgrade/migration path for existing SQLite databases verified
 Tag and publish v1.0.0
53. Example Complete Workflow
Suppose the developer wants to test DropRoom.

Start: python app.py
Create project — Name: DropRoom, Frontend: http://localhost:3000, API: http://localhost:8000, Environment: Local
Click TEST CONNECTION → Frontend ✓, API ✓
Click DISCOVER API → requests http://localhost:8000/openapi.json → OpenAPI 3.1 detected, 14 endpoints found
Select API endpoints:
☑ GET /api/health
☑ POST /api/rooms
☑ GET /api/rooms/{id}
☐ DELETE /api/rooms/{id}
Configure load scenario — Scenario: DropRoom Guest, Users: 100, Spawn: 10/sec, Duration: 5 minutes
Configure gates — API Pass: 100%, Average: < 300ms, P95: < 500ms, P99: < 800ms, Errors: < 1%
Click ▶ RUN PREFLIGHT
Preflight executes: Connection ✓ → API Tests ✓ → Load Test ✓ → Deployment Gates ✓
Final result:
PREFLIGHT

DROPROOM

────────────────────────

API

48 / 48

✓ PASS


LOAD

Users       100
Requests    18,421
RPS         87.4

Average     142ms
P95         387ms
P99         621ms

Errors      0.17%

✓ PASS


────────────────────────

DEPLOYMENT GATES

✓ CONFIGURED CHECKS PASSED

Duration

5m 48s
54. Definition of Done — v0.1
Preflight v0.1 is complete when a developer can:

OPEN PREFLIGHT
      ↓
CREATE PROJECT
      ↓
ENTER API URL
      ↓
TEST CONNECTION
      ↓
DISCOVER OPENAPI
      ↓
SELECT ENDPOINTS
      ↓
CONFIGURE LOAD
      ↓
SELECT 100 USERS
      ↓
RUN PREFLIGHT
      ↓
WATCH LIVE METRICS
      ↓
REVIEW RESULTS
      ↓
CHECK DEPLOYMENT GATES
      ↓
VIEW SAVED REPORT
From one desktop application, the developer should be able to answer:

 Is the application reachable?
 What APIs are available?
 Are selected API endpoints working?
 How quickly are they responding?
 Can the application handle the configured concurrent load?
 What is the P95 response time?
 What is the P99 response time?
 How many requests are failing?
 What throughput is the application achieving?
 Did the configured deployment requirements pass?
 Did performance improve or regress compared with previous runs?
55. Long-Term Vision
                    PREFLIGHT
                        │
         ┌──────────────┼──────────────┐
         │              │              │
         ▼              ▼              ▼
        API            LOAD         SECURITY
         │              │              │
         └──────────────┼──────────────┘
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
             E2E             PERFORMANCE
              │                   │
              └─────────┬─────────┘
                        ▼
                DEPLOYMENT GATES
                        │
               ┌────────┴────────┐
               ▼                 ▼
             PASSED            FAILED
               │                 │
               ▼                 ▼
          Continue to       Review problems
          next deployment   before deployment
          step
The application should make pre-deployment testing easier without hiding the underlying metrics. The developer should always be able to see why a test passed or failed.

56. Core Principles
Simple setup — URL → Discover → Configure → Run.
Real metrics — Show actual response times, percentiles, failures, and throughput.
No frozen GUI — All long-running work happens outside the CustomTkinter main thread.
Safe defaults — Potentially destructive tests require explicit configuration.
Environment awareness — Production receives stronger warnings and restrictions.
Transparent results — Never show only PASS or FAIL. Show the underlying measurements.
Reusable engine — GUI and future CLI use the same testing engine.
Incremental development — API + load testing first. Browser, security, performance, and CI/CD later.
Configurable gates — Preflight evaluates the requirements defined for each project.
Developer control — The developer decides which endpoints, scenarios, tests, and thresholds are appropriate for the application.
