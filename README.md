# Fotoo Overlay for Kiosk Satellite

Native Android system overlays above Fotoo while Fotoo runs as the Android screensaver.

## 0.7.0

- Now Playing and doorbell camera can be visible at the same time.
- Two independent doorbell triggers can show the same camera.
- Separate opacity controls for Now Playing and the camera.
- Progress bar and elapsed/remaining time.
- Optional playlist/source and next-track fields.
- Persistent camera test mode for setup without pressing the real doorbell.
- Best-effort attachment when Fotoo was already running before the plugin started.

Recommended door triggers for this installation:

- Trigger 1: `binary_sensor.doorbellcamera_person_occupancy`
- Trigger 2: `binary_sensor.reolink_video_doorbell_wifi_visitor`

## Install

Use Kiosk Satellite **Plugin Manager -> Add plugin** and paste:

`https://github.com/mortalone/kiosk-satellite-fotoo-overlay`

Kiosk Satellite discovers the latest stable GitHub release and verifies the
release assets.

For local development only, **Install from ZIP** can still be used.
