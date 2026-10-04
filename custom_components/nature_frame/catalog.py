from __future__ import annotations

import asyncio
import hashlib
import html
import mimetypes
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

INKY_REPO = "veteranbv/inky-bird-frame"
INKY_BRANCH = "main"
REFRESH_SECONDS = 6 * 60 * 60
INKY_PATH_RE = re.compile(
    r"^catalog/species/(?P<species>[^/]+)/(?P<variant>portrait|display)\.png$"
)
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
COMMONS_THUMB_WIDTH = 1200
PRIVATE_MEDIA_ROOT = Path("/media/nature-frame/private")
LOCAL_MEDIA_ROOT = Path("/media")
PRIVATE_MEDIA_URL_ROOT = "/media/local"
SUPPORTED_PRIVATE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

SEEDED_PRIVATE_COLLECTIONS: dict[str, tuple[str, str]] = {
    "zoo private": ("private-zoo", "Zoo · Private"),
}


@dataclass(frozen=True)
class CommonsGallerySpec:
    title: str
    categories: tuple[str, ...]
    max_items: int = 200


# Public collections are intentionally based on named works/series instead of
# broad topical scraping. This keeps each collection visually coherent.
COMMONS_GALLERIES: dict[str, CommonsGallerySpec] = {
    "zoo-swainson": CommonsGallerySpec(
        "Zoo · Public · Swainson",
        (
            "Zoological Illustrations Volume I",
            "Zoological Illustrations Volume II",
            "Zoological Illustrations Volume III",
        ),
        270,
    ),
    "kitchen-pomological": CommonsGallerySpec(
        "Kitchen · USDA Pomological Watercolors",
        ("USDA Pomological Watercolors",),
        240,
    ),
    "kitchen-kohler": CommonsGallerySpec(
        "Kitchen · Köhler Botanical Plates",
        ("Köhlers Medizinal-Pflanzen",),
        240,
    ),
    "kitchen-beeton": CommonsGallerySpec(
        "Kitchen · Mrs Beeton Plates",
        ("Mrs. Beeton's Book of Household Management (images)",),
        200,
    ),
    "mammal-illustrations": CommonsGallerySpec(
        "Mammal illustrations · Joseph Smit",
        ("Mammal illustrations by Joseph Smit",),
        180,
    ),
    "mammal-photos": CommonsGallerySpec(
        "Mammals · Featured photography",
        ("Featured pictures of mammals by Charlesjsharp",),
        180,
    ),
    "night-sky": CommonsGallerySpec(
        "Night sky · Featured astronomy",
        ("Featured pictures of astronomy",),
        180,
    ),
    "aurora": CommonsGallerySpec(
        "Aurora · Featured pictures",
        ("Featured pictures of aurora",),
        160,
    ),
    "galaxies": CommonsGallerySpec(
        "Galaxies · Featured pictures",
        ("Featured pictures of galaxies",),
        160,
    ),
}

VIRTUAL_GALLERIES: dict[str, tuple[str, tuple[str, ...]]] = {
    "kitchen-mixed": (
        "Kitchen · Mixed",
        ("kitchen-pomological", "kitchen-kohler", "kitchen-beeton"),
    ),
    "art-misc": (
        "Art · Misc · Curated",
        (
            "mammal-illustrations",
            "zoo-swainson",
            "night-sky",
            "aurora",
            "galaxies",
        ),
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
    is_private: bool = False
    is_virtual: bool = False

    @property
    def thumbnail(self) -> str | None:
        images = self.portrait or self.landscape
        return images[0].thumbnail or images[0].url if images else None


class NatureFrameCatalog:
    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.galleries: dict[str, NatureGallery] = {}
        self._remote_galleries: dict[str, NatureGallery] = {}
        self._last_refresh = 0.0
        self._lock = asyncio.Lock()

    async def async_refresh(self, force: bool = False) -> None:
        async with self._lock:
            now = time.monotonic()
            refresh_remote = (
                force
                or not self._remote_galleries
                or now - self._last_refresh >= REFRESH_SECONDS
            )

            if refresh_remote:
                remote: dict[str, NatureGallery] = {}

                try:
                    remote["birds"] = await self._async_load_inky()
                except Exception:
                    pass

                results = await asyncio.gather(
                    *[
                        self._async_load_commons(key, spec)
                        for key, spec in COMMONS_GALLERIES.items()
                    ],
                    return_exceptions=True,
                )
                for result in results:
                    if isinstance(result, NatureGallery):
                        remote[result.key] = result

                for key, (title, members) in VIRTUAL_GALLERIES.items():
                    gallery = self._build_virtual_gallery(key, title, members, remote)
                    if gallery:
                        remote[key] = gallery

                if remote:
                    self._remote_galleries = remote
                    self._last_refresh = time.monotonic()
                elif not self._remote_galleries:
                    raise RuntimeError("Nature Frame could not load any remote galleries")

            private = await self.hass.async_add_executor_job(
                self._load_private_galleries
            )
            self.galleries = {**self._remote_galleries, **private}

            if not self.galleries:
                raise RuntimeError("Nature Frame could not load any galleries")

    async def _async_get_json(
        self, url: str, *, params: dict[str, str] | None = None
    ) -> Any:
        session = async_get_clientsession(self.hass)
        headers = {
            "Accept": "application/json",
            "User-Agent": "HomeAssistant-NatureFrame/0.7.1",
        }
        async with session.get(
            url, params=params, headers=headers, timeout=30
        ) as response:
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

        portrait.sort(key=lambda item: item.title.casefold())
        landscape.sort(key=lambda item: item.title.casefold())
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
        self,
        key: str,
        spec: CommonsGallerySpec,
    ) -> NatureGallery:
        portrait: list[NatureImage] = []
        landscape: list[NatureImage] = []
        seen_pageids: set[str] = set()
        per_category = max(1, spec.max_items // len(spec.categories))

        for category in spec.categories:
            continuation: str | None = None
            category_count = 0

            while (
                category_count < per_category
                and len(portrait) + len(landscape) < spec.max_items
            ):
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
                    pageid = str(page.get("pageid") or "")
                    if not pageid or pageid in seen_pageids:
                        continue

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
                    clean_title = re.sub(
                        r"\.(?:jpe?g|png|webp)$", "", clean_title, flags=re.I
                    )
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
                        key=pageid,
                        title=clean_title,
                        orientation="portrait" if height >= width else "landscape",
                        url=url,
                        thumbnail=thumb,
                        mime_type=mime,
                        source=description_url,
                        license=license_name or None,
                    )
                    seen_pageids.add(pageid)
                    (portrait if height >= width else landscape).append(image)
                    category_count += 1

                    if (
                        category_count >= per_category
                        or len(portrait) + len(landscape) >= spec.max_items
                    ):
                        break

                continuation = data.get("continue", {}).get("gcmcontinue")
                if not continuation:
                    break

        portrait.sort(key=lambda item: item.title.casefold())
        landscape.sort(key=lambda item: item.title.casefold())
        if not portrait and not landscape:
            raise RuntimeError(
                f"No usable Commons images found for {', '.join(spec.categories)}"
            )

        source_categories = "; ".join(
            f"https://commons.wikimedia.org/wiki/Category:{category.replace(' ', '_')}"
            for category in spec.categories
        )
        return NatureGallery(
            key=key,
            title=spec.title,
            source=source_categories,
            portrait=tuple(portrait),
            landscape=tuple(landscape),
        )

    def _build_virtual_gallery(
        self,
        key: str,
        title: str,
        member_keys: tuple[str, ...],
        galleries: dict[str, NatureGallery],
    ) -> NatureGallery | None:
        portrait: list[NatureImage] = []
        landscape: list[NatureImage] = []
        sources: list[str] = []

        for member_key in member_keys:
            gallery = galleries.get(member_key)
            if not gallery:
                continue
            portrait.extend(gallery.portrait)
            landscape.extend(gallery.landscape)
            sources.append(gallery.title)

        if not portrait and not landscape:
            return None

        return NatureGallery(
            key=key,
            title=title,
            source="Curated mix: " + ", ".join(sources),
            portrait=tuple(portrait),
            landscape=tuple(landscape),
            is_virtual=True,
        )

    def _load_private_galleries(self) -> dict[str, NatureGallery]:
        PRIVATE_MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

        # Seed the household Zoo collection so it exists immediately after the
        # integration is installed, even before the first private image is added.
        zoo_folder = PRIVATE_MEDIA_ROOT / "Zoo Private"
        zoo_folder.mkdir(parents=True, exist_ok=True)

        galleries: dict[str, NatureGallery] = {}

        for folder in sorted(
            (path for path in PRIVATE_MEDIA_ROOT.iterdir() if path.is_dir()),
            key=lambda path: path.name.casefold(),
        ):
            images: list[NatureImage] = []
            for path in sorted(
                (
                    item
                    for item in folder.rglob("*")
                    if item.is_file()
                    and item.suffix.casefold() in SUPPORTED_PRIVATE_EXTENSIONS
                ),
                key=lambda item: item.as_posix().casefold(),
            ):
                try:
                    relative = path.relative_to(LOCAL_MEDIA_ROOT)
                except ValueError:
                    continue

                relative_url = quote(relative.as_posix(), safe="/")
                url = f"{PRIVATE_MEDIA_URL_ROOT}/{relative_url}"
                mime_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"
                image_key = hashlib.sha1(
                    relative.as_posix().encode("utf-8")
                ).hexdigest()[:16]
                title = re.sub(r"[_-]+", " ", path.stem).strip() or path.name
                images.append(
                    NatureImage(
                        key=image_key,
                        title=title,
                        orientation="any",
                        url=url,
                        thumbnail=url,
                        mime_type=mime_type,
                        source="Local Home Assistant media",
                        license="Private/local",
                    )
                )

            seeded = SEEDED_PRIVATE_COLLECTIONS.get(folder.name.casefold())
            if seeded:
                key, title = seeded
            else:
                if not images:
                    continue
                slug = re.sub(
                    r"[^a-z0-9]+", "-", folder.name.casefold()
                ).strip("-")
                slug = slug or "collection"
                key = f"private-{slug}"
                title = f"Private · {folder.name}"
                if key in galleries:
                    suffix = hashlib.sha1(
                        folder.name.encode("utf-8")
                    ).hexdigest()[:6]
                    key = f"{key}-{suffix}"

            # Private images are exposed in both orientation folders. That
            # guarantees posters remain available regardless of tablet rotation.
            image_tuple = tuple(images)
            galleries[key] = NatureGallery(
                key=key,
                title=title,
                source=str(folder),
                portrait=image_tuple,
                landscape=image_tuple,
                is_private=True,
            )

        return galleries

    def gallery_keys(self) -> list[str]:
        group_order = {
            "birds": 0,
            "zoo-swainson": 1,
            "private-zoo": 2,
            "kitchen-pomological": 3,
            "kitchen-kohler": 4,
            "kitchen-beeton": 5,
            "kitchen-mixed": 6,
            "art-misc": 7,
        }
        return sorted(
            self.galleries,
            key=lambda key: (
                group_order.get(key, 20 if not self.galleries[key].is_private else 30),
                self.galleries[key].title.casefold(),
            ),
        )

    def gallery(self, key: str) -> NatureGallery | None:
        return self.galleries.get(key)

    def images(self, key: str, orientation: str) -> tuple[NatureImage, ...]:
        gallery = self.gallery(key)
        if not gallery:
            return ()
        return gallery.portrait if orientation == "portrait" else gallery.landscape
