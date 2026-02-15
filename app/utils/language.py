def detect_language(text: str) -> str:
    if not text:
        return "ru"
    # Simple MVP heuristic: Cyrillic -> ru, otherwise en.
    return "ru" if any("а" <= c.lower() <= "я" for c in text) else "en"

