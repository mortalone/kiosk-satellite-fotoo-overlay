# Changelog

## 0.10.5

- Packages Nature Frame 0.7.2.
- Adds the requested solid edge-color framing: full artwork is preserved while
  unused bars are filled with colors sampled from the nearest image edge.
- Adds per-screen aspect ratio presets for 16:9, 16:10, 4:3 and 3:2.
- Framed images are generated lazily and cached under
  `/media/nature-frame/framed/`.
- Screensaver Overlay behavior is unchanged from 0.10.4.

## 0.10.4

- Packages Nature Frame 0.7.1.
- Every Nature Frame collection switch now exposes a representative
  `entity_picture` thumbnail for Lovelace.
- Adds collection metadata attributes including profile, image count, source,
  private/virtual flags and gallery key.
- Adds a native Home Assistant Picture Entity card example for visually
  selecting active collections without extra frontend cards.
- Keeps Screensaver Overlay behavior unchanged from 0.10.3.

## 0.10.3

- Fixes Kiosk Satellite install/update failure caused by exceeding the
  manifest limit of 20 settings.
- Replaces two overlay-target booleans with one **Show overlays on** selector.
- Moves camera test mode out of Settings and into two plugin actions:
  **Show doorbell camera test** and **Hide doorbell camera test**.
- Packages Nature Frame 0.7.0 with independent per-screen collection profiles.
- Each Nature Frame profile now has its own Home Assistant device, collection
  switches and Media Browser path.
- Keeps the old Default/active media paths for backwards compatibility.

## 0.10.1

- Extends the existing Now Playing and doorbell camera overlays to Kiosk
  Satellite's own screensavers using the official plugin events
  `screensaver.state` and `screensaver.view`.
- Adds independent **Show on Kiosk Satellite screensavers** and **Show on
  Fotoo** settings.
- Keeps black/blank Kiosk Satellite screensavers free of overlay windows.
- Reads the current screensaver state when the plugin starts, so an already
  active screensaver does not need to be restarted.
- Fotoo support remains available; the plugin is no longer Fotoo-dependent.
- Nature Frame remains at 0.6.0 in this repository release.

## 0.9.0

Packaging release containing **Nature Frame 0.6.0**.

### Nature Frame 0.6.0

- Curated Zoo Public collection from William Swainson's *Zoological
  Illustrations* Volumes I–III.
- Automatically created Zoo Private local collection.
- USDA Pomological Watercolors kitchen collection.
- Köhler botanical kitchen collection.
- Mrs Beeton kitchen plate collection.
- Kitchen Mixed and Art Misc curated virtual collections.
- Equal weighting between simultaneously active collections.
- Documentation corrected for Kiosk Satellite Smart-fill clipping.

### Fotoo Overlay

- Version bumped from 0.8.9 to 0.9.0 for repository packaging.
- No functional overlay change in this release.

## 0.8.9

- Media artwork retry/lifecycle improvements.
- Solid doorbell camera overlay behavior and existing Music Assistant overlay
  fixes.
