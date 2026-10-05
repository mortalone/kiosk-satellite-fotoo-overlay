## Screensaver Overlay Suite 0.11.5

This release starts the migration from one large overlay plugin to smaller,
independent plugins. The existing combined **Screensaver Overlay** is still
included and remains functionally unchanged.

### Standalone ZIPs

The release publishes:

- `now-playing-overlay-0.1.0.zip`
- `doorbell-overlay-0.1.0.zip`
- `quick-actions-overlay-0.1.0.zip`
- `spectrum-visualizer-overlay-0.1.0.zip`

Install these from **Kiosk Satellite -> Plugin Manager -> Install from ZIP**.

### Now Playing Overlay

Keeps the stable cover-art cache and the in-Activity rendering path that works
on Kiosk Satellite's own Home Assistant Media screensaver with **Legacy WebView
renderer = Off**.

### Doorbell Overlay

Doorbell triggers/camera/size/position/time are now independent from Now
Playing, freeing the per-plugin settings budget.

### Screensaver Quick Actions

Adds a touchable rail with up to six items. Each item has a display entity and
an optional separate action entity. Example:

- display: `person.malte`
- action: `script.kald_pa_malte`

The face comes from the person's `entity_picture`; tapping the item runs the
script. Script, button, automation, scene, light, switch, input_boolean and fan
actions are supported.

### Spectrum Visualizer

Adds a Winamp-style spectrum with:

- **Animated** mode
- **Microphone** mode using a 1024-point FFT from Android AudioRecord
- optional media_player gating so it only appears while playback is playing

Microphone mode is experimental because Android devices may not allow the
visualizer and Voice Satellite/wake-word recording to own the microphone at the
same time.

### Nature Frame / Fotoo selector

`examples/screensaver-mode-package.yaml` switches deterministically:

- Nature Frame: Keep screen on ON + Kiosk screensaver ON + Home Assistant Media
- Fotoo: Kiosk screensaver OFF + Keep screen on OFF

This avoids a race between Kiosk Satellite's idle timer and Android/Fotoo.

See `PLUGINS.md` for migration details.
