def build_prompt(
    *,
    language: str,
    question_text: str,
    stimulus_text: str,
    segment_key: str,
) -> str:
    if language == "en":
        return (
            f"Segment profile: {segment_key}.\n"
            f"Stimulus:\n{stimulus_text}\n\n"
            f"Question:\n{question_text}\n\n"
            "Give a concise free-text answer (1-3 sentences), as a real consumer."
        )

    return (
        f"Профиль сегмента: {segment_key}.\n"
        f"Стимул:\n{stimulus_text}\n\n"
        f"Вопрос:\n{question_text}\n\n"
        "Дайте краткий свободный ответ (1-3 предложения) как реальный потребитель."
    )

