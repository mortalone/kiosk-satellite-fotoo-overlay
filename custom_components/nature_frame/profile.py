from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.util import slugify

PROFILE_ID = "profile_id"
PROFILE_NAME = "profile_name"
SCREEN_RATIO = "screen_ratio"


def entry_profile_name(entry: ConfigEntry) -> str:
    value = entry.data.get(PROFILE_NAME)
    if isinstance(value, str) and value.strip():
        return value.strip()
    if entry.title and entry.title != "Nature Frame":
        return entry.title.removeprefix("Nature Frame · ").strip() or "Default"
    return "Default"


def entry_profile_id(entry: ConfigEntry) -> str:
    value = entry.data.get(PROFILE_ID)
    if isinstance(value, str) and value.strip():
        return value.strip()
    # Existing installs become the backwards-compatible Default profile.
    if not entry.data.get(PROFILE_NAME):
        return "default"
    return slugify(entry_profile_name(entry)) or "profile"


def entry_screen_ratio(entry: ConfigEntry) -> str:
    value = entry.options.get(SCREEN_RATIO, entry.data.get(SCREEN_RATIO, "16:9"))
    return str(value) if value else "16:9"
