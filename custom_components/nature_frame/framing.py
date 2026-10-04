from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import Path
from urllib.parse import unquote

from PIL import Image, ImageChops, ImageOps, ImageStat

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .catalog import NatureImage
from .profile import entry_screen_ratio

CACHE_ROOT = Path("/media/nature-frame/framed")
MEDIA_ROOT = Path("/media")
MEDIA_URL_ROOT = "/media/local"
MAX_LONG_EDGE = 1600


def _parse_ratio(value: str, orientation: str) -> float:
    try:
        left, right = value.split(":", 1)
        landscape = float(left) / float(right)
        if landscape <= 0:
            raise ValueError
    except (ValueError, ZeroDivisionError):
        landscape = 16 / 9
    return 1 / landscape if orientation == "portrait" else landscape


def _target_size(ratio: float) -> tuple[int, int]:
    if ratio >= 1:
        width = MAX_LONG_EDGE
        height = max(1, round(width / ratio))
    else:
        height = MAX_LONG_EDGE
        width = max(1, round(height * ratio))
    return width, height


def _median_color(image: Image.Image, box: tuple[int, int, int, int]) -> tuple[int, int, int]:
    crop = image.crop(box)
    median = ImageStat.Stat(crop).median
    return tuple(int(max(0, min(255, value))) for value in median[:3])


def _edge_colors(image: Image.Image) -> dict[str, tuple[int, int, int]]:
    width, height = image.size
    band_x = max(1, round(width * 0.08))
    band_y = max(1, round(height * 0.08))
    inset_x = max(0, round(width * 0.08))
    inset_y = max(0, round(height * 0.08))

    return {
        "top": _median_color(
            image,
            (inset_x, 0, max(inset_x + 1, width - inset_x), band_y),
        ),
        "bottom": _median_color(
            image,
            (
                inset_x,
                max(0, height - band_y),
                max(inset_x + 1, width - inset_x),
                height,
            ),
        ),
        "left": _median_color(
            image,
            (0, inset_y, band_x, max(inset_y + 1, height - inset_y)),
        ),
        "right": _median_color(
            image,
            (
                max(0, width - band_x),
                inset_y,
                width,
                max(inset_y + 1, height - inset_y),
            ),
        ),
        "center": _median_color(image, (0, 0, width, height)),
    }


def _corner_background_color(image: Image.Image) -> tuple[int, int, int] | None:
    """Return a likely outer-canvas color when all four corners agree."""
    width, height = image.size
    sample_w = max(1, round(width * 0.03))
    sample_h = max(1, round(height * 0.03))
    boxes = (
        (0, 0, sample_w, sample_h),
        (max(0, width - sample_w), 0, width, sample_h),
        (0, max(0, height - sample_h), sample_w, height),
        (
            max(0, width - sample_w),
            max(0, height - sample_h),
            width,
            height,
        ),
    )
    colors = [_median_color(image, box) for box in boxes]

    # Only treat the outside as a removable canvas when the corners are
    # essentially the same color. This avoids cropping normal photographs.
    for channel in range(3):
        values = [color[channel] for color in colors]
        if max(values) - min(values) > 18:
            return None

    return tuple(
        round(sum(color[channel] for color in colors) / len(colors))
        for channel in range(3)
    )


def _trim_uniform_outer_canvas(image: Image.Image) -> Image.Image:
    """Trim large, nearly uniform outer margins while preserving the artwork."""
    if image.width < 16 or image.height < 16:
        return image

    background_color = _corner_background_color(image)
    if background_color is None:
        return image

    background = Image.new("RGB", image.size, background_color)
    difference = ImageChops.difference(image, background)
    red, green, blue = difference.split()
    max_difference = ImageChops.lighter(red, ImageChops.lighter(green, blue))
    foreground = max_difference.point(lambda value: 255 if value >= 20 else 0)
    bbox = foreground.getbbox()
    if not bbox:
        return image

    left, top, right, bottom = bbox
    original_area = image.width * image.height
    cropped_area = max(1, right - left) * max(1, bottom - top)

    # Do not react to tiny edge/color variations. This is intended for files
    # where a poster sits inside a significantly larger white/transparent
    # export canvas (common with background-removal/upscaling tools).
    if cropped_area > original_area * 0.92:
        return image

    pad_x = max(2, round((right - left) * 0.01))
    pad_y = max(2, round((bottom - top) * 0.01))
    left = max(0, left - pad_x)
    top = max(0, top - pad_y)
    right = min(image.width, right + pad_x)
    bottom = min(image.height, bottom + pad_y)

    return image.crop((left, top, right, bottom))


def _decode_rgb(data: bytes) -> Image.Image:
    image = Image.open(BytesIO(data))
    image = ImageOps.exif_transpose(image)

    if image.mode in {"RGBA", "LA"} or (
        image.mode == "P" and "transparency" in image.info
    ):
        rgba = image.convert("RGBA")

        # Background-removal tools commonly keep the original canvas size and
        # merely make the surrounding area transparent. Remove that first.
        alpha = rgba.getchannel("A")
        visible = alpha.point(lambda value: 255 if value >= 16 else 0)
        bbox = visible.getbbox()
        if bbox:
            rgba = rgba.crop(bbox)

        base = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        base.alpha_composite(rgba)
        rgb = base.convert("RGB")
        return _trim_uniform_outer_canvas(rgb)

    # Upscalers/background tools also sometimes bake the empty canvas in as
    # opaque white (or another uniform color). Trim that outer canvas too.
    return _trim_uniform_outer_canvas(image.convert("RGB"))


def _render_solid_frame(
    data: bytes,
    target_ratio: float,
    destination: Path,
) -> None:
    image = _decode_rgb(data)
    target_w, target_h = _target_size(target_ratio)

    scale = min(target_w / image.width, target_h / image.height)
    resized_w = max(1, round(image.width * scale))
    resized_h = max(1, round(image.height * scale))
    resized = image.resize((resized_w, resized_h), Image.Resampling.LANCZOS)

    colors = _edge_colors(image)
    canvas = Image.new("RGB", (target_w, target_h), colors["center"])
    left = (target_w - resized_w) // 2
    top = (target_h - resized_h) // 2

    if top > 0:
        top_bar = Image.new("RGB", (target_w, top), colors["top"])
        bottom_h = target_h - (top + resized_h)
        canvas.paste(top_bar, (0, 0))
        if bottom_h > 0:
            bottom_bar = Image.new(
                "RGB", (target_w, bottom_h), colors["bottom"]
            )
            canvas.paste(bottom_bar, (0, top + resized_h))
    elif left > 0:
        left_bar = Image.new("RGB", (left, target_h), colors["left"])
        right_w = target_w - (left + resized_w)
        canvas.paste(left_bar, (0, 0))
        if right_w > 0:
            right_bar = Image.new(
                "RGB", (right_w, target_h), colors["right"]
            )
            canvas.paste(right_bar, (left + resized_w, 0))

    canvas.paste(resized, (left, top))
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, format="JPEG", quality=92, optimize=True)


async def _async_image_bytes(hass: HomeAssistant, image: NatureImage) -> bytes:
    url = image.url
    if url.startswith(f"{MEDIA_URL_ROOT}/"):
        relative = unquote(url[len(MEDIA_URL_ROOT) + 1 :])
        path = (MEDIA_ROOT / relative).resolve()
        if MEDIA_ROOT.resolve() not in path.parents and path != MEDIA_ROOT.resolve():
            raise ValueError("Invalid local media path")
        return await hass.async_add_executor_job(path.read_bytes)

    session = async_get_clientsession(hass)
    headers = {"User-Agent": "HomeAssistant-NatureFrame/0.7.6"}
    async with session.get(url, headers=headers, timeout=30) as response:
        response.raise_for_status()
        return await response.read()


async def async_solid_framed_url(
    hass: HomeAssistant,
    entry: ConfigEntry,
    image: NatureImage,
    orientation: str,
) -> str:
    ratio_label = entry_screen_ratio(entry)
    target_ratio = _parse_ratio(ratio_label, orientation)
    cache_key = hashlib.sha1(
        f"{image.url}|{ratio_label}|{orientation}|solid-v3".encode("utf-8")
    ).hexdigest()
    destination = CACHE_ROOT / f"{cache_key}.jpg"

    if not destination.is_file():
        data = await _async_image_bytes(hass, image)
        await hass.async_add_executor_job(
            _render_solid_frame,
            data,
            target_ratio,
            destination,
        )

    relative = destination.relative_to(MEDIA_ROOT).as_posix()
    return f"{MEDIA_URL_ROOT}/{relative}"
