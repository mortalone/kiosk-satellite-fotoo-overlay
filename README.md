# Fotoo Overlay for Kiosk Satellite

Native Android system overlays above Fotoo while Fotoo runs as the Android screensaver.

## 0.8.6

- Fixes the initial missing cover-art race: if a track/image changes while an older artwork request is still in flight, the new image is fetched immediately afterwards.
- Artwork fetches retry when Music Assistant publishes the track before its image proxy is ready.
- A cover already supplied by the selected Home Assistant media_player is retained while a Music Assistant queue snapshot temporarily has no image.
- Camera visibility at 100% now uses an RGB_565 Android overlay surface and removes FLAG_NOT_TOUCHABLE. This avoids Android's pass-through system-overlay constraints and gives the camera a genuinely solid surface.
- At 100% the camera rectangle consumes touches; touches outside the camera still reach Fotoo. Below 100%, the camera remains pass-through.
- Existing lifecycle cleanup, direct Music Assistant queue tracking, dual door triggers, camera sizing/position and simultaneous Now Playing + camera remain supported.

Recommended door triggers:

- Trigger 1: `binary_sensor.doorbellcamera_person_occupancy`
- Trigger 2: `binary_sensor.reolink_video_doorbell_wifi_visitor`

## Install

Use Kiosk Satellite **Plugin Manager -> Add plugin** and paste:

`https://github.com/mortalone/kiosk-satellite-fotoo-overlay`
