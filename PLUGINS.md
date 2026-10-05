# Standalone overlay plugins

The repository now builds the original combined **Screensaver Overlay** plus
four standalone Kiosk Satellite plugin ZIPs. The standalone packages are
intended for migration/testing before they are moved to individual repositories.

Install them with **Kiosk Satellite -> Plugin Manager -> Install from ZIP**.

## 1. Now Playing Overlay

Package: `now-playing-overlay-0.1.0.zip`

Contains only the settings exposed for Now Playing. It retains the stable cover
handling and the Kiosk Satellite in-Activity overlay path that works with
**Legacy WebView renderer = Off**.

Suggested Raspberry portrait setup:

- Show overlay on: Kiosk Satellite + Fotoo
- Position: Center or Bottom
- Width: 55-65%
- Opacity: 90%

## 2. Doorbell Overlay

Package: `doorbell-overlay-0.1.0.zip`

Doorbell configuration is independent from Now Playing:

- Trigger 1
- Trigger 2
- camera entity
- camera visibility
- camera size
- position
- display time

The camera height follows the actual frame aspect ratio.

## 3. Screensaver Quick Actions

Package: `quick-actions-overlay-0.1.0.zip`

A touchable entity/action rail that can sit at any screen edge while leaving the
middle free for Now Playing. Up to six items are supported.

Each item has:

- **Display entity**: picture, friendly name and state.
- **Action entity**: the entity activated when the item is tapped.

Examples:

| Item | Display entity | Action entity |
| --- | --- | --- |
| Malte | `person.malte` | `script.kald_pa_malte` |
| Silje | `person.siljes_hansen` | `script.kald_pa_silje` |
| Dicte | `person.dicte_hansen` | `script.kald_pa_dicte` |
| Aftensmad | `script.aftensmad` | `script.aftensmad` |

Supported tap actions are inferred from the action entity domain:

- script -> `script.turn_on`
- button/input_button -> `press`
- automation -> `trigger`
- scene -> `turn_on`
- light/switch/input_boolean/fan -> `toggle`

Person entities automatically use their Home Assistant `entity_picture`.

## 4. Spectrum Visualizer Overlay

Package: `spectrum-visualizer-overlay-0.1.0.zip`

Two modes:

- **Animated**: decorative Winamp-style spectrum.
- **Microphone**: real-time 1024-point FFT from Android `AudioRecord`.

Microphone mode needs Kiosk Satellite's microphone permission. A microphone can
usually only be owned by one recording client at a time, so Voice Satellite /
wake-word recording may conflict with this mode on some Android builds. Start
with Animated mode, then test Microphone mode.

An optional media_player can gate the visualizer so it only appears while the
player state is `playing`.

## Nature Frame / Fotoo selector

See:

- `examples/screensaver-mode-package.yaml`
- `examples/screensaver-mode-card.yaml`

Nature Frame mode turns **Keep screen on** and Kiosk Satellite's own screensaver
on and selects **Home Assistant Media**.

Fotoo mode turns Kiosk Satellite's own screensaver off and **Keep screen on**
off. Android is then allowed to reach its configured DreamService (Fotoo)
without racing Kiosk Satellite's idle timer.

## Migration from the combined plugin

Do not enable a standalone Now Playing or Doorbell plugin at the same time as
the same feature in the old combined plugin, or duplicate overlays can appear.

Recommended order:

1. Install and configure Now Playing Overlay.
2. Install and configure Doorbell Overlay.
3. Verify both on the Kiosk Satellite screensaver.
4. Disable the old combined Screensaver Overlay.
5. Install Quick Actions and Visualizer independently.
