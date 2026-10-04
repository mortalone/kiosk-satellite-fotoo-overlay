# Nature Frame Home Assistant integration

Nature Frame is a streaming Media Source for Home Assistant for Kiosk Satellite
and other Home Assistant media consumers.

## 0.6.0

This release changes the collection philosophy: public collections are based on
named works, artists or institutional series instead of broad topical scraping.

### Curated collections

- **Birds · Inky Bird Frame**
- **Zoo · Public · Swainson** — balanced across all three volumes of William
  Swainson's *Zoological Illustrations*.
- **Zoo · Private** — local household collection created automatically at
  `/media/nature-frame/private/Zoo Private/`.
- **Kitchen · USDA Pomological Watercolors** — one coherent USDA series.
- **Kitchen · Köhler Botanical Plates** — plates from *Köhlers
  Medizinal-Pflanzen*.
- **Kitchen · Mrs Beeton Plates** — extracted plates from *Mrs. Beeton's Book
  of Household Management*.
- **Kitchen · Mixed** — virtual collection combining the three kitchen series.
- **Art · Misc · Curated** — deliberately broad virtual collection made only
  from the named curated source collections.
- The existing mammal and astronomy collections remain available.

### Multiple active collections

Every collection has a Home Assistant switch. Any combination can be enabled.
Keep Kiosk Satellite pointed at:

- `media-source://nature_frame/active/portrait`
- `media-source://nature_frame/active/landscape`

When multiple collections are enabled, Nature Frame now balances the playlist so
each active collection contributes the same number of entries. A very large
collection therefore cannot dominate a small private album.

The legacy `select.nature_frame_gallery` remains for compatibility. Choosing a
value there intentionally switches back to one active collection.

### Private collections

Nature Frame creates:

`/media/nature-frame/private/Zoo Private/`

automatically. Put JPG/JPEG, PNG, WebP or GIF files there and reload/browse
Nature Frame. The files remain local to Home Assistant and are never committed
to this public repository.

Any additional first-level folder below
`/media/nature-frame/private/` also becomes a private collection when it
contains supported images. Reload the integration after adding a brand-new
folder so Home Assistant can create its switch entity.

### Framing / clipping

Kiosk Satellite's current **Fill the screen = Smart** behavior can still crop
poster-like images on the tested setup. Do not rely on Smart for no-crop
display. For testing this release, use **Fill the screen = Off** when preserving
the complete artwork is more important than filling the panel.

A dedicated ambient/blurred no-crop renderer is tracked separately; it is not
claimed as part of Nature Frame 0.6.0.

## Source policy

Built-in public collections must be freely reusable and must come from a
recognizable, coherent source series. Broad topical categories belong only in a
deliberately mixed/curated collection such as **Art · Misc**, not in collections
presented as a single visual series.
