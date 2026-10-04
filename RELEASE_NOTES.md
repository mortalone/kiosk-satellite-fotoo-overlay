## Screensaver Overlay 0.10.1

The existing custom overlays now work on **Kiosk Satellite's own screensavers**,
not only Fotoo.

- Uses Kiosk Satellite's official `screensaver.state` and `screensaver.view`
  plugin events.
- Keeps the custom Now Playing card, artwork, progress bar and Music Assistant
  queue handling.
- Keeps the existing dual door/person triggers and camera overlay.
- Adds separate settings for **Show on Kiosk Satellite screensavers** and
  **Show on Fotoo**.
- Black/blank screensavers remain untouched.
- The plugin reads initial screensaver state at startup so it can attach to a
  slideshow that is already running.
- Fotoo support remains available.

## Nature Frame 0.6.0

The same repository contains the current Nature Frame integration with the
curated Zoo/Kitchen collections, private Zoo collection, multi-collection
switches and balanced active playlists.

For poster-like artwork, use **Fill the screen = Off** during testing because
Kiosk Satellite Smart fill can crop the complete image on the tested device.
