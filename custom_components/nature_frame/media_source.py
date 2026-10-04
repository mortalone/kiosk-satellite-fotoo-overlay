from __future__ import annotations

from typing import override

from homeassistant.components.media_player import BrowseError, MediaClass
from homeassistant.components.media_source import (
    BrowseMediaSource,
    MediaSource,
    MediaSourceItem,
    PlayMedia,
    Unresolvable,
)
from homeassistant.core import HomeAssistant

from .catalog import NatureFrameCatalog
from .const import DOMAIN


def _catalog(hass: HomeAssistant) -> NatureFrameCatalog:
    entries = hass.data.get(DOMAIN, {})
    if not entries:
        raise Unresolvable("Nature Frame is not configured")
    return next(iter(entries.values()))


def _selected_gallery(hass: HomeAssistant, catalog: NatureFrameCatalog) -> str:
    entries = hass.config_entries.async_entries(DOMAIN)
    selected = entries[0].options.get("gallery") if entries else None
    return selected if selected in catalog.galleries else catalog.gallery_keys()[0]


async def async_get_media_source(hass: HomeAssistant) -> "NatureFrameMediaSource":
    return NatureFrameMediaSource(hass)


class NatureFrameMediaSource(MediaSource):
    name = "Nature Frame"

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(DOMAIN)
        self.hass = hass

    @override
    async def async_resolve_media(self, item: MediaSourceItem) -> PlayMedia:
        catalog = _catalog(self.hass)
        await catalog.async_refresh()
        parts = [part for part in item.identifier.split("/") if part]
        if len(parts) != 4 or parts[0] != "item":
            raise Unresolvable(f"Could not resolve Nature Frame item: {item.identifier}")
        _, gallery_key, orientation, image_key = parts
        for image in catalog.images(gallery_key, orientation):
            if image.key == image_key:
                return PlayMedia(image.url, image.mime_type)
        raise Unresolvable(f"Unknown Nature Frame item: {item.identifier}")

    @override
    async def async_browse_media(self, item: MediaSourceItem) -> BrowseMediaSource:
        catalog = _catalog(self.hass)
        await catalog.async_refresh()
        identifier = item.identifier or ""

        if not identifier:
            return BrowseMediaSource(
                domain=DOMAIN,
                identifier=None,
                media_class=MediaClass.APP,
                media_content_type="",
                title="Nature Frame",
                can_play=False,
                can_expand=True,
                children_media_class=MediaClass.DIRECTORY,
                children=[
                    self._folder("active/portrait", "Active gallery · Portrait"),
                    self._folder("active/landscape", "Active gallery · Landscape"),
                    self._folder("galleries", "All galleries"),
                ],
            )

        if identifier == "galleries":
            children = []
            for key in catalog.gallery_keys():
                gallery = catalog.gallery(key)
                if gallery:
                    children.append(self._folder(f"gallery/{key}", gallery.title))
            return self._directory(identifier, "All galleries", children)

        if identifier.startswith("gallery/") and identifier.count("/") == 1:
            key = identifier.split("/", 1)[1]
            gallery = catalog.gallery(key)
            if not gallery:
                raise BrowseError("Unknown Nature Frame gallery")
            return self._directory(
                identifier,
                gallery.title,
                [
                    self._folder(f"gallery/{key}/portrait", "Portrait"),
                    self._folder(f"gallery/{key}/landscape", "Landscape"),
                ],
            )

        if identifier in {"active/portrait", "active/landscape"}:
            orientation = identifier.split("/", 1)[1]
            key = _selected_gallery(self.hass, catalog)
            gallery = catalog.gallery(key)
            return self._directory(
                identifier,
                f"{gallery.title if gallery else key} · {orientation.title()}",
                self._image_children(catalog, key, orientation),
            )

        parts = identifier.split("/")
        if len(parts) == 3 and parts[0] == "gallery":
            _, key, orientation = parts
            if orientation not in {"portrait", "landscape"}:
                raise BrowseError("Unknown orientation")
            gallery = catalog.gallery(key)
            if not gallery:
                raise BrowseError("Unknown Nature Frame gallery")
            return self._directory(
                identifier,
                f"{gallery.title} · {orientation.title()}",
                self._image_children(catalog, key, orientation),
            )

        raise BrowseError("Unknown Nature Frame item")

    def _folder(self, identifier: str, title: str) -> BrowseMediaSource:
        return BrowseMediaSource(
            domain=DOMAIN,
            identifier=identifier,
            media_class=MediaClass.DIRECTORY,
            media_content_type="",
            title=title,
            can_play=False,
            can_expand=True,
            children_media_class=MediaClass.IMAGE,
        )

    def _directory(
        self,
        identifier: str,
        title: str,
        children: list[BrowseMediaSource],
    ) -> BrowseMediaSource:
        return BrowseMediaSource(
            domain=DOMAIN,
            identifier=identifier,
            media_class=MediaClass.DIRECTORY,
            media_content_type="",
            title=title,
            can_play=False,
            can_expand=True,
            children_media_class=MediaClass.IMAGE,
            children=children,
        )

    def _image_children(
        self,
        catalog: NatureFrameCatalog,
        gallery_key: str,
        orientation: str,
    ) -> list[BrowseMediaSource]:
        return [
            BrowseMediaSource(
                domain=DOMAIN,
                identifier=f"item/{gallery_key}/{orientation}/{image.key}",
                media_class=MediaClass.IMAGE,
                media_content_type=image.mime_type,
                title=image.title,
                can_play=True,
                can_expand=False,
            )
            for image in catalog.images(gallery_key, orientation)
        ]
