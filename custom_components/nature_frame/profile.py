from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.util import slugify

PROFILE_ID = "profile_id"
PROFILE_NAME = "profile_name"
SCREEN_RATIO = "screen_ratio"

FILL_METHOD = "fill_method"
FILL_SAMPLE_SIZE = "fill_sample_size"
FILL_BLUR_RADIUS = "fill_blur_radius"

FILL_OFF = "Off"
FILL_SOLID = "Solid color"
FILL_EDGE = "Edge stretch"
FILL_EDGE_BLUR = "Edge stretch + blur"
FILL_MIRROR = "Mirror"

FILL_METHODS = (
    FILL_OFF,
    FILL_SOLID,
    FILL_EDGE,
    FILL_EDGE_BLUR,
    FILL_MIRROR,
)

DEFAULT_FILL_METHOD = FILL_SOLID
DEFAULT_FILL_SAMPLE_SIZE = 8
DEFAULT_FILL_BLUR_RADIUS = 10


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


def entry_fill_method(entry: ConfigEntry) -> str:
    value = entry.options.get(
        FILL_METHOD,
        entry.data.get(FILL_METHOD, DEFAULT_FILL_METHOD),
    )
    value = str(value)
    return value if value in FILL_METHODS else DEFAULT_FILL_METHOD


def entry_fill_sample_size(entry: ConfigEntry) -> int:
    value = entry.options.get(
        FILL_SAMPLE_SIZE,
        entry.data.get(FILL_SAMPLE_SIZE, DEFAULT_FILL_SAMPLE_SIZE),
    )
    try:
        return max(1, min(32, int(value)))
    except (TypeError, ValueError):
        return DEFAULT_FILL_SAMPLE_SIZE


def entry_fill_blur_radius(entry: ConfigEntry) -> int:
    value = entry.options.get(
        FILL_BLUR_RADIUS,
        entry.data.get(FILL_BLUR_RADIUS, DEFAULT_FILL_BLUR_RADIUS),
    )
    try:
        return max(0, min(30, int(value)))
    except (TypeError, ValueError):
        return DEFAULT_FILL_BLUR_RADIUS
