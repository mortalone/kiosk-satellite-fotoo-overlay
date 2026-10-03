# Fotoo Overlay for Kiosk Satellite

Native Android system overlays above Fotoo while Fotoo runs as the Android screensaver.

## 0.7.2

- Now Playing and doorbell camera can be visible at the same time.
- Two independent doorbell triggers can show the same camera.
- Separate opacity controls for Now Playing and the camera.
- Progress bar and elapsed/remaining time.
- Optional playlist/source and next-track fields.
- Persistent camera test mode for setup without pressing the real doorbell.
- Best-effort attachment when Fotoo was already running before the plugin started.
- **Attach / show overlays now** test toggle: use it from Remote Admin if Fotoo is already running and the plugin did not receive the original DreamService start event. It forces Now Playing and, when Camera test mode is enabled, the camera overlay immediately. The toggle is cleared when Kiosk Satellite comes back to the foreground.
- 100% opacity is now truly opaque. Previous versions used semi-transparent base backgrounds in addition to the opacity control, so even 100% could still look translucent.

Recommended door triggers for this installation:

- Trigger 1: `binary_sensor.doorbellcamera_person_occupancy`
- Trigger 2: `binary_sensor.reolink_video_doorbell_wifi_visitor`

## Install

Use Kiosk Satellite **Plugin Manager -> Add plugin** and paste:

`https://github.com/mortalone/kiosk-satellite-fotoo-overlay`

Kiosk Satellite discovers the latest stable GitHub release and verifies the
release assets.

For local development only, **Install from ZIP** can still be used.
