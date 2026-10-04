from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


def selected_gallery_keys(
    entry: ConfigEntry,
    available: list[str],
) -> list[str]:
    raw = entry.options.get("galleries")
    if isinstance(raw, list):
        selected = [str(key) for key in raw if str(key) in available]
        if selected:
            return selected

    legacy = entry.options.get("gallery")
    if isinstance(legacy, str) and legacy in available:
        return [legacy]

    return available[:1]


def async_update_gallery_selection(
    hass: HomeAssistant,
    entry: ConfigEntry,
    selected: list[str],
) -> None:
    options = {**entry.options, "galleries": list(dict.fromkeys(selected))}
    if len(selected) == 1:
        options["gallery"] = selected[0]
    else:
        options.pop("gallery", None)
    hass.config_entries.async_update_entry(entry, options=options)
