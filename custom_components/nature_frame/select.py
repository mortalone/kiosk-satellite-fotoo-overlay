from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, INDEX_FILE, MEDIA_ROOT, SELECTION_FILE


def _load_index() -> dict[str, Any]:
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as handle:
            data = json.load(handle)
            return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _gallery_options(index: dict[str, Any]) -> list[str]:
    collections = index.get("collections", {})
    if not isinstance(collections, dict):
        return []
    return sorted(str(key) for key in collections.keys())


def _read_selected(options: list[str]) -> str | None:
    try:
        value = Path(SELECTION_FILE).read_text(encoding="utf-8").strip()
        if value in options:
            return value
    except OSError:
        pass
    return options[0] if options else None


def _clear_directory(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for child in directory.iterdir():
        if child.is_file() or child.is_symlink():
            child.unlink(missing_ok=True)
        elif child.is_dir():
            shutil.rmtree(child)


def _link_file(source: Path, target: Path) -> None:
    try:
        os.link(source, target)
    except OSError:
        try:
            os.symlink(source, target)
        except OSError:
            shutil.copy2(source, target)


def _apply_gallery(gallery: str) -> None:
    index = _load_index()
    collections = index.get("collections", {})
    if gallery not in collections:
        raise ValueError(f"Unknown Nature Frame gallery: {gallery}")

    item = collections[gallery]
    if not isinstance(item, dict):
        raise ValueError(f"Invalid Nature Frame gallery metadata: {gallery}")

    active_root = Path(MEDIA_ROOT) / "active"
    for orientation in ("portrait", "landscape"):
        active = active_root / orientation
        _clear_directory(active)

        source_value = item.get(orientation)
        if not source_value:
            continue
        source = Path(str(source_value))
        if not source.exists():
            continue

        for image in sorted(source.glob("*.png")):
            _link_file(image, active / image.name)

        source_txt = source.parent / "SOURCE.txt"
        if source_txt.is_file():
            shutil.copy2(source_txt, active / "SOURCE.txt")

    Path(SELECTION_FILE).write_text(gallery + "\n", encoding="utf-8")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    async_add_entities([NatureFrameGallerySelect(hass)], True)


class NatureFrameGallerySelect(SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Gallery"
    _attr_icon = "mdi:image-multiple"
    _attr_unique_id = "nature_frame_gallery"

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._options: list[str] = []
        self._current: str | None = None
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)},
            name="Nature Frame",
            manufacturer="Nature Frame",
            model="Media gallery controller",
        )

    @property
    def options(self) -> list[str]:
        return self._options

    @property
    def current_option(self) -> str | None:
        return self._current

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        await self._async_refresh()

    async def _async_refresh(self) -> None:
        index = await self.hass.async_add_executor_job(_load_index)
        self._options = _gallery_options(index)
        self._current = await self.hass.async_add_executor_job(
            _read_selected, self._options
        )
        if self._current:
            await self.hass.async_add_executor_job(_apply_gallery, self._current)
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        if option not in self._options:
            raise ValueError(f"Unsupported gallery: {option}")
        await self.hass.async_add_executor_job(_apply_gallery, option)
        self._current = option
        self.async_write_ha_state()
