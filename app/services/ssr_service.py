from __future__ import annotations

import numpy as np
import polars as pl
from semantic_similarity_rating import ResponseRater

from app.services.constants import LIKERT_REFERENCE_SETS

_RATERS: dict[str, ResponseRater] = {}


def _build_reference_df(language: str) -> pl.DataFrame:
    refs = LIKERT_REFERENCE_SETS[language]
    return pl.DataFrame(
        {
            "id": ["default"] * 5,
            "int_response": [1, 2, 3, 4, 5],
            "sentence": refs,
        }
    )


def get_rater(language: str) -> ResponseRater:
    if language not in _RATERS:
        _RATERS[language] = ResponseRater(_build_reference_df(language))
    return _RATERS[language]


def score_texts_to_pmfs(texts: list[str], language: str) -> np.ndarray:
    if not texts:
        return np.empty((0, 5))
    rater = get_rater(language)
    return rater.get_response_pmfs("default", texts, temperature=1.0, epsilon=0.01)


def expected_scores(pmfs: np.ndarray) -> np.ndarray:
    scale = np.array([1, 2, 3, 4, 5], dtype=float)
    return (pmfs * scale[None, :]).sum(axis=1)


def pmf_to_argmax_score(pmf: np.ndarray) -> int:
    return int(np.argmax(pmf) + 1)

