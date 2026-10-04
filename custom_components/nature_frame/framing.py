from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import Path
from urllib.parse import unquote

from PIL import Image, ImageChops, ImageFilter, ImageOps, ImageStat

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .catalog import NatureImage
from .profile import (
    FILL_EDGE,
    FILL_EDGE_BLUR,
    FILL_MIRROR,
    FILL_OFF,
    FILL_SOLID,
    entry_fill_blur_radius,
    entry_fill_method,
    entry_fill_sample_size,
    entry_screen_ratio,
)

CACHE_ROOT = Path("/media/nature-frame/framed")
MEDIA_ROOT = Path("/media")
MEDIA_URL_ROOT = "/media/local"
MAX_LONG_EDGE = 1600
CACHE_GENERATION = "frame-v4"


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


def _median_color(
    image: Image.Image,
    box: tuple[int, int, int, int],
) -> tuple[int, int, int]:
    crop = image.crop(box)
    median = ImageStat.Stat(crop).median
    return tuple(int(max(0, min(255, value))) for value in median[:3])


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


def _resized_contain(
    image: Image.Image,
    target_w: int,
    target_h: int,
) -> tuple[Image.Image, int, int]:
    scale = min(target_w / image.width, target_h / image.height)
    resized_w = max(1, round(image.width * scale))
    resized_h = max(1, round(image.height * scale))
    resized = image.resize((resized_w, resized_h), Image.Resampling.LANCZOS)
    return resized, (target_w - resized_w) // 2, (target_h - resized_h) // 2


def _edge_strip(
    image: Image.Image,
    side: str,
    sample_size: int,
) -> Image.Image:
    sample = max(1, min(sample_size, image.width, image.height))

    if side == "top":
        return image.crop((0, 0, image.width, sample))
    if side == "bottom":
        return image.crop((0, image.height - sample, image.width, image.height))
    if side == "left":
        return image.crop((0, 0, sample, image.height))
    if side == "right":
        return image.crop((image.width - sample, 0, image.width, image.height))

    raise ValueError(f"Unknown edge side: {side}")


def _solid_bar(
    resized: Image.Image,
    side: str,
    size: tuple[int, int],
    sample_size: int,
) -> Image.Image:
    strip = _edge_strip(resized, side, sample_size)
    color = _median_color(strip, (0, 0, strip.width, strip.height))
    return Image.new("RGB", size, color)


def _stretched_bar(
    resized: Image.Image,
    side: str,
    size: tuple[int, int],
    sample_size: int,
    *,
    blur_radius: int = 0,
    mirror: bool = False,
) -> Image.Image:
    strip = _edge_strip(resized, side, sample_size)

    if mirror:
        if side in {"top", "bottom"}:
            strip = strip.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        else:
            strip = strip.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    bar = strip.resize(size, Image.Resampling.BILINEAR)

    if blur_radius > 0:
        bar = bar.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    return bar


def _paste_fill_bars(
    canvas: Image.Image,
    resized: Image.Image,
    left: int,
    top: int,
    method: str,
    sample_size: int,
    blur_radius: int,
) -> None:
    target_w, target_h = canvas.size
    image_w, image_h = resized.size

    top_gap = top
    bottom_gap = target_h - top - image_h
    left_gap = left
    right_gap = target_w - left - image_w

    def make_bar(side: str, size: tuple[int, int]) -> Image.Image:
        if method == FILL_SOLID:
            return _solid_bar(resized, side, size, sample_size)
        if method == FILL_EDGE:
            return _stretched_bar(
                resized,
                side,
                size,
                sample_size,
            )
        if method == FILL_EDGE_BLUR:
            return _stretched_bar(
                resized,
                side,
                size,
                sample_size,
                blur_radius=blur_radius,
            )
        if method == FILL_MIRROR:
            return _stretched_bar(
                resized,
                side,
                size,
                sample_size,
                mirror=True,
            )

        # Off or unknown: leave the black canvas visible.
        return Image.new("RGB", size, (0, 0, 0))

    # With contain scaling normally only one axis has meaningful gaps. These
    # branches still handle rounding or unusual aspect ratios safely.
    if top_gap > 0:
        canvas.paste(make_bar("top", (target_w, top_gap)), (0, 0))
    if bottom_gap > 0:
        canvas.paste(
            make_bar("bottom", (target_w, bottom_gap)),
            (0, top + image_h),
        )
    if left_gap > 0:
        canvas.paste(make_bar("left", (left_gap, target_h)), (0, 0))
    if right_gap > 0:
        canvas.paste(
            make_bar("right", (right_gap, target_h)),
            (left + image_w, 0),
        )


def _render_frame(
    data: bytes,
    target_ratio: float,
    destination: Path,
    fill_method: str,
    sample_size: int,
    blur_radius: int,
) -> None:
    image = _decode_rgb(data)
    target_w, target_h = _target_size(target_ratio)
    resized, left, top = _resized_contain(image, target_w, target_h)

    canvas = Image.new("RGB", (target_w, target_h), (0, 0, 0))

    if fill_method != FILL_OFF:
        _paste_fill_bars(
            canvas,
            resized,
            left,
            top,
            fill_method,
            sample_size,
            blur_radius,
        )

    canvas.paste(resized, (left, top))
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, format="JPEG", quality=92, optimize=True)


def _local_media_path(url: str) -> Path | None:
    if not url.startswith(f"{MEDIA_URL_ROOT}/"):
        return None

    relative = unquote(url[len(MEDIA_URL_ROOT) + 1 :])
    path = (MEDIA_ROOT / relative).resolve()
    media_root = MEDIA_ROOT.resolve()

    if media_root not in path.parents and path != media_root:
        raise ValueError("Invalid local media path")

    return path


async def _async_source_fingerprint(
    hass: HomeAssistant,
    image: NatureImage,
) -> str:
    path = _local_media_path(image.url)
    if path is None:
        return image.url

    def _fingerprint() -> str:
        stat = path.stat()
        return f"{image.url}|{stat.st_size}|{stat.st_mtime_ns}"

    return await hass.async_add_executor_job(_fingerprint)


async def _async_image_bytes(hass: HomeAssistant, image: NatureImage) -> bytes:
    path = _local_media_path(image.url)
    if path is not None:
        return await hass.async_add_executor_job(path.read_bytes)

    session = async_get_clientsession(hass)
    headers = {"User-Agent": "HomeAssistant-NatureFrame/0.8.0"}
    async with session.get(image.url, headers=headers, timeout=30) as response:
        response.raise_for_status()
        return await response.read()


async def async_framed_url(
    hass: HomeAssistant,
    entry: ConfigEntry,
    image: NatureImage,
    orientation: str,
) -> str:
    ratio_label = entry_screen_ratio(entry)
    target_ratio = _parse_ratio(ratio_label, orientation)
    fill_method = entry_fill_method(entry)
    sample_size = entry_fill_sample_size(entry)
    blur_radius = entry_fill_blur_radius(entry)
    source_fingerprint = await _async_source_fingerprint(hass, image)

    cache_key = hashlib.sha1(
        (
            f"{source_fingerprint}|{ratio_label}|{orientation}|"
            f"{fill_method}|{sample_size}|{blur_radius}|{CACHE_GENERATION}"
        ).encode("utf-8")
    ).hexdigest()
    destination = CACHE_ROOT / f"{cache_key}.jpg"

    if not destination.is_file():
        data = await _async_image_bytes(hass, image)
        await hass.async_add_executor_job(
            _render_frame,
            data,
            target_ratio,
            destination,
            fill_method,
            sample_size,
            blur_radius,
        )

    relative = destination.relative_to(MEDIA_ROOT).as_posix()
    return f"{MEDIA_URL_ROOT}/{relative}"


# Backwards-compatible internal alias for older callers.
async_solid_framed_url = async_framed_url
