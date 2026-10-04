from __future__ import annotations

import asyncio
import html
import re
import time
from dataclasses import dataclass
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

INKY_REPO = "veteranbv/inky-bird-frame"
INKY_BRANCH = "main"
REFRESH_SECONDS = 6 * 60 * 60
INKY_PATH_RE = re.compile(
    r"^catalog/species/(?P<species>[^/]+)/(?P<variant>portrait|display)\\.png$"
)
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
COMMONS_THUMB_WIDTH = 1200

# Curated Wikimedia Commons categories. Commons supplies the licence metadata
# and thumbnail URLs; Nature Frame never republishes the files itself.
COMMONS_GALLERIES: dict[str, tuple[str, str]] = {
    "mammal-illustrations": (
        "Mammal illustrations · Joseph Smit",
        "Mammal illustrations by Joseph Smit",
    ),
    "mammal-photos": (
        "Mammals · Featured photography",
        "Featured pictures of mammals by Charlesjsharp",
    ),
    "night-sky": (
        "Night sky · Featured astronomy",
        "Featured pictures of astronomy",
    ),
    "aurora": (
        "Aurora · Featured pictures",
        "Featured pictures of aurora",
    ),
    "galaxies": (
        "Galaxies · Featured pictures",
        "Featured pictures of galaxies",
    ),
}


@dataclass(frozen=True)
class NatureImage:
    key: str
    title: str
    orientation: str
    url: str
    thumbnail: str | None = None
    mime_type: str = "image/jpeg"
    source: str | None = None
    license: str | None = None


@dataclass(frozen=True)
class NatureGallery:
    key: str
    title: str
    source: str
    portrait: tuple[NatureImage, ...]
    landscape: tuple[NatureImage, ...]

    @property
    def thumbnail(self) -> str | None:
        images = self.portrait or self.landscape
        return images[0].thumbnail or images[0].url if images else None


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

            galleries: dict[str, NatureGallery] = {}
            # A provider failure must not take down the whole Media Source.
            try:
                galleries["birds"] = await self._async_load_inky()
            except Exception:
                pass

            results = await asyncio.gather(
                *[
                    self._async_load_commons(key, title, category)
                    for key, (title, category) in COMMONS_GALLERIES.items()
                ],
                return_exceptions=True,
            )
            for result in results:
                if isinstance(result, NatureGallery):
                    galleries[result.key] = result

            if not galleries:
                raise RuntimeError("Nature Frame could not load any galleries")

            self.galleries = galleries
            self._last_refresh = time.monotonic()

    async def _async_get_json(
        self, url: str, *, params: dict[str, str] | None = None
    ) -> Any:
        session = async_get_clientsession(self.hass)
        headers = {
            "Accept": "application/json",
            "User-Agent": "HomeAssistant-NatureFrame/0.4.0",
        }
        async with session.get(url, params=params, headers=headers, timeout=30) as response:
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
            match = INKY_PATH_RE.match(path)
            if not match:
                continue
            species = match.group("species")
            title = (
                species.split("-", 1)[1].replace("-", " ").title()
                if "-" in species
                else species
            )
            orientation = (
                "portrait" if match.group("variant") == "portrait" else "landscape"
            )
            url = f"https://raw.githubusercontent.com/{INKY_REPO}/{commit_sha}/{path}"
            image = NatureImage(
                key=species,
                title=title,
                orientation=orientation,
                url=url,
                thumbnail=url,
                mime_type="image/png",
                source=f"https://github.com/{INKY_REPO}",
                license="See upstream repository",
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

    async def _async_load_commons(
        self, key: str, title: str, category: str
    ) -> NatureGallery:
        portrait: list[NatureImage] = []
        landscape: list[NatureImage] = []
        continuation: str | None = None

        # Cap each curated collection to 200 direct files. That keeps the
        # Media Browser and the kiosk playlist responsive while still giving
        # plenty of variety.
        while len(portrait) + len(landscape) < 200:
            params = {
                "action": "query",
                "format": "json",
                "formatversion": "2",
                "generator": "categorymembers",
                "gcmtitle": f"Category:{category}",
                "gcmtype": "file",
                "gcmlimit": "100",
                "prop": "imageinfo",
                "iiprop": "url|mime|size|extmetadata",
                "iiurlwidth": str(COMMONS_THUMB_WIDTH),
                "origin": "*",
            }
            if continuation:
                params["gcmcontinue"] = continuation
            data = await self._async_get_json(COMMONS_API, params=params)
            pages = data.get("query", {}).get("pages", [])

            for page in pages:
                info_list = page.get("imageinfo") or []
                if not info_list:
                    continue
                info = info_list[0]
                mime = str(info.get("mime", ""))
                if mime not in {"image/jpeg", "image/png", "image/webp"}:
                    continue
                width = int(info.get("width") or 0)
                height = int(info.get("height") or 0)
                if not width or not height:
                    continue

                file_title = str(page.get("title", ""))
                clean_title = re.sub(r"^File:", "", file_title, flags=re.I)
                clean_title = re.sub(r"\\.(?:jpe?g|png|webp)$", "", clean_title, flags=re.I)
                clean_title = clean_title.replace("_", " ").strip()
                ext = info.get("extmetadata") or {}
                license_name = html.unescape(
                    str((ext.get("LicenseShortName") or {}).get("value", ""))
                )
                description_url = str(info.get("descriptionurl") or "")
                url = str(info.get("thumburl") or info.get("url") or "")
                if not url:
                    continue
                thumb = str(info.get("thumburl") or url)
                image = NatureImage(
                    key=str(page.get("pageid")),
                    title=clean_title,
                    orientation="portrait" if height >= width else "landscape",
                    url=url,
                    thumbnail=thumb,
                    mime_type=mime,
                    source=description_url,
                    license=license_name or None,
                )
                (portrait if height >= width else landscape).append(image)
                if len(portrait) + len(landscape) >= 200:
                    break

            continuation = data.get("continue", {}).get("gcmcontinue")
            if not continuation:
                break

        portrait.sort(key=lambda item: item.title.casefold())
        landscape.sort(key=lambda item: item.title.casefold())
        if not portrait and not landscape:
            raise RuntimeError(f"No usable Commons images found for {category}")

        return NatureGallery(
            key=key,
            title=title,
            source=f"https://commons.wikimedia.org/wiki/Category:{category.replace(' ', '_')}",
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
