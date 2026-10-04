from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

INKY_REPO = "veteranbv/inky-bird-frame"
INKY_BRANCH = "main"
REFRESH_SECONDS = 6 * 60 * 60
PATH_RE = re.compile(
    r"^catalog/species/(?P<species>[^/]+)/(?P<variant>portrait|display)\.png$"
)


@dataclass(frozen=True)
class NatureImage:
    key: str
    title: str
    orientation: str
    url: str
    mime_type: str = "image/png"


@dataclass(frozen=True)
class NatureGallery:
    key: str
    title: str
    source: str
    portrait: tuple[NatureImage, ...]
    landscape: tuple[NatureImage, ...]


class NatureFrameCatalog:
    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.galleries: dict[str, NatureGallery] = {}
        self._last_refresh = 0.0
        self._lock = asyncio.Lock()

    async def async_refresh(self, force: bool = False) -> None:
        now = time.monotonic()
        if not force and self.galleries and now - self._last_refresh < REFRESH_SECONDS:
            return
        async with self._lock:
            now = time.monotonic()
            if not force and self.galleries and now - self._last_refresh < REFRESH_SECONDS:
                return
            self.galleries = {"birds": await self._async_load_inky()}
            self._last_refresh = time.monotonic()

    async def _async_get_json(self, url: str) -> Any:
        session = async_get_clientsession(self.hass)
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "HomeAssistant-NatureFrame/0.3.0",
        }
        async with session.get(url, headers=headers, timeout=30) as response:
            response.raise_for_status()
            return await response.json()

    async def _async_load_inky(self) -> NatureGallery:
        branch = await self._async_get_json(
            f"https://api.github.com/repos/{INKY_REPO}/branches/{INKY_BRANCH}"
        )
        commit_sha = str(branch["commit"]["sha"])
        tree_sha = str(branch["commit"]["commit"]["tree"]["sha"])
        tree = await self._async_get_json(
            f"https://api.github.com/repos/{INKY_REPO}/git/trees/{tree_sha}?recursive=1"
        )
        if tree.get("truncated"):
            raise RuntimeError("GitHub returned a truncated Inky Bird Frame tree")

        portrait: list[NatureImage] = []
        landscape: list[NatureImage] = []
        for item in tree.get("tree", []):
            path = str(item.get("path", ""))
            match = PATH_RE.match(path)
            if not match:
                continue
            species = match.group("species")
            title = species.split("-", 1)[1].replace("-", " ").title() if "-" in species else species
            orientation = "portrait" if match.group("variant") == "portrait" else "landscape"
            image = NatureImage(
                key=species,
                title=title,
                orientation=orientation,
                url=f"https://raw.githubusercontent.com/{INKY_REPO}/{commit_sha}/{path}",
            )
            (portrait if orientation == "portrait" else landscape).append(image)

        portrait.sort(key=lambda item: item.title)
        landscape.sort(key=lambda item: item.title)
        if not portrait and not landscape:
            raise RuntimeError("No Inky Bird Frame images were found")

        return NatureGallery(
            key="birds",
            title="Birds · Inky Bird Frame",
            source=f"https://github.com/{INKY_REPO}",
            portrait=tuple(portrait),
            landscape=tuple(landscape),
        )

    def gallery_keys(self) -> list[str]:
        return sorted(self.galleries)

    def gallery(self, key: str) -> NatureGallery | None:
        return self.galleries.get(key)

    def images(self, key: str, orientation: str) -> tuple[NatureImage, ...]:
        gallery = self.gallery(key)
        if not gallery:
            return ()
        return gallery.portrait if orientation == "portrait" else gallery.landscape
