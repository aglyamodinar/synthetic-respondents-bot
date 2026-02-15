from fastapi import APIRouter, HTTPException

from app.services.study_service import get_artifact_for_run, get_metrics_for_run, get_study, latest_run_for_study

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/studies/{study_id}/status")
def study_status(study_id: str) -> dict:
    study = get_study(study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")
    run = latest_run_for_study(study_id)
    return {
        "study_id": study_id,
        "study_status": study.status,
        "run": {
            "id": run.id if run else None,
            "status": run.status if run else None,
            "cost_usd": run.estimated_cost_usd if run else None,
        },
    }


@router.get("/runs/{run_id}/metrics")
def run_metrics(run_id: str) -> dict:
    metrics = get_metrics_for_run(run_id)
    return {
        "run_id": run_id,
        "rows": [
            {
                "stimulus_pk": m.stimulus_pk,
                "segment_key": m.segment_key,
                "mean": m.mean,
                "median": m.median,
                "sd": m.sd,
                "distribution": m.distribution,
                "top2box": m.top2box,
                "bottom2box": m.bottom2box,
                "topbox": m.topbox,
            }
            for m in metrics
        ],
    }


@router.get("/runs/{run_id}/artifact")
def run_artifact(run_id: str) -> dict:
    artifact = get_artifact_for_run(run_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return {"run_id": run_id, "artifact_type": artifact.artifact_type, "path": artifact.path}

