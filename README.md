# Fotoo Overlay for Kiosk Satellite

Native Android overlays above Fotoo while Fotoo is running as Android's real DreamService/screensaver.

## Version 0.2

The proof of concept succeeded on the Raspberry Pi 4 / Android 14 panel: a real
`TYPE_APPLICATION_OVERLAY` remains visible above Fotoo.

Version 0.2 changes the behavior so there is **no permanent overlay before
Fotoo starts**. The plugin listens for Android's dreaming start/stop broadcasts
and creates overlays only while a DreamService is active.

### Now Playing

Choose a Home Assistant `media_player` entity in the plugin settings. While
Fotoo is running and the player is playing (or paused, when enabled), the
plugin shows:

- album artwork from `entity_picture`
- title
- artist
- album

The card disappears automatically when Fotoo exits.

### Doorbell

Choose:

- a doorbell/visitor trigger entity
- a camera entity
- display duration

A binary sensor triggers when it changes to `on`. An `event.*` entity
triggers whenever it receives a new event state. While Fotoo is active, the
camera overlay temporarily takes priority over Now Playing and refreshes the
camera entity's `entity_picture` about once per second.

## Install developer build

Build with GitHub Actions, download the `fotoo-overlay` workflow artifact,
extract it, then install `fotoo-system-overlay-poc-0.2.0.zip` through:

**Kiosk Satellite -> Plugin Manager -> Developer Tools -> Install from ZIP**

Kiosk Satellite must have **Display over other apps** permission.

## First test

Configure only **Now Playing entity** first, for example
`media_player.drivhus`. Start music and let Android enter Fotoo normally.
The card should appear only after Fotoo starts and disappear when Fotoo ends.

Then configure the doorbell entities.
