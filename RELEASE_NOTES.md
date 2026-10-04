## Screensaver Overlay 0.10.10

Packaging release. Overlay behavior is unchanged.

## Nature Frame 0.7.6

Private posters exported from PhotoRoom/upscalers can contain a large invisible
or white square canvas around the actual artwork. Upscaling that file does not
make the poster larger on screen because the empty canvas is scaled too.

Nature Frame now removes that outer canvas automatically before framing:

- transparent padding is trimmed;
- large near-uniform opaque margins are also detected and trimmed;
- the remaining poster is scaled to fill the target screen on one axis while
  preserving the full poster and its aspect ratio;
- old framed renders are bypassed by a new cache generation.

Keep Kiosk Satellite **Fill the screen = Off**.
