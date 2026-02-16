from __future__ import annotations

from typing import Iterable

from sqlalchemy import desc, select

from app.config import get_settings
from app.db.models import Artifact, Metric, Run, Study, Stimulus
from app.db.session import SessionLocal
from app.services.constants import MODES

settings = get_settings()


def create_study(telegram_user_id: int, title: str, language: str) -> str:
    question = settings.default_question_ru if language == "ru" else settings.default_question_en
    with SessionLocal() as db:
        prev_stmt = (
            select(Study)
            .where(Study.telegram_user_id == telegram_user_id)
            .order_by(desc(Study.created_at))
            .limit(1)
        )
        prev_study = db.execute(prev_stmt).scalar_one_or_none()
        mode = prev_study.mode if prev_study and prev_study.mode in MODES else "pilot"
        study = Study(
            telegram_user_id=telegram_user_id,
            title=title,
            language=language,
            question_text=question,
            mode=mode,
            segments={},
            status="draft",
        )
        db.add(study)
        db.commit()
        db.refresh(study)
        return study.id


def get_latest_study(telegram_user_id: int) -> Study | None:
    with SessionLocal() as db:
        stmt = (
            select(Study)
            .where(Study.telegram_user_id == telegram_user_id)
            .order_by(desc(Study.created_at))
            .limit(1)
        )
        return db.execute(stmt).scalar_one_or_none()


def get_study(study_id: str) -> Study | None:
    with SessionLocal() as db:
        return db.get(Study, study_id)


def update_study_mode(study_id: str, mode: str) -> None:
    if mode not in MODES:
        raise ValueError(f"Unknown mode {mode}.")
    with SessionLocal() as db:
        study = db.get(Study, study_id)
        if not study:
            raise ValueError("Study not found.")
        study.mode = mode
        db.commit()


def update_study_segments(study_id: str, segments: dict) -> None:
    with SessionLocal() as db:
        study = db.get(Study, study_id)
        if not study:
            raise ValueError("Study not found.")
        study.segments = segments
        db.commit()


def update_study_question(study_id: str, question_text: str) -> None:
    with SessionLocal() as db:
        study = db.get(Study, study_id)
        if not study:
            raise ValueError("Study not found.")
        study.question_text = question_text.strip()
        db.commit()


def replace_stimuli(study_id: str, items: Iterable[dict]) -> int:
    with SessionLocal() as db:
        study = db.get(Study, study_id)
        if not study:
            raise ValueError("Study not found.")
        db.query(Stimulus).filter(Stimulus.study_id == study_id).delete()
        for item in items:
            db.add(
                Stimulus(
                    study_id=study_id,
                    stimulus_id=item["stimulus_id"],
                    stimulus_text=item["stimulus_text"],
                    category=item.get("category", "other"),
                    language=item.get("language", study.language),
                )
            )
        study.status = "ready"
        db.commit()
        return db.query(Stimulus).filter(Stimulus.study_id == study_id).count()


def create_run(study_id: str, model_name: str, respondent_count: int) -> str:
    with SessionLocal() as db:
        run = Run(
            study_id=study_id,
            model_name=model_name,
            respondent_count=respondent_count,
            status="queued",
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run.id


def list_history(telegram_user_id: int, limit: int = 20) -> list[Study]:
    with SessionLocal() as db:
        stmt = (
            select(Study)
            .where(Study.telegram_user_id == telegram_user_id)
            .order_by(desc(Study.created_at))
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())


def latest_run_for_study(study_id: str) -> Run | None:
    with SessionLocal() as db:
        stmt = select(Run).where(Run.study_id == study_id).order_by(desc(Run.created_at)).limit(1)
        return db.execute(stmt).scalar_one_or_none()


def get_metrics_for_run(run_id: str) -> list[Metric]:
    with SessionLocal() as db:
        stmt = select(Metric).where(Metric.run_id == run_id)
        return list(db.execute(stmt).scalars().all())


def get_artifact_for_run(run_id: str, artifact_type: str = "pdf") -> Artifact | None:
    with SessionLocal() as db:
        stmt = (
            select(Artifact)
            .where(Artifact.run_id == run_id, Artifact.artifact_type == artifact_type)
            .order_by(desc(Artifact.created_at))
            .limit(1)
        )
        return db.execute(stmt).scalar_one_or_none()
