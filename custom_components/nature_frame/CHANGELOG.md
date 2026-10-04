# Nature Frame changelog

## 0.7.6

- Automatically trims transparent outer padding before fitting private artwork.
- Also detects and trims large opaque, near-uniform export canvases such as
  white margins added by background-removal or upscaling tools.
- The poster itself is then scaled to fill the available screen on one axis
  while preserving its full aspect ratio.
- Bumps framed-image cache generation so existing small cached renders are not
  reused.

## 0.7.6

- Fixes private PNG posters becoming tiny after background removal.
- Transparent outer canvas/padding is cropped before Nature Frame scales and
  frames the artwork.
- Preserves the visible poster itself and its border; only transparent padding
  outside the visible artwork is removed.
- Bumps the framing cache key so existing cached images are regenerated
  automatically.

## 0.7.5

- Fixes private collections not appearing in the Lovelace selector after images
  are added.
- Private collection contents are rescanned automatically.
- Collection switch thumbnails and image_count attributes now use live catalog
  data instead of the startup snapshot.
- No Home Assistant restart is required just to add images to an existing
  private collection such as Zoo · Private.

## 0.7.4

- Gives virtual collections such as Kitchen · Mixed and Art · Misc their own
  representative cover image instead of reusing the first source collection's
  thumbnail.
- Deduplicates active playlists by image URL when a virtual collection and one
  of its source collections are enabled together.
- Keeps public fallback catalogues, per-screen profiles, Lovelace thumbnails
  and solid edge-color framing.

## 0.7.3

- Adds built-in fallback catalogues for Zoo · Public · Swainson and the three
  Kitchen collections.
- Public collection switches now still exist when the Wikimedia API cannot be
  reached from Home Assistant during startup.
- The normal Wikimedia API catalogue remains preferred and supplies the larger
  collection when available.
- Keeps per-screen profiles, Lovelace thumbnails and solid edge-color framing.

## 0.7.2

- Adds solid edge-color framing for screen-profile playlists.
- Nature Frame now creates a screen-ratio canvas before handing an image to
  Kiosk Satellite. Empty top/bottom or side areas are filled with solid median
  colors sampled from the nearest image edge instead of black.
- Keeps the full artwork intact: use Kiosk Satellite **Fill the screen = Off**.
- Adds a per-profile screen aspect-ratio setting with 16:9, 16:10, 4:3 and 3:2
  presets. Portrait mode automatically uses the inverted ratio.
- Generated framed images are cached lazily under
  `/media/nature-frame/framed/`; images are only processed when displayed.

## 0.7.1

- Exposes each collection's representative thumbnail through the switch
  entity's `entity_picture`.
- Adds profile, gallery key, image count, source and private/virtual metadata
  attributes to collection switches.
- Adds stable suggested entity IDs for newly created screen profiles.
- Adds a native Lovelace Picture Entity grid example with tap-to-toggle.

## 0.7.0

- Adds one independent collection profile per tablet/screen.
- Existing installations migrate implicitly to a backwards-compatible Default
  profile without changing the config-entry version.
- Additional Nature Frame entries can be named after the target screen, such as
  Kitchen tablet, Living room or 1st floor.
- Every profile gets its own Home Assistant device and collection switches.
- Adds **Nature Frame -> Screens / profiles** to the Media Browser.
- Adds stable per-profile media paths:
  `media-source://nature_frame/profile/<profile>/portrait` and
  `.../landscape`.
- Keeps legacy `active/portrait` and `active/landscape` paths working for
  the first/Default profile.

## 0.6.0

- Replaces the broad Zoo-art source with **Zoo · Public · Swainson**, balanced
  across *Zoological Illustrations* Volumes I–III.
- Creates **Zoo · Private** automatically under Home Assistant local media.
- Adds **Kitchen · USDA Pomological Watercolors**.
- Adds **Kitchen · Köhler Botanical Plates**.
- Adds **Kitchen · Mrs Beeton Plates**.
- Adds virtual **Kitchen · Mixed** and **Art · Misc · Curated** collections.
- Keeps existing Birds, mammal and astronomy collections.
- Balances multi-collection playlists so large libraries do not dominate small
  collections.
- Keeps the legacy single-gallery select for backwards compatibility.
- Corrects documentation: Kiosk Satellite Smart fill may crop artwork on the
  tested setup; use Fill the screen = Off for guaranteed no-crop display until
  the dedicated ambient renderer is available.

## 0.5.0

- Added multi-collection selection through Home Assistant switches.
- Added private/local collection discovery.
- Added thumbnails in the Home Assistant Media Browser.
- Added stable Active collections Portrait/Landscape media folders.

## 0.4.0

- Added streaming Wikimedia Commons collections and Media Browser thumbnails.
