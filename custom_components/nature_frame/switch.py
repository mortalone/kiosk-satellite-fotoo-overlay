from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo

from .catalog import NatureFrameCatalog
from .const import DOMAIN
from .selection import async_update_gallery_selection, selected_gallery_keys


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    catalog: NatureFrameCatalog = hass.data[DOMAIN][entry.entry_id]
    entities = [
        NatureFrameGallerySwitch(hass, entry, catalog, key)
        for key in catalog.gallery_keys()
    ]
    async_add_entities(entities, True)


class NatureFrameGallerySwitch(SwitchEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:image-multiple"

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        catalog: NatureFrameCatalog,
        gallery_key: str,
    ) -> None:
        self.hass = hass
        self.entry = entry
        self.catalog = catalog
        self.gallery_key = gallery_key
        gallery = catalog.gallery(gallery_key)
        self._attr_name = gallery.title if gallery else gallery_key
        self._attr_unique_id = f"nature_frame_gallery_{gallery_key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)},
            name="Nature Frame",
            manufacturer="Nature Frame",
            model="Streaming media gallery",
        )

    @property
    def is_on(self) -> bool:
        return self.gallery_key in selected_gallery_keys(
            self.entry, self.catalog.gallery_keys()
        )

    async def async_turn_on(self, **kwargs) -> None:
        available = self.catalog.gallery_keys()
        selected = selected_gallery_keys(self.entry, available)
        if self.gallery_key not in selected:
            selected.append(self.gallery_key)
        async_update_gallery_selection(self.hass, self.entry, selected)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        available = self.catalog.gallery_keys()
        selected = selected_gallery_keys(self.entry, available)
        selected = [key for key in selected if key != self.gallery_key]
        if not selected:
            raise HomeAssistantError(
                "At least one Nature Frame collection must remain enabled"
            )
        async_update_gallery_selection(self.hass, self.entry, selected)
        self.async_write_ha_state()
