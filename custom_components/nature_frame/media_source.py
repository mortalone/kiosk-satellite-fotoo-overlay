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
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .catalog import NatureFrameCatalog, NatureImage
from .const import DOMAIN
from .profile import entry_profile_id, entry_profile_name
from .selection import selected_gallery_keys

BALANCED_ITEMS_PER_COLLECTION = 80


def _catalog(hass: HomeAssistant) -> NatureFrameCatalog:
    entries = hass.data.get(DOMAIN, {})
    if not entries:
        raise Unresolvable("Nature Frame is not configured")
    return next(iter(entries.values()))


def _profile_entries(hass: HomeAssistant) -> list[ConfigEntry]:
    return hass.config_entries.async_entries(DOMAIN)


def _profile_entry(hass: HomeAssistant, profile_id: str) -> ConfigEntry | None:
    entries = _profile_entries(hass)
    for entry in entries:
        if entry_profile_id(entry) == profile_id:
            return entry
    if profile_id == "default" and entries:
        return entries[0]
    return None


def _selected_for_entry(
    entry: ConfigEntry,
    catalog: NatureFrameCatalog,
) -> list[str]:
    return selected_gallery_keys(entry, catalog.gallery_keys())


def _profile_thumbnail(
    entry: ConfigEntry,
    catalog: NatureFrameCatalog,
) -> str | None:
    for key in _selected_for_entry(entry, catalog):
        gallery = catalog.gallery(key)
        if gallery and gallery.thumbnail:
            return gallery.thumbnail
    return None


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
        if len(parts) not in {4, 5} or parts[0] != "item":
            raise Unresolvable(
                f"Could not resolve Nature Frame item: {item.identifier}"
            )
        _, gallery_key, orientation, image_key = parts[:4]
        for image in catalog.images(gallery_key, orientation):
            if image.key == image_key:
                return PlayMedia(image.url, image.mime_type)
        raise Unresolvable(f"Unknown Nature Frame item: {item.identifier}")

    @override
    async def async_browse_media(self, item: MediaSourceItem) -> BrowseMediaSource:
        catalog = _catalog(self.hass)
        await catalog.async_refresh()
        identifier = item.identifier or ""
        profiles = _profile_entries(self.hass)
        first_profile = profiles[0] if profiles else None
        root_thumb = _profile_thumbnail(first_profile, catalog) if first_profile else None

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
                thumbnail=root_thumb,
                children=[
                    self._folder("profiles", "Screens / profiles", root_thumb),
                    self._folder("galleries", "All collections"),
                    self._folder("private", "Private collections"),
                ],
            )

        if identifier == "profiles":
            children = [
                self._folder(
                    f"profile/{entry_profile_id(entry)}",
                    entry_profile_name(entry),
                    _profile_thumbnail(entry, catalog),
                )
                for entry in profiles
            ]
            return self._directory(
                identifier,
                "Screens / profiles",
                children,
                root_thumb,
            )

        if identifier.startswith("profile/") and identifier.count("/") == 1:
            profile_id = identifier.split("/", 1)[1]
            entry = _profile_entry(self.hass, profile_id)
            if entry is None:
                raise BrowseError("Unknown Nature Frame screen profile")
            selected = _selected_for_entry(entry, catalog)
            thumb = _profile_thumbnail(entry, catalog)
            title = entry_profile_name(entry)
            return self._directory(
                identifier,
                title,
                [
                    self._folder(
                        f"profile/{profile_id}/portrait",
                        f"Portrait · {len(selected)} active",
                        thumb,
                    ),
                    self._folder(
                        f"profile/{profile_id}/landscape",
                        f"Landscape · {len(selected)} active",
                        thumb,
                    ),
                ],
                thumb,
            )

        parts = identifier.split("/")
        if len(parts) == 3 and parts[0] == "profile":
            _, profile_id, orientation = parts
            if orientation not in {"portrait", "landscape"}:
                raise BrowseError("Unknown orientation")
            entry = _profile_entry(self.hass, profile_id)
            if entry is None:
                raise BrowseError("Unknown Nature Frame screen profile")
            selected = _selected_for_entry(entry, catalog)
            thumb = _profile_thumbnail(entry, catalog)
            title = entry_profile_name(entry)
            return self._directory(
                identifier,
                f"{title} · {orientation.title()} · {len(selected)} active",
                self._active_image_children(catalog, selected, orientation),
                thumb,
            )

        # Backwards compatibility for tablets already pointed at active/*.
        # It resolves to the first (normally migrated Default) profile.
        if identifier in {"active/portrait", "active/landscape"}:
            if first_profile is None:
                raise BrowseError("No Nature Frame screen profiles configured")
            orientation = identifier.split("/", 1)[1]
            selected = _selected_for_entry(first_profile, catalog)
            thumb = _profile_thumbnail(first_profile, catalog)
            return self._directory(
                identifier,
                f"{entry_profile_name(first_profile)} · {orientation.title()} · {len(selected)} active",
                self._active_image_children(catalog, selected, orientation),
                thumb,
            )

        if identifier in {"galleries", "private"}:
            private_only = identifier == "private"
            children = []
            for key in catalog.gallery_keys():
                gallery = catalog.gallery(key)
                if not gallery or (private_only and not gallery.is_private):
                    continue
                children.append(
                    self._folder(
                        f"gallery/{key}",
                        gallery.title,
                        gallery.thumbnail,
                    )
                )
            return self._directory(
                identifier,
                "Private collections" if private_only else "All collections",
                children,
            )

        if identifier.startswith("gallery/") and identifier.count("/") == 1:
            key = identifier.split("/", 1)[1]
            gallery = catalog.gallery(key)
            if not gallery:
                raise BrowseError("Unknown Nature Frame collection")
            portrait_thumb = (
                gallery.portrait[0].thumbnail if gallery.portrait else gallery.thumbnail
            )
            landscape_thumb = (
                gallery.landscape[0].thumbnail
                if gallery.landscape
                else gallery.thumbnail
            )
            return self._directory(
                identifier,
                gallery.title,
                [
                    self._folder(
                        f"gallery/{key}/portrait", "Portrait", portrait_thumb
                    ),
                    self._folder(
                        f"gallery/{key}/landscape", "Landscape", landscape_thumb
                    ),
                ],
                gallery.thumbnail,
            )

        if len(parts) == 3 and parts[0] == "gallery":
            _, key, orientation = parts
            if orientation not in {"portrait", "landscape"}:
                raise BrowseError("Unknown orientation")
            gallery = catalog.gallery(key)
            if not gallery:
                raise BrowseError("Unknown Nature Frame collection")
            return self._directory(
                identifier,
                f"{gallery.title} · {orientation.title()}",
                self._image_children(catalog, key, orientation),
                gallery.thumbnail,
            )

        raise BrowseError("Unknown Nature Frame item")

    def _folder(
        self, identifier: str, title: str, thumbnail: str | None = None
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
            thumbnail=thumbnail,
        )

    def _directory(
        self,
        identifier: str,
        title: str,
        children: list[BrowseMediaSource],
        thumbnail: str | None = None,
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
            thumbnail=thumbnail,
        )

    def _image_item(
        self,
        gallery_key: str,
        orientation: str,
        image: NatureImage,
        title: str,
        slot: int | None = None,
    ) -> BrowseMediaSource:
        identifier = f"item/{gallery_key}/{orientation}/{image.key}"
        if slot is not None:
            identifier += f"/{slot}"
        return BrowseMediaSource(
            domain=DOMAIN,
            identifier=identifier,
            media_class=MediaClass.IMAGE,
            media_content_type=image.mime_type,
            title=title,
            can_play=True,
            can_expand=False,
            thumbnail=image.thumbnail or image.url,
        )

    def _image_children(
        self,
        catalog: NatureFrameCatalog,
        gallery_key: str,
        orientation: str,
        *,
        prefix_title: bool = False,
    ) -> list[BrowseMediaSource]:
        gallery = catalog.gallery(gallery_key)
        title_prefix = f"{gallery.title} · " if prefix_title and gallery else ""
        return [
            self._image_item(
                gallery_key,
                orientation,
                image,
                f"{title_prefix}{image.title}",
            )
            for image in catalog.images(gallery_key, orientation)
        ]

    def _balanced_images(
        self,
        images: tuple[NatureImage, ...],
        target: int,
    ) -> list[NatureImage]:
        if not images:
            return []
        if len(images) == target:
            return list(images)
        if len(images) > target:
            return [
                images[min(len(images) - 1, (index * len(images)) // target)]
                for index in range(target)
            ]
        return [images[index % len(images)] for index in range(target)]

    def _active_image_children(
        self,
        catalog: NatureFrameCatalog,
        gallery_keys: list[str],
        orientation: str,
    ) -> list[BrowseMediaSource]:
        available = [
            (key, catalog.gallery(key), catalog.images(key, orientation))
            for key in gallery_keys
            if catalog.gallery(key) is not None
        ]
        available = [
            (key, gallery, images)
            for key, gallery, images in available
            if gallery is not None and images
        ]
        if not available:
            return []

        if len(available) == 1:
            key, _, _ = available[0]
            return self._image_children(
                catalog,
                key,
                orientation,
                prefix_title=False,
            )

        children: list[BrowseMediaSource] = []
        for key, gallery, images in available:
            balanced = self._balanced_images(images, BALANCED_ITEMS_PER_COLLECTION)
            for slot, image in enumerate(balanced):
                children.append(
                    self._image_item(
                        key,
                        orientation,
                        image,
                        f"{gallery.title} · {image.title}",
                        slot,
                    )
                )
        return children
