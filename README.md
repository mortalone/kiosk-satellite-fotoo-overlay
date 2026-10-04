# Fotoo Overlay for Kiosk Satellite

Native Android system overlays above Fotoo while Fotoo runs as the Android screensaver.

## 0.8.0

- Now Playing uses Kiosk Satellite's existing Music Assistant configuration directly when the selected KS player source is Music Assistant.
- The plugin polls Music Assistant's active queue directly, so automatic next-track transitions do not depend on the Home Assistant media_player updating correctly.
- Manual track changes and automatic queue advances are both reflected in the overlay.
- Progress uses Music Assistant queue elapsed time plus a local monotonic clock.
- Next-track title is read from Music Assistant's queue when available.
- Doorbell camera and Now Playing can remain visible simultaneously.
- Two independent doorbell triggers can show the same camera.
- Camera 100% uses a genuinely opaque Android window plus an RGB-only bitmap, so Fotoo cannot blend through the camera rectangle.
- Camera width, height and vertical position are adjustable.
- Separate opacity controls for Now Playing and the camera.
- Persistent camera test mode and instant attach/test mode remain available.

Recommended door triggers for this installation:

- Trigger 1: `binary_sensor.doorbellcamera_person_occupancy`
- Trigger 2: `binary_sensor.reolink_video_doorbell_wifi_visitor`

## Install

Use Kiosk Satellite **Plugin Manager -> Add plugin** and paste:

`https://github.com/mortalone/kiosk-satellite-fotoo-overlay`

Kiosk Satellite discovers the latest stable GitHub release and verifies the release assets.
