# Fotoo Overlay for Kiosk Satellite

Native Android system overlays above Fotoo while Fotoo runs as the Android screensaver.

## Fotoo Overlay 0.8.9

- Fixes the initial missing cover-art race: if a track/image changes while an older artwork request is still in flight, the new image is fetched immediately afterwards.
- Artwork fetches retry when Music Assistant publishes the track before its image proxy is ready.
- A cover already supplied by the selected Home Assistant media_player is retained while a Music Assistant queue snapshot temporarily has no image.
- Camera visibility at 100% uses an RGB_565 Android overlay surface and removes FLAG_NOT_TOUCHABLE, giving the camera a solid surface.
- At 100% the camera rectangle consumes touches; touches outside the camera still reach Fotoo. Below 100%, the camera remains pass-through.
- Existing lifecycle cleanup, direct Music Assistant queue tracking, dual door triggers, camera sizing/position and simultaneous Now Playing + camera remain supported.

Recommended door triggers:

- Trigger 1: `binary_sensor.doorbellcamera_person_occupancy`
- Trigger 2: `binary_sensor.reolink_video_doorbell_wifi_visitor`

## Install Fotoo Overlay

Use Kiosk Satellite **Plugin Manager -> Add plugin** and paste:

`https://github.com/mortalone/kiosk-satellite-fotoo-overlay`

---

## Home Assistant integration: Nature Frame 0.5.0

The same repository contains **Nature Frame**, a streaming Home Assistant Media
Source designed for Kiosk Satellite photo screensavers.

Nature Frame 0.5.0 adds:

- multiple simultaneously active collections through Home Assistant switches;
- a Zoo art/poster collection from Wikimedia Commons;
- private collections from `/media/nature-frame/private/<collection>/`;
- thumbnails throughout the Home Assistant Media Browser;
- stable `active/portrait` and `active/landscape` folders, so the kiosk source
  does not need to change when collections are enabled or disabled.

For Kiosk Satellite, use **Home Assistant Media**, enable **Shuffle**, and set
**Fill the screen** to **Smart** for full-frame posters over a blurred ambient
background instead of clipping.
