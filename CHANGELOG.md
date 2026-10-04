# Changelog

## 0.11.3

- Replaces separate Doorbell **Camera width** and **Camera height** settings
  with one **Camera size** setting.
- Camera size controls width from 30–100% of the screen; height now follows the
  actual camera frame aspect ratio automatically.
- Doorbell images use FIT_CENTER inside the aspect-matched overlay, avoiding
  unnecessary cropping from an arbitrary width/height box.
- Frees one plugin setting slot for future controls.

## 0.11.2

- Fixes Now Playing failing to appear for the explicitly selected Home Assistant
  media_player when Kiosk Satellite also has its own Music Assistant / Sendspin
  player configured.
- The selected Home Assistant media_player is now authoritative for
  playing/paused/idle state; direct Music Assistant data only enriches artwork,
  title and queue metadata.
- Now Playing is polled from Home Assistant continuously while an eligible
  screensaver is active, including Kiosk Satellite's own screensavers.
- Adds **Center** as a Now Playing position.
- Adds **Now Playing width** from 30–100% of screen width, so the overlay can
  fit between Kiosk Satellite screensaver widgets.
- Saving plugin settings now rebuilds the Now Playing overlay window so geometry
  changes apply immediately.
- Removes the rarely needed optional playlist-name entity from the settings UI
  to stay within Kiosk Satellite SDK 1's 20-setting manifest limit. Playlist /
  source display still works from media_player and Music Assistant metadata.

## 0.11.1

- Packages Nature Frame 0.8.1.
- Fixes missing thumbnails on Lovelace selector tiles for private collections.
- Private collection covers are now generated as stable local JPEG previews.
- Screensaver Overlay behavior is unchanged.

## 0.11.0

- Packages Nature Frame 0.8.0.
- Adds selectable framing per screen profile: Off, Solid color, Edge stretch,
  Edge stretch + blur and Mirror.
- Adds 1–32 px edge sample size and 0–30 px blur controls.
- Edge modes preserve the varying colors along the actual image edge.
- Local/private framing cache now invalidates when a source file at the same
  path changes.
- Screensaver Overlay behavior is unchanged.

## 0.10.10

- Packages Nature Frame 0.7.6.
- Private poster exports now have transparent/white outer canvas trimmed before
  screen fitting, so the artwork itself fills one screen axis.
- Screensaver Overlay behavior is unchanged.

## 0.10.10

- Packages Nature Frame 0.7.6.
- Trims transparent outer padding from background-removed PNG posters before
  fitting them to the target screen.
- Makes private Zoo posters use much more of the available display area while
  keeping the complete visible artwork.
- Screensaver Overlay behavior is unchanged.

## 0.10.9

- Packages Nature Frame 0.7.5.
- Private library thumbnails and image counts now refresh automatically after
  files are added.
- Fixes Zoo · Private remaining hidden by the Lovelace auto-entities selector
  after images are uploaded.
- Screensaver Overlay behavior is unchanged.

## 0.10.8

- Packages Nature Frame 0.7.4.
- Virtual collections now use distinct Lovelace covers.
- Active playlists deduplicate the same underlying image across selected
  collections.
- Screensaver Overlay behavior is unchanged.

## 0.10.7

- Packages Nature Frame 0.7.3.
- Adds fallback catalogues so the public Zoo/Kitchen switches remain available
  even if Wikimedia API discovery fails at Home Assistant startup.
- Keeps Screensaver Overlay behavior unchanged.

## 0.10.6

- Packages the complete Nature Frame 0.7.2 implementation.
- Includes per-screen profiles, Lovelace collection thumbnails and solid
  edge-color no-crop framing.
- Keeps Screensaver Overlay behavior unchanged from 0.10.4.

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
