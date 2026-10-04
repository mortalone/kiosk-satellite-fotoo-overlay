## Screensaver Overlay 0.11.4

### Kiosk Satellite screensavers without Legacy WebView

Kiosk Satellite's own screensavers now use a different overlay path from
external Fotoo.

When Kiosk Satellite owns the foreground Activity, Now Playing, the doorbell
camera and the test overlay are attached directly above the kiosk content.
This avoids the hybrid-composition WebView layer that could cover Android
`TYPE_APPLICATION_OVERLAY` windows on Raspberry Pi hardware.

Fotoo remains unchanged and continues to use the Android system-overlay path.

After installing 0.11.4, **Legacy WebView renderer can be turned back OFF** for
testing. Restart Kiosk Satellite once after changing that renderer setting.

### Stable cover art

Now Playing artwork no longer clears while a new image is loading. Home
Assistant's selected media_player artwork is preferred over Music Assistant
queue artwork, transient signed-token changes are ignored for image identity,
and decoded covers are kept in a small memory cache.

Brief metadata gaps during track changes keep the old cover for 2.5 seconds
instead of flashing an empty square.

## Nature Frame

No Nature Frame code changes in this release.
