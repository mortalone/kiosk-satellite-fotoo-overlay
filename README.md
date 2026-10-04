# Screensaver Overlay for Kiosk Satellite

Native **Now Playing** and **doorbell camera** overlays for Kiosk Satellite.
The same plugin still supports Fotoo, but Fotoo is no longer required.

## Screensaver Overlay 0.10.1

The plugin now listens to Kiosk Satellite's official `screensaver.state` and
`screensaver.view` plugin events.

That means the existing custom overlays can run over Kiosk Satellite's own
screensavers, including the Home Assistant Media/Nature Frame slideshow:

- the custom Now Playing card with artwork, title, artist, progress and the
  existing optional playlist/next-track fields;
- the doorbell/person camera overlay with the existing trigger and sizing
  settings;
- Fotoo remains supported independently.

Two settings control where the overlays appear:

- **Show on Kiosk Satellite screensavers** — enabled by default.
- **Show on Fotoo** — enabled by default.

Black/blank Kiosk Satellite screensavers are deliberately left untouched.

The old **Attach / show overlays now** command remains available as a manual
preview/fallback, but it is no longer needed for normal Kiosk Satellite
screensaver operation.

## Nature Frame 0.6.0

This repository also packages the **Nature Frame** Home Assistant integration.

Curated collections include:

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
entities. The Active collections playlist is balanced per collection so large
libraries do not drown out small private albums.

Private Zoo images belong in:

`/media/nature-frame/private/Zoo Private/`

Nature Frame creates that folder automatically.

## Kiosk Satellite media setup

Point the Kiosk Satellite screensaver at one of the stable Nature Frame sources:

- `media-source://nature_frame/active/portrait`
- `media-source://nature_frame/active/landscape`

Enable Shuffle.

On the tested setup, **Fill the screen = Smart** can crop poster-style artwork.
Use **Fill the screen = Off** when the complete artwork must be preserved until
the dedicated ambient/blurred no-crop renderer is added.

## Install the overlay plugin

Use Kiosk Satellite **Plugin Manager -> Add plugin** and paste:

`https://github.com/mortalone/kiosk-satellite-fotoo-overlay`

## Install Nature Frame

Add the same repository to HACS as a custom integration and install
**Nature Frame**. The repository/plugin and Nature Frame integration keep
separate semantic versions.
