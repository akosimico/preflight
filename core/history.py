from database.repositories import LoadMetricsRepository,TestResultsRepository,TestRunsRepository
def runs_for_project(runs:TestRunsRepository,project_id:int): return list(reversed(runs.list(project_id=project_id)))
def compare_latest(runs:TestRunsRepository,metrics:LoadMetricsRepository,project_id:int):
    history=runs_for_project(runs,project_id)
    if len(history)<2:return None
    current,previous=history[0],history[1];return {"current":current,"previous":previous,"current_metrics":metrics.list(test_run_id=current["id"]),"previous_metrics":metrics.list(test_run_id=previous["id"])}
