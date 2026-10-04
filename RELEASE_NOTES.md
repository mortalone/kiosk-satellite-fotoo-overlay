## Screensaver Overlay 0.11.1

Packaging release. Now Playing and doorbell overlay behavior is unchanged.

## Nature Frame 0.8.1

Fixes the **Zoo · Private** selector tile showing a broken/missing image.

Private collection switches no longer expose the original first private file
directly as their Lovelace `entity_picture`. Nature Frame now generates a
small, browser-safe JPEG cover under:

`/media/nature-frame/previews/private/`

The cover is regenerated when the source file changes, and it works regardless
of the source image being a transparent PNG or having spaces/Unicode in its
filename.

After updating, restart Home Assistant once. The selector card itself does not
need to be changed.
