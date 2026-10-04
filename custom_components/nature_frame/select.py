from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .catalog import NatureFrameCatalog
from .const import DOMAIN
from .profile import entry_profile_id, entry_profile_name
from .selection import async_update_gallery_selection, selected_gallery_keys


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    catalog: NatureFrameCatalog = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NatureFrameGallerySelect(hass, entry, catalog)], True)


class NatureFrameGallerySelect(SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Single gallery"
    _attr_icon = "mdi:image-multiple"

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        catalog: NatureFrameCatalog,
    ) -> None:
        self.hass = hass
        self.entry = entry
        self.catalog = catalog

        profile_id = entry_profile_id(entry)
        profile_name = entry_profile_name(entry)
        self._attr_unique_id = (
            "nature_frame_gallery"
            if profile_id == "default"
            else f"nature_frame_{profile_id}_gallery"
        )
        device_identifier = (
            (DOMAIN, DOMAIN)
            if profile_id == "default"
            else (DOMAIN, f"profile_{profile_id}")
        )
        self._attr_device_info = DeviceInfo(
            identifiers={device_identifier},
            name=f"Nature Frame · {profile_name}",
            manufacturer="Nature Frame",
            model="Screen collection profile",
        )

    @property
    def options(self) -> list[str]:
        return self.catalog.gallery_keys()

    @property
    def current_option(self) -> str | None:
        selected = selected_gallery_keys(self.entry, self.options)
        return selected[0] if selected else None

    async def async_select_option(self, option: str) -> None:
        if option not in self.options:
            raise ValueError(f"Unsupported gallery: {option}")
        # Compatibility helper: selecting here intentionally returns this
        # screen profile to one active collection. Multi-select uses switches.
        async_update_gallery_selection(self.hass, self.entry, [option])
        self.async_write_ha_state()
