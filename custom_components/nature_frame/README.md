# Nature Frame Home Assistant integration

Nature Frame is a streaming Media Source for Home Assistant. It builds small
remote catalog indexes and resolves an image only when it is displayed. It does
not need to download entire galleries to the Home Assistant machine.

## 0.4.0

- Adds real thumbnails to the Home Assistant Media Browser.
- Adds separate streaming galleries:
  - Birds · Inky Bird Frame
  - Mammal illustrations · Joseph Smit
  - Mammals · Featured photography
  - Night sky · Featured astronomy
  - Aurora · Featured pictures
  - Galaxies · Featured pictures
- Wikimedia Commons galleries use Commons' 1200 px derivative images rather
  than multi-megabyte originals.
- Portrait and landscape items are split from source dimensions.
- The Lovelace entity `select.nature_frame_gallery` controls which gallery
  appears under **Active gallery**.

## Kiosk Satellite

Point the portrait kiosk permanently at:

`media-source://nature_frame/active/portrait`

Then change `select.nature_frame_gallery` from Lovelace.

## Copyright and private posters

Only freely licensed/publicly reusable sources should be built into the public
integration. Copyrighted posters owned by the household should instead be added
through a private/local collection; they must not be redistributed in this
public repository.
