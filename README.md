# Fotoo Overlay for Kiosk Satellite

Native Android system overlays above Fotoo while Fotoo runs as the Android
screensaver. This repository also packages the **Nature Frame** Home Assistant
integration.

## Repository release 0.9.0

### Fotoo Overlay

The overlay plugin version is bumped to 0.9.0 as a packaging release so Kiosk
Satellite and HACS can reference the same repository release. Overlay behavior
is unchanged from 0.8.9.

### Nature Frame 0.6.0

Nature Frame now provides curated, visually coherent collections rather than
using broad topical scraping for named libraries:

- Birds · Inky Bird Frame
- Zoo · Public · Swainson
- Zoo · Private
- Kitchen · USDA Pomological Watercolors
- Kitchen · Köhler Botanical Plates
- Kitchen · Mrs Beeton Plates
- Kitchen · Mixed
- Art · Misc · Curated
- existing mammal and astronomy collections

Multiple collections can be enabled simultaneously using Home Assistant switch
entities. The Active collections playlist is balanced per collection so huge
libraries do not drown out small private albums.

Private Zoo images belong in:

`/media/nature-frame/private/Zoo Private/`

Nature Frame creates that folder automatically.

## Kiosk Satellite media setup

Point the screensaver at the stable Nature Frame media source:

- `media-source://nature_frame/active/portrait`
- `media-source://nature_frame/active/landscape`

Enable Shuffle in Kiosk Satellite.

**Important:** on the tested setup, Kiosk Satellite's **Fill the screen = Smart**
can crop poster-style artwork. Use **Fill the screen = Off** while testing if the
whole image must remain visible. A dedicated ambient/blurred no-crop renderer is
a separate follow-up feature.

## Install Fotoo Overlay

Use Kiosk Satellite **Plugin Manager -> Add plugin** and paste:

`https://github.com/mortalone/kiosk-satellite-fotoo-overlay`

## Install Nature Frame

Add the same repository to HACS as a custom integration and install
**Nature Frame**. The repository release and integration manifest are versioned
separately: repository 0.9.0 contains Nature Frame 0.6.0.
