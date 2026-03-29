"""
Simple i18n module — Vietnamese (default) and English.

Usage:
    from src.i18n import t, set_lang

    set_lang("vi")  # or "en"
    print(t("app_title"))
    print(t("found_n", n=42))
"""

from src.i18n import vi, en


_LANGS = {
    "vi": vi.STRINGS,
    "en": en.STRINGS,
}

_current = "vi"


def set_lang(lang):
    """Set the active language. Supported: 'vi', 'en'."""
    global _current
    if lang in _LANGS:
        _current = lang


def get_lang():
    """Get the currently active language code."""
    return _current


def get_available_langs():
    """Return list of supported language codes."""
    return list(_LANGS.keys())


def t(key, **kwargs):
    """
    Get a translated string by key.
    Supports format placeholders: t("found_n", n=42) → "Tìm thấy 42 conversations"
    Falls back to the key itself if not found.
    """
    text = _LANGS.get(_current, _LANGS["vi"]).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text
