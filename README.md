# Fotoo System Overlay POC for Kiosk Satellite

This is a deliberately small proof of concept.

## Goal

Verify that a Kiosk Satellite SDK 1 plugin can create a real Android
`TYPE_APPLICATION_OVERLAY` which remains visible while Fotoo is running as
Android's native screensaver (DreamService).

This is **not** the final Now Playing implementation yet. First we prove the
system-overlay layer works on the Raspberry Pi / Android 14 build.

## Important implementation detail

Kiosk Satellite's public plugin API currently does not expose an Android
`Context`, while a native WindowManager overlay needs one. Plugins run inside
the Kiosk Satellite process and are not sandboxed, so this POC obtains the
application context using:

1. `ActivityThread.currentApplication()` by reflection.
2. A fallback that walks the current Kiosk Satellite PluginHost's enclosing
   objects until it finds PluginBridge's Context.

Both are compatibility hacks. They are isolated in one method so they can be
replaced if Kiosk Satellite later exposes a supported Context/system-overlay
API.

## Build with GitHub Actions

1. Create a GitHub repository and upload the contents of this folder.
2. Open **Actions -> Build developer ZIP -> Run workflow**.
3. Download the artifact named `fotoo-system-overlay-poc`.
4. Inside it is `fotoo-system-overlay-poc-0.1.0.zip`.

## Install

In Kiosk Satellite:

**Plugin Manager -> Developer Tools -> Install from ZIP**

Choose `fotoo-system-overlay-poc-0.1.0.zip`, accept the local-development
warning, then enable the plugin.

Kiosk Satellite must already have **Display over other apps** permission.

## Test

With `Show test overlay when enabled` on, a dark card should appear near the
bottom of the screen:

    KS native overlay test
    If this stays visible over Fotoo, the approach works.

Then leave the panel untouched until Android starts Fotoo as its system
screensaver.

### Pass

The test card remains visible **above Fotoo**.

Touching elsewhere on the screen should still dismiss Fotoo and return to
Kiosk Satellite because the proof-of-concept card is deliberately
`FLAG_NOT_TOUCHABLE`.

### Fail

If the card disappears when Fotoo starts, or the plugin reports an error,
capture the plugin status and Kiosk Satellite log. That tells us which layer
the ROM is blocking.

## Next phase after a pass

Replace the test card with a real native overlay controller:

- Now Playing: title, artist, playback state and controls.
- Optional album artwork.
- Doorbell: temporary live camera overlay above Fotoo.
- Hide/show rules based on playback and doorbell state.
