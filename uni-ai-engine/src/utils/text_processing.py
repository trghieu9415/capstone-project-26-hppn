import re
import unicodedata


def normalize_unicode(text: str) -> str:
    if not text:
        return ""
    return unicodedata.normalize("NFC", text)


def clean_whitespace(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def remove_unprintable_chars(text: str) -> str:
    if not text:
        return ""

    return "".join(
        ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in ["\n", "\t"]
    )


def clean_text_pipeline(raw_text: str) -> str:
    if not raw_text:
        return ""

    text = normalize_unicode(raw_text)
    text = remove_unprintable_chars(text)
    text = clean_whitespace(text)

    return text
