# Nature Frame changelog

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
