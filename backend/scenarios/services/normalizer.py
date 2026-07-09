import base64
import codecs
import re
import unicodedata

ZERO_WIDTH = re.compile("[\u200b\u200c\u200d\ufeff]")
WHITESPACE = re.compile(r"\s+")
LEET_MAP = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"})


def normalize_text(text: str) -> dict:
    normalized = unicodedata.normalize("NFKC", text or "")
    normalized = ZERO_WIDTH.sub("", normalized)
    normalized = WHITESPACE.sub(" ", normalized).strip()
    leetspeak = normalized.translate(LEET_MAP)
    decoded = []

    for token in re.findall(r"[A-Za-z0-9+/=]{12,}", normalized):
        try:
            raw = base64.b64decode(token, validate=True)
            if len(raw) <= 2048:
                candidate = raw.decode("utf-8")
                decoded.append({"type": "base64", "source": token[:40], "value": candidate})
        except Exception:
            pass

    try:
        rot13 = codecs.decode(normalized, "rot_13")
        if rot13 != normalized:
            decoded.append({"type": "rot13", "source": normalized[:40], "value": rot13})
    except Exception:
        pass

    views = [text or "", normalized, leetspeak] + [item["value"] for item in decoded]
    return {
        "raw": text or "",
        "normalized": normalized,
        "leetspeak": leetspeak,
        "decoded": decoded,
        "views": views,
    }
