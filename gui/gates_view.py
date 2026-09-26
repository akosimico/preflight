from __future__ import annotations

import customtkinter as ctk

from core.gates import evaluate, latest_release_evidence, validate_thresholds
from core.projects import ProjectService
from core.timezone import format_pht
from database.repositories import LoadMetricsRepository, SettingsRepository, TestRunsRepository
from gui.theme import DANGER, MUTED, SUCCESS, SURFACE, SURFACE_ALT, WARNING


GATE_COPY = {
    "api_pass_rate": (
        "Minimum successful API tests (%)",
        "At least this percentage of API checks must pass.",
        "%",
        "minimum",
    ),
    "avg_response_ms": (
        "Maximum average response time (ms)",
        "The average time across all load-test requests must be at or below this limit.",
        "ms",
        "maximum",
    ),
    "p95_ms": (
        "95% of requests must finish within (ms)",
        "Only the slowest 5% of requests may take longer than this limit.",
        "ms",
        "maximum",
    ),
    "p99_ms": (
        "99% of requests must finish within (ms)",
        "Only the slowest 1% of requests may take longer than this limit.",
        "ms",
        "maximum",
    ),
    "error_rate": (
        "Maximum failed requests (%)",
        "No more than this percentage of load-test requests may fail.",
        "%",
        "maximum",
    ),
}


class GatesView(ctk.CTkFrame):
    """Release-rule editor and decision history for the active project."""

    def __init__(
        self,
        master,
        projects: ProjectService,
        runs: TestRunsRepository,
        settings: SettingsRepository,
        metrics: LoadMetricsRepository,
    ):
        super().__init__(master, fg_color="transparent")
        self.projects = projects
        self.runs = runs
        self.settings = settings
        self.metrics = metrics
        self.entries: dict[str, ctk.CTkEntry] = {}
        self.rules_open = True
        self.evaluated_evidence: tuple[int, int] | None = None

        ctk.CTkLabel(self, text="Deployment Gates", font=("Segoe UI", 28, "bold")).pack(
            anchor="w", padx=28, pady=(24, 4)
        )

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=28, pady=(0, 16))
        toolbar.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            toolbar,
            text=(
                "Release rules use the latest completed API check and the latest load test. "
                "Refresh updates the available evidence below."
            ),
            text_color=MUTED,
            justify="left",
            wraplength=720,
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(toolbar, text="REFRESH", width=110, command=self.refresh).grid(
            row=0, column=1, sticky="e", padx=(16, 0)
        )

        self.banner = ctk.CTkFrame(self, fg_color=SURFACE_ALT, corner_radius=12)
        self.banner.pack(fill="x", padx=28, pady=(0, 12))
        self.banner_title = ctk.CTkLabel(self.banner, text="AWAITING EVALUATION", font=("Segoe UI", 18, "bold"))
        self.banner_title.pack(anchor="w", padx=18, pady=(14, 2))
        self.banner_detail = ctk.CTkLabel(
            self.banner,
            text="Save your release rules to evaluate the latest API and load-test evidence.",
            text_color=MUTED,
        )
        self.banner_detail.pack(anchor="w", padx=18, pady=(0, 14))

        self.rules_header = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=12)
        self.rules_header.pack(fill="x", padx=28, pady=(0, 2))
        self.rules_toggle = ctk.CTkButton(
            self.rules_header,
            text="RELEASE RULES  ▾",
            anchor="w",
            fg_color="transparent",
            hover_color=SURFACE_ALT,
            command=self.toggle_rules,
        )
        self.rules_toggle.pack(fill="x", padx=6, pady=5)

        self.rules_body = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=12)
        self.rules_body.pack(fill="x", padx=28, pady=(0, 12))
        self._build_rules()

        self.results = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=12)
        self.results.pack(fill="x", padx=28, pady=(0, 12))
        self.result_title = ctk.CTkLabel(self.results, text="Evaluation results", font=("Segoe UI", 16, "bold"))
        self.result_title.pack(anchor="w", padx=18, pady=(14, 8))
        self.result_body = ctk.CTkFrame(self.results, fg_color="transparent")
        self.result_body.pack(fill="x", padx=12, pady=(0, 14))
        ctk.CTkLabel(
            self.result_body,
            text="No evaluation yet. Save the rules to evaluate the newest API and load-test evidence.",
            text_color=MUTED,
        ).pack(anchor="w", padx=6)

        self.history_panel = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=12)
        self.history_panel.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        ctk.CTkLabel(self.history_panel, text="Run history", font=("Segoe UI", 16, "bold")).pack(
            anchor="w", padx=18, pady=(14, 2)
        )
        ctk.CTkLabel(
            self.history_panel,
            text="Recent load-test runs. The newest API run and newest load run are used together when you evaluate.",
            text_color=MUTED,
        ).pack(anchor="w", padx=18, pady=(0, 10))
        self.history_body = ctk.CTkScrollableFrame(self.history_panel, fg_color="transparent", height=160)
        self.history_body.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.refresh()

    def _build_rules(self) -> None:
        saved = self.settings.get("gate_thresholds") or {}
        defaults = {"api_pass_rate": 95, "avg_response_ms": 500, "p95_ms": 800, "p99_ms": 1200, "error_rate": 2}
        for key, (title, description, unit, direction) in GATE_COPY.items():
            card = ctk.CTkFrame(self.rules_body, fg_color=SURFACE_ALT, corner_radius=10)
            card.pack(fill="x", padx=12, pady=6)
            card.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(card, text=title, font=("Segoe UI", 14, "bold")).grid(
                row=0, column=0, sticky="w", padx=14, pady=(10, 1)
            )
            ctk.CTkLabel(
                card,
                text=f"{description} This is a {direction} limit.",
                text_color=MUTED,
                wraplength=550,
                justify="left",
            ).grid(row=1, column=0, sticky="w", padx=14, pady=(0, 10))
            input_box = ctk.CTkFrame(card, fg_color="transparent")
            input_box.grid(row=0, column=1, rowspan=2, sticky="e", padx=14)
            entry = ctk.CTkEntry(input_box, width=150)
            entry.insert(0, str(saved.get(key, defaults[key])))
            entry.pack(side="left")
            ctk.CTkLabel(input_box, text=unit, text_color=MUTED).pack(side="left", padx=(8, 0))
            self.entries[key] = entry

        ctk.CTkButton(
            self.rules_body,
            text="SAVE RULES & EVALUATE LATEST EVIDENCE",
            command=self.evaluate,
        ).pack(anchor="e", padx=12, pady=(10, 14))

    def toggle_rules(self) -> None:
        self.rules_open = not self.rules_open
        if self.rules_open:
            self.rules_body.pack(fill="x", padx=28, pady=(0, 12), before=self.results)
            self.rules_toggle.configure(text="RELEASE RULES  ▾")
        else:
            self.rules_body.pack_forget()
            self.rules_toggle.configure(text="RELEASE RULES  ▸")

    def _thresholds(self) -> dict[str, float] | None:
        try:
            return validate_thresholds({key: entry.get() for key, entry in self.entries.items()})
        except ValueError as exc:
            self._set_banner("RULES NEED ATTENTION", str(exc), DANGER)
            return None

    def refresh(self) -> None:
        """Reload project run history without selecting or pinning a historical run."""
        project = self.projects.active()
        runs = self.runs.list(project_id=project["id"]) if project else []
        self.render_history(runs)

        thresholds = self._thresholds()
        if not thresholds:
            return
        api_run, load_run, _ = latest_release_evidence(
            runs,
            lambda run_id: self.metrics.list(test_run_id=run_id),
        )
        latest_evidence = (api_run["id"], load_run["id"]) if api_run and load_run else None
        if latest_evidence and latest_evidence != self.evaluated_evidence:
            self._set_banner(
                "LATEST EVIDENCE AVAILABLE",
                f"API Run #{api_run['id']} and Load Run #{load_run['id']} are ready to evaluate.",
                WARNING,
            )
        elif not latest_evidence and self.evaluated_evidence is None:
            self._set_banner(
                "MISSING RELEASE EVIDENCE",
                "Run both API preflight and load testing first. Security-only or incomplete runs cannot be evaluated.",
                WARNING,
            )

    def render_history(self, runs: list[dict]) -> None:
        for child in self.history_body.winfo_children():
            child.destroy()
        compatible = [run for run in reversed(runs) if self.metrics.list(test_run_id=run["id"])]
        if not compatible:
            ctk.CTkLabel(
                self.history_body,
                text="No completed load-test runs yet. Run load testing, then return here and press Refresh.",
                text_color=MUTED,
                justify="left",
            ).pack(anchor="w", padx=6, pady=8)
            return
        for run in compatible:
            metrics = self.metrics.list(test_run_id=run["id"])[0]
            gate_status = (run.get("gate_status") or "").lower()
            status = (gate_status or "Not evaluated").replace("_", " ").title()
            color = SUCCESS if gate_status == "passed" else DANGER if gate_status == "failed" else MUTED
            row = ctk.CTkFrame(self.history_body, fg_color=SURFACE_ALT, corner_radius=8)
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(
                row,
                text=f"Run #{run['id']}  ·  {format_pht(run.get('created_at'))}",
                font=("Segoe UI", 13, "bold"),
            ).pack(side="left", padx=12, pady=9)
            ctk.CTkLabel(
                row,
                text=f"{metrics.get('average_ms', 0):.1f} ms average  ·  {metrics.get('error_rate', 0):.1f}% errors",
                text_color=MUTED,
            ).pack(side="left", padx=(0, 12))
            ctk.CTkLabel(row, text=status, text_color=color).pack(side="right", padx=12)

    def evaluate(self) -> None:
        project = self.projects.active()
        if not project:
            self._set_banner("NO ACTIVE PROJECT", "Create or choose a project before evaluating release rules.", DANGER)
            return
        thresholds = self._thresholds()
        if not thresholds:
            return

        self.settings.set("gate_thresholds", thresholds)
        api_run, load_run, values = latest_release_evidence(
            self.runs.list(project_id=project["id"]),
            lambda run_id: self.metrics.list(test_run_id=run_id),
        )
        if not api_run or not load_run or not values:
            self._set_banner(
                "MISSING RELEASE EVIDENCE",
                "Run both API preflight and load testing first. Security-only or incomplete runs cannot be evaluated.",
                WARNING,
            )
            self.render_results([])
            return

        items = evaluate(values, thresholds)
        passed = all(item.passed for item in items)
        # TestRunsRepository uses the shared generic update method.  Persist in
        # the same uppercase format used by the workflow runner.
        self.runs.update(api_run["id"], gate_status="PASSED" if passed else "FAILED")
        self.evaluated_evidence = (api_run["id"], load_run["id"])
        detail = (
            f"{project['name']} · API Run #{api_run['id']} ({format_pht(api_run.get('created_at'))}) "
            f"· Load Run #{load_run['id']} ({format_pht(load_run.get('created_at'))})"
        )
        self._set_banner("READY TO DEPLOY" if passed else "NOT READY TO DEPLOY", detail, SUCCESS if passed else DANGER)
        self.render_results(items)
        self.refresh()
        if self.rules_open:
            self.toggle_rules()

    def _set_banner(self, title: str, detail: str, color: str) -> None:
        self.banner.configure(fg_color=color)
        self.banner_title.configure(text=title, text_color="#ffffff")
        self.banner_detail.configure(text=detail, text_color="#ffffff")

    def render_results(self, items) -> None:
        for child in self.result_body.winfo_children():
            child.destroy()
        if not items:
            ctk.CTkLabel(
                self.result_body,
                text="No compatible run is available for evaluation.",
                text_color=MUTED,
            ).pack(anchor="w", padx=6)
            return
        for item in items:
            title, _, unit, direction = GATE_COPY[item.name]
            color = SUCCESS if item.passed else DANGER
            icon = "✓" if item.passed else "✕"
            comparison = "meets" if item.passed else "does not meet"
            amount = abs(item.margin)
            if direction == "minimum":
                margin_text = f"{amount:.1f}{unit} {'above' if item.margin >= 0 else 'below'} minimum"
            else:
                margin_text = f"{amount:.1f}{unit} {'below' if item.margin >= 0 else 'above'} limit"
            row = ctk.CTkFrame(self.result_body, fg_color=SURFACE_ALT, corner_radius=8)
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=icon, text_color=color, font=("Segoe UI", 16, "bold"), width=28).pack(
                side="left", padx=(10, 2), pady=8
            )
            ctk.CTkLabel(row, text=title, font=("Segoe UI", 13, "bold")).pack(side="left", padx=(4, 10))
            ctk.CTkLabel(
                row,
                text=f"{item.actual:.1f}{unit} {comparison} {item.limit:.1f}{unit} · {margin_text}",
                text_color=MUTED,
            ).pack(side="left", padx=(0, 10))
