# Nature Frame Home Assistant integration

Nature Frame is a streaming Media Source for Home Assistant for Kiosk Satellite
and other Home Assistant media consumers.

## 0.8.0

### One collection profile per screen

Nature Frame profiles map explicitly to tablets/screens. Each profile has its
own collection switches, Media Source folder, target aspect ratio and framing
settings.

In Home Assistant Media:

**Nature Frame -> Screens / profiles -> <profile name> -> Portrait/Landscape**

Point each Kiosk Satellite device at its own profile folder and keep
**Fill the screen = Off** so Nature Frame controls the no-crop framing.

### Selectable empty-area fill

Configure a Nature Frame profile from **Settings -> Devices & services ->
Nature Frame -> Configure**.

Available fill methods:

- **Off** — black unused area; the artwork is still contained without cropping.
- **Solid color** — one median color sampled from the nearest image edge.
- **Edge stretch** — copies the nearest edge strip and stretches it outward.
  Different colors along the edge remain different across the filled area.
- **Edge stretch + blur** — same as Edge stretch with a configurable blur.
- **Mirror** — mirrors the nearest edge strip into the unused area.

Two tuning controls are available:

- **Edge sample size**: 1–32 px. Use 1–2 px for a literal continuation of the
  last pixel rows/columns; 6–10 px is smoother on textured artwork.
- **Edge blur radius**: 0–30 px. Used by Edge stretch + blur.

New profiles default to **Edge stretch + blur**, sample size **8 px**, blur
**10 px**. Existing profiles without a saved fill setting retain the previous
**Solid color** behavior until changed.

Changing framing settings creates a different cache key automatically; replacing
a local/private image at the same path also invalidates its framed cache via
file size/mtime fingerprinting.

### Curated collections

- **Birds · Inky Bird Frame**
- **Zoo · Public · Swainson**
- **Zoo · Private**
- **Kitchen · USDA Pomological Watercolors**
- **Kitchen · Köhler Botanical Plates**
- **Kitchen · Mrs Beeton Plates**
- **Kitchen · Mixed**
- **Art · Misc · Curated**
- existing mammal and astronomy collections

Multiple collections can be active in each screen profile independently. The
playlist is balanced and duplicate source-image URLs are removed.

### Private collections

Nature Frame creates:

`/media/nature-frame/private/Zoo Private/`

automatically. Put JPG/JPEG, PNG, WebP or GIF files there. Private images remain
local to Home Assistant.

Any additional first-level folder below
`/media/nature-frame/private/` also becomes a private collection when it
contains supported images. Private folders are rescanned automatically.

### Poster cleanup

Nature Frame trims large transparent export canvases and clearly uniform outer
canvas before fitting the image. It does not intentionally remove a normal
printed poster border. For archival/other use, keep your separately cleaned
source files in the private library.
