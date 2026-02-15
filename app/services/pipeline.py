from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
from sqlalchemy import select

from app.config import get_settings
from app.db.models import Artifact, Metric, Run, Study, Stimulus, SyntheticResponse
from app.db.session import SessionLocal
from app.services.openrouter_client import OpenRouterClient
from app.services.pricing import estimate_cost_usd
from app.services.prompting import build_prompt
from app.services.report_pdf import build_report_pdf
from app.services.ssr_service import expected_scores, pmf_to_argmax_score, score_texts_to_pmfs
from app.utils.cache import get_cached_json, make_cache_key, set_cached_json
from app.utils.metrics import compute_metrics

settings = get_settings()


def _segment_keys(segments: dict) -> list[str]:
    if not segments:
        return ["all"]
    keys: list[str] = []
    for values in segments.values():
        if isinstance(values, list):
            keys.extend(str(v) for v in values if v)
    return keys or ["all"]


async def _generate_one(
    *,
    llm: OpenRouterClient,
    model: str,
    language: str,
    question_text: str,
    stimulus_text: str,
    segment_key: str,
    respondent_idx: int,
) -> dict:
    prompt = build_prompt(
        language=language,
        question_text=question_text,
        stimulus_text=stimulus_text,
        segment_key=segment_key,
    )
    cache_key = make_cache_key(
        {
            "model": model,
            "language": language,
            "question_text": question_text,
            "stimulus_text": stimulus_text,
            "segment_key": segment_key,
            "respondent_idx": respondent_idx,
        }
    )
    cached = get_cached_json(cache_key)
    if cached:
        return cached

    generated = await llm.generate_response(
        prompt=prompt,
        language=language,
        model=model,
        max_tokens=settings.max_output_tokens,
    )
    set_cached_json(cache_key, generated)
    return generated


async def execute_run_async(run_id: str) -> None:
    llm = OpenRouterClient()
    with SessionLocal() as db:
        run = db.get(Run, run_id)
        if not run:
            raise ValueError("Run not found.")
        study = db.get(Study, run.study_id)
        if not study:
            raise ValueError("Study not found.")
        stimuli = list(db.execute(select(Stimulus).where(Stimulus.study_id == study.id)).scalars())
        if not stimuli:
            raise ValueError("No stimuli loaded.")

        run.status = "running"
        run.started_at = datetime.utcnow()
        db.commit()

    total_in = 0
    total_out = 0
    grouped_rows: dict[tuple[int, str], list[dict]] = defaultdict(list)
    segments = _segment_keys(study.segments or {})

    for stimulus in stimuli:
        for respondent_idx in range(run.respondent_count):
            seg = segments[respondent_idx % len(segments)]
            generated = await _generate_one(
                llm=llm,
                model=run.model_name,
                language=study.language,
                question_text=study.question_text,
                stimulus_text=stimulus.stimulus_text,
                segment_key=seg,
                respondent_idx=respondent_idx,
            )
            txt = generated["text"]
            grouped_rows[(stimulus.id, seg)].append(
                {
                    "stimulus_pk": stimulus.id,
                    "segment_key": seg,
                    "respondent_idx": respondent_idx,
                    "response_text": txt,
                }
            )
            total_in += generated["usage"]["prompt_tokens"]
            total_out += generated["usage"]["completion_tokens"]

    metrics_rows: list[dict] = []
    enriched_responses: list[dict] = []

    for (stimulus_pk, segment_key), rows in grouped_rows.items():
        texts = [row["response_text"] for row in rows]
        pmfs = score_texts_to_pmfs(texts, study.language)
        exp = expected_scores(pmfs)
        discrete_scores = np.array([pmf_to_argmax_score(p) for p in pmfs], dtype=int)
        m = compute_metrics(discrete_scores)
        m["stimulus_pk"] = stimulus_pk
        m["segment_key"] = segment_key
        metrics_rows.append(m)

        for row, pmf, exp_score in zip(rows, pmfs, exp):
            enriched_responses.append(
                {
                    "stimulus_pk": stimulus_pk,
                    "segment_key": segment_key,
                    "respondent_idx": row["respondent_idx"],
                    "response_text": row["response_text"],
                    "pmf": pmf.tolist(),
                    "expected_score": float(exp_score),
                }
            )

    report_rows = []
    with SessionLocal() as db:
        run = db.get(Run, run_id)
        study = db.get(Study, run.study_id)
        stimulus_map = {s.id: s for s in db.execute(select(Stimulus).where(Stimulus.study_id == study.id)).scalars()}

        db.query(SyntheticResponse).filter(SyntheticResponse.run_id == run_id).delete()
        db.query(Metric).filter(Metric.run_id == run_id).delete()

        for row in enriched_responses:
            db.add(
                SyntheticResponse(
                    run_id=run_id,
                    stimulus_pk=row["stimulus_pk"],
                    segment_key=row["segment_key"],
                    respondent_idx=row["respondent_idx"],
                    response_text=row["response_text"],
                    pmf=row["pmf"],
                    expected_score=row["expected_score"],
                )
            )

        for row in metrics_rows:
            db.add(
                Metric(
                    run_id=run_id,
                    stimulus_pk=row["stimulus_pk"],
                    segment_key=row["segment_key"],
                    mean=row["mean"],
                    median=row["median"],
                    sd=row["sd"],
                    variance=row["variance"],
                    mode=row["mode"],
                    top2box=row["top2box"],
                    bottom2box=row["bottom2box"],
                    topbox=row["topbox"],
                    net_score=row["net_score"],
                    distribution=row["distribution"],
                    ci_mean_low=row["ci_mean_low"],
                    ci_mean_high=row["ci_mean_high"],
                    ci_t2b_low=row["ci_t2b_low"],
                    ci_t2b_high=row["ci_t2b_high"],
                )
            )
            report_rows.append(
                {
                    "stimulus_id": stimulus_map[row["stimulus_pk"]].stimulus_id,
                    "segment_key": row["segment_key"],
                    "mean": row["mean"],
                    "median": row["median"],
                    "sd": row["sd"],
                    "top2box": row["top2box"],
                    "bottom2box": row["bottom2box"],
                    "topbox": row["topbox"],
                }
            )

        report_path = settings.reports_path / f"{run_id}.pdf"
        build_report_pdf(
            path=Path(report_path),
            study_id=study.id,
            run_id=run_id,
            language=study.language,
            rows=report_rows,
        )
        db.add(Artifact(run_id=run_id, artifact_type="pdf", path=str(report_path)))

        run.token_input = total_in
        run.token_output = total_out
        run.estimated_cost_usd = estimate_cost_usd(run.model_name, total_in, total_out)
        run.status = "completed"
        run.finished_at = datetime.utcnow()
        study.status = "completed"
        db.commit()


def execute_run(run_id: str) -> None:
    try:
        asyncio.run(execute_run_async(run_id))
    except Exception as exc:
        with SessionLocal() as db:
            run = db.get(Run, run_id)
            if run:
                run.status = "failed"
                run.finished_at = datetime.utcnow()
                run.error_message = str(exc)
                db.commit()
        raise
