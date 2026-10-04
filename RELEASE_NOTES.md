## Screensaver Overlay 0.10.6

Packaging release. Overlay behavior is unchanged from 0.10.4.

## Nature Frame 0.7.2

This release contains the requested no-crop solid framing and the latest
per-screen profile + Lovelace thumbnail features.

For screen-profile playlists Nature Frame creates a canvas matching the target
screen ratio. The complete artwork remains visible, while unused top/bottom or
side areas are filled with **solid colors sampled from the nearest image edge**
instead of black bars.

Use Kiosk Satellite **Fill the screen = Off**.

Each Nature Frame profile supports 16:9, 16:10, 4:3 or 3:2. Portrait playback
automatically inverts the configured landscape ratio. Framed images are created
lazily and cached under `/media/nature-frame/framed/`.

Collection switches expose representative thumbnails as `entity_picture` for
native Lovelace Picture Entity cards.
