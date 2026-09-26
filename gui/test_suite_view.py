from __future__ import annotations

from datetime import datetime, timezone
from threading import Thread

import customtkinter as ctk
import httpx

from core.parameters import baseline_body, url_for
from core.projects import ProjectService
from core.release_endpoints import include_in_release_gate
from core.test_manager import TestManager
from database.repositories import (
    EndpointsRepository,
    TestResultsRepository,
    TestRunsRepository,
)
from gui.components.expandable_result import ExpandableResult
from gui.components.log_console import LogConsole
from runners.api_runner import (
    expected_success_status,
    prepare_response,
    run_request,
)


class TestSuiteView(ctk.CTkFrame):
    def __init__(
        self,
        master,
        projects: ProjectService,
        endpoints: EndpointsRepository,
        runs: TestRunsRepository,
        results: TestResultsRepository,
    ):
        super().__init__(
            master,
            fg_color="transparent",
        )

        self.projects = projects
        self.endpoints = endpoints
        self.runs = runs
        self.results = results
        self.manager = TestManager()

        # ---------------------------------------------------------
        # Title
        # ---------------------------------------------------------

        ctk.CTkLabel(
            self,
            text="API Test Suite",
            font=ctk.CTkFont(
                size=30,
                weight="bold",
            ),
        ).pack(
            anchor="w",
            padx=28,
            pady=(30, 6),
        )

        # ---------------------------------------------------------
        # Status
        # ---------------------------------------------------------

        self.status = ctk.CTkLabel(
            self,
            text=(
                "Run enabled discovered endpoints. "
                "Parameterized paths are skipped until you provide "
                "real values in Manual test."
            ),
        )

        self.status.pack(
            anchor="w",
            padx=28,
            pady=(0, 14),
        )

        # ---------------------------------------------------------
        # Main controls
        # ---------------------------------------------------------

        controls = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        controls.pack(
            anchor="w",
            padx=28,
            pady=(0, 10),
        )

        ctk.CTkButton(
            controls,
            text="RUN API TESTS",
            command=self.run,
        ).pack(
            side="left",
            padx=(0, 6),
        )

        ctk.CTkButton(
            controls,
            text="STOP",
            fg_color="#B34141",
            command=self.manager.cancel,
        ).pack(
            side="left",
        )

        # ---------------------------------------------------------
        # Manual request controls
        # ---------------------------------------------------------

        manual = ctk.CTkFrame(self)

        manual.pack(
            fill="x",
            padx=28,
            pady=(0, 10),
        )

        self.manual_method = ctk.CTkOptionMenu(
            manual,
            values=[
                "GET",
                "POST",
                "PUT",
                "PATCH",
                "DELETE",
            ],
            width=90,
        )

        self.manual_method.pack(
            side="left",
            padx=8,
            pady=8,
        )

        self.manual_path = ctk.CTkEntry(
            manual,
            placeholder_text=(
                "Manual path, e.g. " "/api/v1/rooms/a-real-token/uploads"
            ),
        )

        self.manual_path.pack(
            side="left",
            fill="x",
            expand=True,
            padx=4,
            pady=8,
        )

        ctk.CTkButton(
            manual,
            text="RUN MANUAL",
            command=self.run_manual,
        ).pack(
            side="left",
            padx=8,
            pady=8,
        )

        # ---------------------------------------------------------
        # Results
        # ---------------------------------------------------------

        self.rows = ctk.CTkScrollableFrame(
            self,
            label_text="Results",
        )

        self.rows.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=(0, 10),
        )

        # ---------------------------------------------------------
        # Console
        # ---------------------------------------------------------

        self.console = LogConsole(self)

        self.console.pack(
            fill="x",
            padx=28,
            pady=(0, 20),
        )

        self.after(
            150,
            self.poll_events,
        )

    # =========================================================
    # Automatic API test runner
    # =========================================================

    def run(self):
        project = self.projects.active()

        if not project or not project["api_url"]:
            self.status.configure(text="Select a project with an API URL first.")
            return

        self.status.configure(text="Running API tests…")

        self.clear_rows()
        self.console.clear()

        self.console.write("Starting discovered endpoint checks.")

        def worker():
            # -------------------------------------------------
            # Create test run
            # -------------------------------------------------

            run = self.runs.create(
                project["id"],
                status="RUNNING",
                started_at=datetime.now(timezone.utc).isoformat(),
            )

            records = self.endpoints.list(
                project_id=project["id"],
                enabled=1,
            )

            passed = 0
            skipped = 0
            failed = 0
            gate_passed = 0
            gate_failed = 0

            # -------------------------------------------------
            # Shared HTTP client
            #
            # IMPORTANT:
            # Reuse the same connection for all requests.
            #
            # trust_env=False prevents environment/system
            # proxies from interfering with localhost tests.
            # -------------------------------------------------

            try:
                with httpx.Client(
                    timeout=httpx.Timeout(10.0),
                    trust_env=False,
                    follow_redirects=True,
                ) as client:

                    for endpoint in records:
                        method = endpoint["method"]
                        path = endpoint["path"]

                        name = f"{method} {path}"
                        counts_for_gate = include_in_release_gate(endpoint)

                        # -------------------------------------
                        # Build request URL
                        # -------------------------------------

                        target = url_for(
                            project["api_url"],
                            path,
                            endpoint["definition_json"],
                        )

                        # -------------------------------------
                        # Skip unresolved path parameters
                        # -------------------------------------

                        if target is None:
                            skipped += 1

                            reason = (
                                "A path parameter needs a documented "
                                "example, default, or enum value. "
                                "Use the manual runner with a real value."
                            )

                            saved = self.results.create(
                                run["id"],
                                name,
                                "SKIPPED",
                                endpoint_id=endpoint["id"],
                                details_json={
                                    "error": reason,
                                },
                            )

                            self.after(
                                0,
                                lambda item=saved, message=reason: (
                                    self.add_row(item),
                                    self.console.write(
                                        f"Skipped {item['name']}: " f"{message}"
                                    ),
                                ),
                            )

                            continue

                        # -------------------------------------
                        # Execute HTTP request
                        # -------------------------------------

                        result = run_request(
                            method,
                            target,
                            expected_status=expected_success_status(
                                endpoint["definition_json"]
                            ),
                            body=baseline_body(endpoint["definition_json"]),
                            client=client,
                        )

                        # -------------------------------------
                        # Determine result status
                        # -------------------------------------

                        if result.passed:
                            passed += 1
                            if counts_for_gate:
                                gate_passed += 1
                            status = "PASSED"
                        else:
                            failed += 1
                            if counts_for_gate:
                                gate_failed += 1
                            status = "FAILED"

                        # -------------------------------------
                        # Save result
                        # -------------------------------------

                        saved = self.results.create(
                            run["id"],
                            name,
                            status,
                            endpoint_id=endpoint["id"],
                            duration_ms=result.duration_ms,
                            details_json={
                                "error": result.error,
                                "status_code": result.status_code,
                                "response": prepare_response(result.response_text),
                            },
                        )

                        # -------------------------------------
                        # Update GUI
                        # -------------------------------------

                        self.after(
                            0,
                            lambda item=saved: (
                                self.add_row(item),
                                self.console.write(
                                    f"{item['status']}: "
                                    f"{item['name']} "
                                    f"({item['duration_ms'] or 0} ms)"
                                ),
                            ),
                        )

            except Exception as error:
                self.after(
                    0,
                    lambda message=str(error): (
                        self.console.write(f"Test runner error: {message}"),
                        self.status.configure(
                            text="API test run encountered an error."
                        ),
                    ),
                )

            # -------------------------------------------------
            # Finish run
            # -------------------------------------------------

            self.runs.update(
                run["id"],
                status="COMPLETED",
                finished_at=datetime.now(timezone.utc).isoformat(),
                summary_json={
                    "passed": passed,
                    "failed": failed,
                    "skipped": skipped,
                    "total": len(records),
                    "gate_passed": gate_passed,
                    "gate_failed": gate_failed,
                    "gate_executed": gate_passed + gate_failed,
                },
            )

            summary = f"Completed: {passed}/{len(records)} passed"

            if failed:
                summary += f", {failed} failed"

            if skipped:
                summary += f", {skipped} skipped"

            summary += "."

            self.after(
                0,
                lambda message=summary: (
                    self.status.configure(text=message),
                    self.console.write(message),
                ),
            )

        Thread(
            target=worker,
            daemon=True,
        ).start()

    # =========================================================
    # Clear result rows
    # =========================================================

    def clear_rows(self):
        for child in self.rows.winfo_children():
            child.destroy()

    # =========================================================
    # Add result row
    # =========================================================

    def add_row(self, item):
        details = item.get(
            "details_json",
            {},
        )

        status = item["status"]

        duration = item.get("duration_ms")

        duration_text = f"{duration} ms" if duration is not None else "— ms"

        ExpandableResult(
            self.rows,
            item["name"],
            status,
            duration_text,
            [
                (
                    "HTTP status",
                    details.get("status_code"),
                ),
                (
                    "Duration",
                    (f"{duration} ms" if duration is not None else "Not recorded"),
                ),
                (
                    "Error / reason",
                    details.get("error"),
                ),
                (
                    "Request",
                    item["name"],
                ),
            ],
            details.get("response"),
        ).pack(
            fill="x",
            padx=4,
            pady=3,
        )

    # =========================================================
    # Manual API test
    # =========================================================

    def run_manual(self):
        project = self.projects.active()
        path = self.manual_path.get().strip()

        if not project or not project["api_url"] or not path:
            self.status.configure(text=("Select a project and enter " "a manual path."))
            return

        method = self.manual_method.get()

        name = f"{method} {path}"

        self.status.configure(text=f"Running {name}…")

        self.console.clear()

        self.console.write(f"Starting manual check: {name}")

        def worker():
            run = self.runs.create(
                project["id"],
                status="RUNNING",
                started_at=datetime.now(timezone.utc).isoformat(),
            )

            url = project["api_url"].rstrip("/") + (
                path if path.startswith("/") else f"/{path}"
            )

            # ---------------------------------------------
            # Use a dedicated client for this single
            # manual request.
            # ---------------------------------------------

            with httpx.Client(
                timeout=httpx.Timeout(10.0),
                trust_env=False,
                follow_redirects=True,
            ) as client:

                result = run_request(
                    method,
                    url,
                    client=client,
                )

            status = "PASSED" if result.passed else "FAILED"

            saved = self.results.create(
                run["id"],
                name,
                status,
                duration_ms=result.duration_ms,
                details_json={
                    "error": result.error,
                    "status_code": result.status_code,
                    "response": prepare_response(result.response_text),
                },
            )

            self.runs.update(
                run["id"],
                status="COMPLETED",
                finished_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=result.duration_ms,
                summary_json={
                    "passed": int(result.passed),
                    "failed": int(not result.passed),
                    "skipped": 0,
                    "total": 1,
                },
            )

            self.after(
                0,
                lambda: (
                    self.clear_rows(),
                    self.add_row(saved),
                    self.status.configure(text=f"{name}: {status}"),
                    self.console.write(
                        f"{status}: " f"{name} " f"({result.duration_ms or 0} ms)"
                    ),
                ),
            )

        Thread(
            target=worker,
            daemon=True,
        ).start()

    # =========================================================
    # TestManager event polling
    # =========================================================

    def poll_events(self):
        for event in self.manager.poll():
            if event.kind == "log":
                self.console.write(event.payload["message"])

        self.after(
            150,
            self.poll_events,
        )
