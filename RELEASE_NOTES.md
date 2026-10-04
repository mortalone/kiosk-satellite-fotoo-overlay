## Screensaver Overlay 0.10.10

Packaging release. Overlay behavior is unchanged.

## Nature Frame 0.7.6

This fixes PhotoRoom/background-remover PNG files appearing much smaller than
the screen.

Those tools often make the outer background transparent without reducing the
actual canvas size. Nature Frame previously scaled the entire transparent
canvas, so the poster itself could occupy only the middle of the display.

Nature Frame now trims only transparent outer padding first, then scales the
visible artwork as large as possible while preserving the full poster.

The framing cache version is also bumped, so old framed copies are regenerated
automatically after the update.
