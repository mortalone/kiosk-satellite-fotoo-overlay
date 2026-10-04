# Nature Frame Home Assistant integration

Nature Frame is a streaming Media Source for Home Assistant for Kiosk Satellite
and other Home Assistant media consumers.

## 0.7.2

### One collection profile per screen

Nature Frame profiles now map explicitly to tablets/screens.

The existing installation becomes the backwards-compatible **Default** profile.
Add another Nature Frame integration entry for every screen that needs its own
collection mix, for example:

- **Køkken tablet**
- **Stue**
- **1. sal hub**

Each profile gets its own Home Assistant device and its own collection switches.
That makes it clear which switches control which screen.

In Home Assistant Media the profiles appear under:

**Nature Frame -> Screens / profiles -> <profile name> -> Portrait/Landscape**

Point each Kiosk Satellite device at its own profile folder. Example:

`media-source://nature_frame/profile/kokken-tablet/landscape`

The old `active/portrait` and `active/landscape` paths remain compatible and
resolve to the first/Default profile.

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
playlist is balanced so each active collection contributes the same number of
entries.

### Private collections

Nature Frame creates:

`/media/nature-frame/private/Zoo Private/`

automatically. Put JPG/JPEG, PNG, WebP or GIF files there. Private images remain
local to Home Assistant.

Any additional first-level folder below
`/media/nature-frame/private/` also becomes a private collection when it
contains supported images.

### Framing / clipping

Kiosk Satellite's current **Fill the screen = Smart** behavior can still crop
poster-like images on the tested setup. Use **Fill the screen = Off** when the
whole artwork must remain visible until the dedicated ambient/blurred no-crop
renderer is implemented.


### Solid framing

For screen-profile playlists, Nature Frame 0.7.2 lazily creates a canvas that
matches the profile's configured display ratio. The complete artwork is kept
inside that canvas. Any unused top/bottom or side area is filled with a **solid
color sampled from the nearest edge of the image**, rather than black.

This is designed to be used with Kiosk Satellite:

**Fill the screen = Off**

Choose the screen's landscape aspect ratio in the Nature Frame profile options.
Portrait playback automatically uses the inverted ratio. Generated images are
cached under `/media/nature-frame/framed/`.
