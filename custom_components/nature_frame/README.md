# Nature Frame Home Assistant integration

Companion integration for the **Nature Frame Sync** Home Assistant app.

It creates a writable Home Assistant select:

`select.nature_frame_gallery`

Add that entity to Lovelace as a normal Entities card, Tile card, or dropdown. Changing the selection rebuilds:

- `/media/nature-frame/active/portrait`
- `/media/nature-frame/active/landscape`

using hard links where possible, so selecting a gallery does not duplicate hundreds of megabytes of images.

## Kiosk Satellite

Point **Home Assistant Media** to:

- `nature-frame/active/portrait` for a portrait kiosk
- `nature-frame/active/landscape` for a landscape kiosk

The selected gallery is then controlled from Lovelace.

Kiosk Satellite builds its slideshow playlist when a screensaver session starts. If you change the gallery while the screensaver is already running, restart the screensaver to rebuild the playlist immediately.

## Install with HACS

Add this repository as a HACS custom repository of type **Integration**:

`https://github.com/mortalone/kiosk-satellite-fotoo-overlay`

Install **Nature Frame**, restart Home Assistant, then add the **Nature Frame** integration under Devices & services.
