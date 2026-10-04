## Screensaver Overlay 0.11.0

Packaging release. Now Playing and doorbell overlay behavior is unchanged.

## Nature Frame 0.8.0

Nature Frame now lets each screen profile choose how unused space around a
contained image is rendered.

Available modes:

- **Off** — black unused space.
- **Solid color** — one median color sampled from the nearest image edge.
- **Edge stretch** — stretches the nearest 1–32 pixel edge strip outward while
  preserving different colors across that edge.
- **Edge stretch + blur** — Edge stretch plus configurable 0–30 px blur.
- **Mirror** — mirrors the sampled edge strip outward.

Configure the current profile under **Settings -> Devices & services -> Nature
Frame -> Configure**.

For the poster use case, start with **Edge stretch**, sample size **1–2 px** if
you want the literal last pixel rows continued outward. For a softer ambient
look, use **Edge stretch + blur**, sample **8 px**, blur **10 px**.

New profiles default to Edge stretch + blur. Existing profiles remain on the
previous Solid color behavior until changed.

Keep Kiosk Satellite **Fill the screen = Off**.
