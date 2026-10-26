"""
Convert Uzbek Latin text to the updated alphabet (28 letters, 2026 reform):

    Sh -> Ş    Ch -> Ç    O' -> Ö    G' -> Ğ

"Ng" stays as a letter combination, and the tutuq belgisi (ta'lim, ma'lumot)
stays an apostrophe.

Proper names are left as they are: project and brand names (Oqqushlar,
oqqushlar.uz, ShohzoDev, BuildBest...), the owner's name, domains, and
English/technical terms (schema-per-tenant, health-check). CamelCase words,
anything with a digit or a dot inside, and words in PROTECTED are skipped.
"""

import re

# Lower-case forms of words that must never be converted.
PROTECTED = {
    # names
    "shohzod", "shohzodev", "oqqushlar", "english",
    # technical / English terms used inside Uzbek sentences
    "schema", "schema-per-tenant", "health-check", "check", "dashboard", "push",
    "cache", "fetch", "branch", "switch", "chrome", "tech", "charset", "stylesheet",
    "django", "postgresql", "telegram", "github", "cloudflare",
}

_APOSTROPHES = "'ʻ‘’`"
_TOKEN = re.compile(r"[^\s«»\"()\[\]{},;:!?—–/|·<>=]+")
_OG = re.compile(r"([oOgG])[" + _APOSTROPHES + r"]")
_OG_MAP = {"o": "ö", "O": "Ö", "g": "ğ", "G": "Ğ"}


def _is_protected(token):
    core = token.strip(_APOSTROPHES + ".")
    lower = core.lower()
    if not core or lower in PROTECTED:
        return True
    # brand + Uzbek suffix: Oqqushlar'da, Django'da
    if any(lower.startswith(p + a) for p in PROTECTED for a in _APOSTROPHES):
        return True
    if any(ch.isdigit() for ch in core):
        return True
    if "." in core:  # domains, file names: oqqushlar.uz
        return True
    if any(ch.isupper() for ch in core[1:]) and not core.isupper():  # CamelCase: ShohzoDev
        return True
    return False


def _convert_token(token):
    if token.strip(_APOSTROPHES + ".").lower() in PROTECTED:  # schema-per-tenant, health-check
        return token
    if "-" in token.strip("-"):
        # Hyphenated words are judged part by part: AI-yordamchi -> AI-yordamçi
        return "-".join(_convert_token(part) if part else part for part in token.split("-"))
    if _is_protected(token):
        return token
    token = _OG.sub(lambda m: _OG_MAP[m.group(1)], token)
    token = token.replace("SH", "Ş").replace("Sh", "Ş").replace("sh", "ş")
    token = token.replace("CH", "Ç").replace("Ch", "Ç").replace("ch", "ç")
    return token


def to_new_latin(text):
    """Uzbek Latin (old orthography) -> updated alphabet. Idempotent."""
    if not text:
        return text
    return _TOKEN.sub(lambda m: _convert_token(m.group(0)), text)
