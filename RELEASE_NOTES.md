## Screensaver Overlay 0.10.3

This release fixes the Plugin Manager error **Too many settings or commands**.

Kiosk Satellite allows at most 20 settings per plugin. The overlay now uses
exactly 20:

- **Show overlays on** replaces the previous two destination toggles.
- Camera test mode moved to plugin actions:
  **Show doorbell camera test** and **Hide doorbell camera test**.

The Now Playing and doorbell overlays continue to work on Kiosk Satellite's own
screensavers and on Fotoo.

## Nature Frame 0.7.0

Nature Frame now supports one independent collection profile per tablet/screen.

Create entries named after the screen, then select the matching folder in that
tablet's Kiosk Satellite:

**Nature Frame -> Screens / profiles -> <screen> -> Portrait/Landscape**

Each profile has its own Home Assistant device and collection switches, so the
Kitchen tablet can use Kitchen collections while another screen can use Birds,
Zoo or a different mix.

The old Active collections paths remain compatible with the first/Default
profile.
