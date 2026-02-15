from app.services.pipeline import execute_run
from app.workers.celery_app import celery


@celery.task(name="run_study_task")
def run_study_task(run_id: str) -> str:
    execute_run(run_id)
    return run_id

