## Screensaver Overlay 0.10.5

Packaging release. Overlay behavior is unchanged from 0.10.4.

## Nature Frame 0.7.2

This release adds the requested no-crop solid framing.

Nature Frame now prepares screen-profile images on a canvas matching the target
screen ratio. The original artwork remains complete, while unused top/bottom or
side areas are filled with **solid colors sampled from the nearest image edge**
instead of black bars.

Use Kiosk Satellite **Fill the screen = Off**.

Each Nature Frame profile can use 16:9, 16:10, 4:3 or 3:2. Portrait playback
automatically inverts the configured landscape ratio. Framed images are
generated only when needed and cached under `/media/nature-frame/framed/`.

Nature Frame 0.7.1 thumbnail/entity-picture support and per-screen profiles
remain included.
