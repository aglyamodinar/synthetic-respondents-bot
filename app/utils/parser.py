import csv
import io


def parse_txt_stimuli(raw: str, default_lang: str) -> list[dict]:
    out = []
    for idx, line in enumerate(raw.splitlines(), start=1):
        text = line.strip()
        if not text:
            continue
        out.append(
            {
                "stimulus_id": f"S{idx}",
                "stimulus_text": text,
                "category": "other",
                "language": default_lang,
            }
        )
    return out


def parse_csv_stimuli(raw: str, default_lang: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(raw))
    required = {"stimulus_id", "stimulus_text"}
    missing = required - set(reader.fieldnames or [])
    if missing:
        raise ValueError(f"CSV missing columns: {sorted(missing)}")

    out = []
    for row in reader:
        sid = (row.get("stimulus_id") or "").strip()
        txt = (row.get("stimulus_text") or "").strip()
        if not sid or not txt:
            continue
        out.append(
            {
                "stimulus_id": sid,
                "stimulus_text": txt,
                "category": (row.get("category") or "other").strip() or "other",
                "language": (row.get("language") or default_lang).strip() or default_lang,
            }
        )
    return out

