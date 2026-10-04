from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .catalog import NatureFrameCatalog
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    catalog: NatureFrameCatalog = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NatureFrameGallerySelect(hass, entry, catalog)], True)


class NatureFrameGallerySelect(SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Gallery"
    _attr_icon = "mdi:image-multiple"
    _attr_unique_id = "nature_frame_gallery"

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        catalog: NatureFrameCatalog,
    ) -> None:
        self.hass = hass
        self.entry = entry
        self.catalog = catalog
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)},
            name="Nature Frame",
            manufacturer="Nature Frame",
            model="Streaming media gallery",
        )

    @property
    def options(self) -> list[str]:
        return self.catalog.gallery_keys()

    @property
    def current_option(self) -> str | None:
        selected = self.entry.options.get("gallery")
        if selected in self.options:
            return selected
        return self.options[0] if self.options else None

    async def async_select_option(self, option: str) -> None:
        if option not in self.options:
            raise ValueError(f"Unsupported gallery: {option}")
        self.hass.config_entries.async_update_entry(
            self.entry,
            options={**self.entry.options, "gallery": option},
        )
        self.async_write_ha_state()
