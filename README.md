# Fotoo Overlay for Kiosk Satellite

Native Android system overlays above Fotoo while Fotoo runs as the Android screensaver.

## 0.8.5

This release is primarily a lifecycle/stability fix.

- **Critical fix:** Android system overlay windows are now removed on the Android main thread. Older builds tried to remove them from the plugin worker thread; Android could reject that removal and leave an orphan camera window visible even after disabling the plugin.
- Saving camera settings immediately recreates the camera window on the main thread, so turning Camera test mode off really removes the test camera.
- Automatic Fotoo process inference has been removed. Normal operation now uses the exact Android DreamService start/stop events; **Attach / show overlays now** is the explicit fallback if the plugin was installed while Fotoo was already running.
- Attach/test fallback automatically expires after two minutes and is also cleared when Fotoo stops or Kiosk Satellite resumes.
- Startup performs best-effort cleanup of stale Fotoo doorbell overlay windows left by older plugin sessions.
- Music Assistant HTTP polling now parses the actual `/api` JSON-RPC response shape (the queue object is returned directly), fixing Now Playing disappearing after 0.8.0.
- If direct Music Assistant polling fails, the selected Home Assistant media_player is used as a fallback instead of leaving Now Playing blank.
- Camera and Music Assistant I/O run concurrently so a slow camera snapshot cannot block track updates.
- Camera 100% remains an opaque Android window with an RGB-only bitmap.
- Camera width, height and position remain adjustable.
- Two door triggers and simultaneous camera + Now Playing remain supported.

Recommended door triggers:

- Trigger 1: `binary_sensor.doorbellcamera_person_occupancy`
- Trigger 2: `binary_sensor.reolink_video_doorbell_wifi_visitor`

## Install

Use Kiosk Satellite **Plugin Manager -> Add plugin** and paste:

`https://github.com/mortalone/kiosk-satellite-fotoo-overlay`
