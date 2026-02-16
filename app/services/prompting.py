from app.services.constants import LIKERT_REFERENCE_SETS


def _anchor_phrase(language: str, respondent_idx: int) -> str:
    lang = language if language in LIKERT_REFERENCE_SETS else "ru"
    anchors = LIKERT_REFERENCE_SETS[lang]
    return anchors[respondent_idx % len(anchors)]


def build_prompt(
    *,
    language: str,
    question_text: str,
    stimulus_text: str,
    segment_key: str,
    respondent_idx: int,
) -> str:
    lang = language if language in {"ru", "en"} else "ru"
    anchor = _anchor_phrase(lang, respondent_idx)

    if lang == "en":
        return (
            f"Segment profile: {segment_key}.\n"
            f"Synthetic respondent #{respondent_idx + 1}.\n"
            f"Stimulus:\n{stimulus_text}\n\n"
            f"Question:\n{question_text}\n\n"
            f"Start the first sentence exactly with: '{anchor}'.\n"
            "Then add 1-2 short reasons from this respondent's perspective.\n"
            "Keep the answer concise (1-3 sentences), as a real consumer."
        )

    return (
        f"Профиль сегмента: {segment_key}.\n"
        f"Синтетический респондент #{respondent_idx + 1}.\n"
        f"Стимул:\n{stimulus_text}\n\n"
        f"Вопрос:\n{question_text}\n\n"
        f"Начните первое предложение строго с фразы: '{anchor}'.\n"
        "После этого добавьте 1-2 короткие причины от лица этого респондента.\n"
        "Дайте краткий свободный ответ (1-3 предложения) как реальный потребитель."
    )
