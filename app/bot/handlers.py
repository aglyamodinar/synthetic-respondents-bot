from __future__ import annotations

from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message

from app.config import get_settings
from app.services.constants import MODES, SEGMENT_CATALOG
from app.services.study_service import (
    create_run,
    create_study,
    get_artifact_for_run,
    get_latest_study,
    get_study,
    list_history,
    latest_run_for_study,
    replace_stimuli,
    update_study_mode,
    update_study_question,
    update_study_segments,
)
from app.utils.language import detect_language
from app.utils.parser import parse_csv_stimuli, parse_txt_stimuli
from app.workers.tasks import run_study_task

router = Router()
settings = get_settings()


def _msg(lang: str, ru: str, en: str) -> str:
    return ru if lang == "ru" else en


def _parse_segments(raw: str) -> dict:
    segments = {}
    if not raw.strip():
        return segments
    chunks = [c.strip() for c in raw.split(";") if c.strip()]
    for chunk in chunks:
        if "=" not in chunk:
            continue
        key, values = chunk.split("=", 1)
        vals = [v.strip() for v in values.split(",") if v.strip()]
        if vals:
            segments[key.strip()] = vals
    return segments


def _validate_segments(segments: dict) -> tuple[list[str], list[str]]:
    bad_groups = [k for k in segments if k not in SEGMENT_CATALOG]
    bad_values: list[str] = []
    for group, values in segments.items():
        allowed = set(SEGMENT_CATALOG.get(group, []))
        for value in values:
            if value not in allowed:
                bad_values.append(f"{group}:{value}")
    return bad_groups, bad_values


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    lang = detect_language(message.text or "")
    await message.answer(
        _msg(
            lang,
            "Готово. Создайте исследование: /new_study <название>\nКоманды: /set_mode /set_segments /set_question /upload_stimuli /run /status /report /history",
            "Ready. Create a study: /new_study <title>\nCommands: /set_mode /set_segments /set_question /upload_stimuli /run /status /report /history",
        )
    )


@router.message(Command("new_study"))
async def cmd_new_study(message: Message) -> None:
    lang = detect_language(message.text or "")
    title = (message.text or "").replace("/new_study", "", 1).strip() or "Untitled Study"
    study_id = create_study(message.from_user.id, title, lang)
    await message.answer(
        _msg(
            lang,
            f"Создано исследование `{study_id}`.\nЗагрузите стимулы: /upload_stimuli (текстом или файлом).",
            f"Study `{study_id}` created.\nUpload stimuli via /upload_stimuli (text or file).",
        ),
        parse_mode="Markdown",
    )


@router.message(Command("set_mode"))
async def cmd_set_mode(message: Message) -> None:
    lang = detect_language(message.text or "")
    raw = (message.text or "").replace("/set_mode", "", 1).strip()
    if raw not in MODES:
        await message.answer(
            _msg(
                lang,
                f"Режимы: {', '.join(MODES.keys())}",
                f"Modes: {', '.join(MODES.keys())}",
            )
        )
        return
    study = get_latest_study(message.from_user.id)
    if not study:
        await message.answer(_msg(lang, "Нет активного исследования.", "No active study found."))
        return
    update_study_mode(study.id, raw)
    await message.answer(_msg(lang, f"Режим установлен: {raw}", f"Mode set: {raw}"))


@router.message(Command("set_segments"))
async def cmd_set_segments(message: Message) -> None:
    lang = detect_language(message.text or "")
    study = get_latest_study(message.from_user.id)
    if not study:
        await message.answer(_msg(lang, "Сначала создайте исследование.", "Create a study first."))
        return

    raw = (message.text or "").replace("/set_segments", "", 1).strip()
    if not raw:
        await message.answer(
            _msg(
                lang,
                "Формат: /set_segments adoption=early_adopters,late_majority;engagement=regular;activity=active",
                "Format: /set_segments adoption=early_adopters,late_majority;engagement=regular;activity=active",
            )
        )
        return

    segments = _parse_segments(raw)
    bad_groups, bad_values = _validate_segments(segments)
    if bad_groups:
        await message.answer(_msg(lang, f"Неизвестные группы: {bad_groups}", f"Unknown groups: {bad_groups}"))
        return
    if bad_values:
        await message.answer(
            _msg(
                lang,
                f"Неизвестные значения сегментов: {bad_values}",
                f"Unknown segment values: {bad_values}",
            )
        )
        return
    update_study_segments(study.id, segments)
    await message.answer(_msg(lang, "Сегменты обновлены.", "Segments updated."))


@router.message(Command("set_question"))
async def cmd_set_question(message: Message) -> None:
    study = get_latest_study(message.from_user.id)
    lang = study.language if study else detect_language(message.text or "")
    if not study:
        await message.answer(_msg(lang, "Сначала создайте исследование.", "Create a study first."))
        return
    raw = (message.text or "").replace("/set_question", "", 1).strip()
    if not raw:
        await message.answer(
            _msg(
                lang,
                "Формат: /set_question <текст вопроса>",
                "Format: /set_question <question text>",
            )
        )
        return
    update_study_question(study.id, raw)
    await message.answer(_msg(lang, "Вопрос обновлен.", "Question updated."))


@router.message(F.document)
async def file_upload(message: Message) -> None:
    study = get_latest_study(message.from_user.id)
    lang = study.language if study else detect_language(message.caption or "")
    if not study:
        await message.answer(_msg(lang, "Сначала создайте исследование.", "Create a study first."))
        return

    doc = message.document
    suffix = Path(doc.file_name).suffix.lower()
    if suffix not in {".txt", ".csv"}:
        await message.answer(_msg(lang, "Только .txt или .csv", "Only .txt or .csv supported"))
        return

    file = await message.bot.get_file(doc.file_id)
    content = await message.bot.download_file(file.file_path)
    raw = content.read().decode("utf-8")
    items = parse_csv_stimuli(raw, study.language) if suffix == ".csv" else parse_txt_stimuli(raw, study.language)
    count = replace_stimuli(study.id, items)
    await message.answer(_msg(lang, f"Загружено стимулов: {count}", f"Stimuli loaded: {count}"))


@router.message(Command("upload_stimuli"))
async def text_upload(message: Message) -> None:
    study = get_latest_study(message.from_user.id)
    lang = study.language if study else detect_language(message.text or "")
    if not study:
        await message.answer(_msg(lang, "Сначала создайте исследование.", "Create a study first."))
        return

    raw = (message.text or "").replace("/upload_stimuli", "", 1).strip()
    if not raw:
        await message.answer(
            _msg(
                lang,
                "Пришлите .txt/.csv файлом или вставьте строки после команды /upload_stimuli.",
                "Send a .txt/.csv file or paste lines after /upload_stimuli.",
            )
        )
        return
    items = parse_txt_stimuli(raw, study.language)
    count = replace_stimuli(study.id, items)
    await message.answer(_msg(lang, f"Загружено стимулов: {count}", f"Stimuli loaded: {count}"))


@router.message(Command("run"))
async def cmd_run(message: Message) -> None:
    study = get_latest_study(message.from_user.id)
    lang = study.language if study else detect_language(message.text or "")
    if not study:
        await message.answer(_msg(lang, "Сначала создайте исследование.", "Create a study first."))
        return
    respondent_count = MODES.get(study.mode, 250)
    run_id = create_run(study.id, settings.openrouter_model, respondent_count)
    run_study_task.delay(run_id)
    await message.answer(
        _msg(
            lang,
            f"Запуск `{run_id}` поставлен в очередь.",
            f"Run `{run_id}` has been queued.",
        ),
        parse_mode="Markdown",
    )


@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    study = get_latest_study(message.from_user.id)
    lang = study.language if study else detect_language(message.text or "")
    if not study:
        await message.answer(_msg(lang, "Нет исследований.", "No studies yet."))
        return
    run = latest_run_for_study(study.id)
    if not run:
        await message.answer(_msg(lang, "Запусков пока нет.", "No runs yet."))
        return
    await message.answer(
        _msg(
            lang,
            f"Run `{run.id}`: {run.status}\nCost: ${run.estimated_cost_usd:.4f}",
            f"Run `{run.id}`: {run.status}\nCost: ${run.estimated_cost_usd:.4f}",
        ),
        parse_mode="Markdown",
    )


@router.message(Command("report"))
async def cmd_report(message: Message) -> None:
    study = get_latest_study(message.from_user.id)
    lang = study.language if study else detect_language(message.text or "")
    if not study:
        await message.answer(_msg(lang, "Нет исследований.", "No studies yet."))
        return
    run = latest_run_for_study(study.id)
    if not run:
        await message.answer(_msg(lang, "Нет запусков.", "No runs yet."))
        return
    artifact = get_artifact_for_run(run.id)
    if not artifact or not Path(artifact.path).exists():
        await message.answer(_msg(lang, "Отчет еще не готов.", "Report is not ready yet."))
        return
    await message.answer_document(FSInputFile(artifact.path))


@router.message(Command("history"))
async def cmd_history(message: Message) -> None:
    lang = detect_language(message.text or "")
    studies = list_history(message.from_user.id)
    if not studies:
        await message.answer(_msg(lang, "История пуста.", "History is empty."))
        return
    lines = []
    for s in studies:
        lines.append(f"{s.id} | {s.title} | {s.mode} | {s.status}")
    await message.answer("\n".join(lines[:20]))


@router.message(Command("rerun"))
async def cmd_rerun(message: Message) -> None:
    raw = (message.text or "").replace("/rerun", "", 1).strip()
    study = get_study(raw) if raw else get_latest_study(message.from_user.id)
    lang = study.language if study else detect_language(message.text or "")
    if not study or study.telegram_user_id != message.from_user.id:
        await message.answer(_msg(lang, "Исследование не найдено.", "Study not found."))
        return
    respondent_count = MODES.get(study.mode, 250)
    run_id = create_run(study.id, settings.openrouter_model, respondent_count)
    run_study_task.delay(run_id)
    await message.answer(
        _msg(
            lang,
            f"Повторный запуск `{run_id}` поставлен в очередь.",
            f"Rerun `{run_id}` has been queued.",
        ),
        parse_mode="Markdown",
    )
