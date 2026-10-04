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

from PIL import Image, ImageOps

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

INKY_REPO = "veteranbv/inky-bird-frame"
INKY_BRANCH = "main"
REFRESH_SECONDS = 6 * 60 * 60
PRIVATE_REFRESH_SECONDS = 10
INKY_PATH_RE = re.compile(
    r"^catalog/species/(?P<species>[^/]+)/(?P<variant>portrait|display)\.png$"
)
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
COMMONS_THUMB_WIDTH = 1200
PRIVATE_MEDIA_ROOT = Path("/media/nature-frame/private")
PRIVATE_PREVIEW_ROOT = Path("/media/nature-frame/previews/private")
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

# Small built-in fallbacks keep the named public collections available even
# when the Wikimedia API is temporarily unreachable from Home Assistant.
# The normal API catalogue still wins and provides the much larger library.
COMMONS_FALLBACK_FILES: dict[str, tuple[tuple[str, int, int], ...]] = {
    "zoo-swainson": (
        ("Zoological Illustrations Volume I Plate 1.jpg", 1625, 2177),
        ("Zoological Illustrations Volume I Plate 10.jpg", 1617, 2517),
        ("Zoological Illustrations Volume I Plate 11.jpg", 1818, 2928),
        ("Zoological Illustrations Volume I Plate 13.jpg", 1717, 2825),
        ("Zoological Illustrations Volume I Plate 14.jpg", 1769, 2641),
        ("Zoological Illustrations Volume I Plate 15.jpg", 1573, 2768),
        ("Zoological Illustrations Volume I Plate 16.jpg", 1891, 2913),
        ("Zoological Illustrations Volume I Plate 18.jpg", 1553, 2601),
        ("Zoological Illustrations Volume II Series 2 056.jpg", 2017, 2973),
        ("Zoological Illustrations Volume II Series 2 063.jpg", 1733, 3181),
        ("Zoological Illustrations Volume II Series 2 080.jpg", 1800, 3000),
        ("Zoological Illustrations Volume III Plate 120.jpg", 1505, 2585),
        ("Zoological Illustrations Volume III Plate 121.jpg", 1839, 2873),
        ("Zoological Illustrations Volume III Plate 122.jpg", 1733, 2609),
        ("Zoological Illustrations Volume III Plate 123.jpg", 1609, 2669),
        ("Zoological Illustrations Volume III Plate 124.jpg", 1541, 2853),
        ("Zoological Illustrations Volume III Plate 125.jpg", 1847, 2761),
        ("Zoological Illustrations Volume III Plate 126.jpg", 1449, 2577),
        ("Zoological Illustrations Volume III Plate 127.jpg", 1501, 2925),
    ),
    "kitchen-pomological": (
        ("Pomological Watercolor POM00000001.jpg", 2629, 4000),
        ("Pomological Watercolor POM00000002.jpg", 2835, 4000),
        ("Pomological Watercolor POM00000003.jpg", 2814, 4000),
        ("Pomological Watercolor POM00000004.jpg", 3187, 4000),
        ("Pomological Watercolor POM00000005.jpg", 2690, 4000),
        ("Pomological Watercolor POM00000006.jpg", 3217, 4000),
        ("Pomological Watercolor POM00000007.jpg", 2968, 4000),
        ("Pomological Watercolor POM00000008.jpg", 2774, 4000),
        ("Pomological Watercolor POM00000009.jpg", 3246, 4000),
        ("Pomological Watercolor POM00000010.jpg", 2651, 4000),
        ("Pomological Watercolor POM00000011.jpg", 3274, 4000),
        ("Pomological Watercolor POM00000012.jpg", 3170, 4000),
    ),
    "kitchen-kohler": (
        ("Köhler's Medizinal-Pflanzen in naturgetreuen Abbildungen mit kurz erläuterndem Texte (Plate 100) (8231716529).jpg", 1405, 2032),
        ("Köhler's Medizinal-Pflanzen in naturgetreuen Abbildungen mit kurz erläuterndem Texte (Plate 101) (8231717005).jpg", 1402, 1993),
        ("Köhler's Medizinal-Pflanzen in naturgetreuen Abbildungen mit kurz erläuterndem Texte (Plate 102) (8232779960).jpg", 1393, 2014),
        ("Köhler's Medizinal-Pflanzen in naturgetreuen Abbildungen mit kurz erläuterndem Texte (Plate 103) (8232780324).jpg", 1408, 1984),
        ("Köhler's Medizinal-Pflanzen in naturgetreuen Abbildungen mit kurz erläuterndem Texte (Plate 104) (8231718261).jpg", 1426, 1990),
        ("Köhler's Medizinal-Pflanzen in naturgetreuen Abbildungen mit kurz erläuterndem Texte (Plate 105) (8231718775).jpg", 1420, 1966),
        ("Köhler's Medizinal-Pflanzen in naturgetreuen Abbildungen mit kurz erläuterndem Texte (Plate 106) (8231719251).jpg", 1375, 1975),
        ("Köhler's Medizinal-Pflanzen in naturgetreuen Abbildungen mit kurz erläuterndem Texte (Plate 107) (8231719867).jpg", 1441, 1948),
    ),
    "kitchen-beeton": (
        ("A Dinner Table from Mrs. Beeton& -39;s Book of Household Management. Digitally enhanced from our own 1923 edition.jpg", 1562, 2500),
        ("A Supper Buffet for Ball or Reception from Mrs. Beeton& -39;s Book of Household Management. Digitally enhanced from our own 1923 edition.jpg", 2500, 1786),
        ("Puddingsbhm.jpg", 449, 762),
        ("Mrs Beeton (p1710).jpg", 2035, 3076),
        ("Mrs Beeton (p1711).jpg", 1993, 3016),
        ("Mrs Beeton (p1712).jpg", 1985, 2997),
        ("Mrs Beeton (p1713).jpg", 1989, 3013),
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
    cover_thumbnail: str | None = None

    @property
    def thumbnail(self) -> str | None:
        if self.cover_thumbnail:
            return self.cover_thumbnail
        images = self.portrait or self.landscape
        return images[0].thumbnail or images[0].url if images else None


class NatureFrameCatalog:
    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.galleries: dict[str, NatureGallery] = {}
        self._remote_galleries: dict[str, NatureGallery] = {}
        self._private_galleries: dict[str, NatureGallery] = {}
        self._last_refresh = 0.0
        self._last_private_refresh = 0.0
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

                commons_items = list(COMMONS_GALLERIES.items())
                results = await asyncio.gather(
                    *[
                        self._async_load_commons(key, spec)
                        for key, spec in commons_items
                    ],
                    return_exceptions=True,
                )
                for (key, spec), result in zip(commons_items, results):
                    if isinstance(result, NatureGallery):
                        remote[result.key] = result
                    else:
                        fallback_gallery = self._fallback_commons_gallery(
                            key,
                            spec,
                        )
                        if fallback_gallery:
                            remote[key] = fallback_gallery

                for key, (title, members) in VIRTUAL_GALLERIES.items():
                    gallery = self._build_virtual_gallery(key, title, members, remote)
                    if gallery:
                        remote[key] = gallery

                if remote:
                    self._remote_galleries = remote
                    self._last_refresh = time.monotonic()
                elif not self._remote_galleries:
                    raise RuntimeError("Nature Frame could not load any remote galleries")

            refresh_private = (
                force
                or not self._private_galleries
                or now - self._last_private_refresh >= PRIVATE_REFRESH_SECONDS
            )
            if refresh_private:
                self._private_galleries = await self.hass.async_add_executor_job(
                    self._load_private_galleries
                )
                self._last_private_refresh = time.monotonic()

            self.galleries = {
                **self._remote_galleries,
                **self._private_galleries,
            }

            if not self.galleries:
                raise RuntimeError("Nature Frame could not load any galleries")

    async def _async_get_json(
        self, url: str, *, params: dict[str, str] | None = None
    ) -> Any:
        session = async_get_clientsession(self.hass)
        headers = {
            "Accept": "application/json",
            "User-Agent": "HomeAssistant-NatureFrame/0.8.1",
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

    def _fallback_commons_gallery(
        self,
        key: str,
        spec: CommonsGallerySpec,
    ) -> NatureGallery | None:
        files = COMMONS_FALLBACK_FILES.get(key)
        if not files:
            return None

        portrait: list[NatureImage] = []
        landscape: list[NatureImage] = []
        for index, (filename, width, height) in enumerate(files):
            encoded = quote(filename, safe="")
            url = (
                "https://commons.wikimedia.org/wiki/"
                f"Special:Redirect/file/{encoded}?width={COMMONS_THUMB_WIDTH}"
            )
            image = NatureImage(
                key=f"fallback-{key}-{index}",
                title=re.sub(r"\.(?:jpe?g|png|webp)$", "", filename, flags=re.I),
                orientation="portrait" if height >= width else "landscape",
                url=url,
                thumbnail=url,
                mime_type="image/jpeg",
                source=(
                    "https://commons.wikimedia.org/wiki/File:"
                    + quote(filename.replace(" ", "_"), safe="():,_-.")
                ),
                license="Public domain / see Wikimedia Commons file page",
            )
            (portrait if height >= width else landscape).append(image)

        source_categories = "; ".join(
            "https://commons.wikimedia.org/wiki/Category:"
            + quote(category.replace(" ", "_"), safe="():,_-.")
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

        # Virtual collections reuse member images. Give them a deliberately
        # different cover so their Lovelace tile is not visually identical to
        # the first source collection.
        cover_thumbnail = None
        for member_key in reversed(member_keys):
            member = galleries.get(member_key)
            if not member:
                continue
            candidates = member.portrait or member.landscape
            if not candidates:
                continue
            cover = candidates[min(len(candidates) - 1, max(1, len(candidates) // 2))]
            cover_thumbnail = cover.thumbnail or cover.url
            break

        return NatureGallery(
            key=key,
            title=title,
            source="Curated mix: " + ", ".join(sources),
            portrait=tuple(portrait),
            landscape=tuple(landscape),
            is_virtual=True,
            cover_thumbnail=cover_thumbnail,
        )

    def _private_cover_thumbnail(
        self,
        source_path: Path,
        gallery_key: str,
    ) -> str | None:
        """Create a stable browser-safe JPEG cover for a private collection."""
        try:
            relative = source_path.relative_to(LOCAL_MEDIA_ROOT)
            stat = source_path.stat()
            fingerprint = hashlib.sha1(
                (
                    f"{relative.as_posix()}|{stat.st_size}|"
                    f"{stat.st_mtime_ns}"
                ).encode("utf-8")
            ).hexdigest()[:16]

            PRIVATE_PREVIEW_ROOT.mkdir(parents=True, exist_ok=True)
            destination = (
                PRIVATE_PREVIEW_ROOT
                / f"{gallery_key}-{fingerprint}.jpg"
            )

            if not destination.is_file():
                with Image.open(source_path) as opened:
                    image = ImageOps.exif_transpose(opened)

                    if image.mode in {"RGBA", "LA"} or (
                        image.mode == "P"
                        and "transparency" in image.info
                    ):
                        rgba = image.convert("RGBA")
                        base = Image.new(
                            "RGBA",
                            rgba.size,
                            (255, 255, 255, 255),
                        )
                        base.alpha_composite(rgba)
                        image = base.convert("RGB")
                    else:
                        image = image.convert("RGB")

                    image.thumbnail(
                        (900, 900),
                        Image.Resampling.LANCZOS,
                    )
                    image.save(
                        destination,
                        format="JPEG",
                        quality=88,
                        optimize=True,
                    )

                # Keep only the current cover for this collection.
                for old in PRIVATE_PREVIEW_ROOT.glob(
                    f"{gallery_key}-*.jpg"
                ):
                    if old != destination:
                        try:
                            old.unlink()
                        except OSError:
                            pass

            relative_preview = destination.relative_to(
                LOCAL_MEDIA_ROOT
            ).as_posix()
            return (
                f"{PRIVATE_MEDIA_URL_ROOT}/"
                f"{quote(relative_preview, safe='/')}"
            )
        except Exception:
            # A failed preview must never hide/break the private collection.
            return None

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
            first_source_path: Path | None = None
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
                if first_source_path is None:
                    first_source_path = path

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

            # Use a generated, simple local JPEG as the collection cover.
            # Home Assistant frontend cards can be less reliable when an
            # entity_picture points directly at a private source filename with
            # spaces, Unicode, transparency or a recently replaced file.
            cover_thumbnail = (
                self._private_cover_thumbnail(first_source_path, key)
                if first_source_path is not None
                else None
            )

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
                cover_thumbnail=cover_thumbnail,
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
