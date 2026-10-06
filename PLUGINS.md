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

## 3. Quick Actions & Clock

Package: `quick-actions-overlay-0.2.0.zip`

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

One set of up to six actions is shared across all selected contexts:

- **Show on** selects Kiosk screensavers, Fotoo, or both (existing setting).
- **Quick actions on dashboard** adds them above the normal Lovelace dashboard
  inside the Android Kiosk app. It does not add a Lovelace card in desktop browsers.
- **Quick actions in Party Mode** is off by default.
- **Clock on dashboard**, **Clock on Kiosk screensaver**, and **Clock on Fotoo**
  are independent and off by default. The clock is always hidden in Party Mode.
- **Clock position**, **Clock size**, and **Show clock date** set its appearance.

For a compact action row, choose Horizontal and turn off **Show names and
states**. Keep the existing art selector below the Lovelace player. If enabling
this clock on the Kiosk screensaver, disable Kiosk's built-in clock to avoid two
clocks. Alternatively leave this setting off and keep the existing built-in clock.

Update an existing Quick Actions plugin using the 0.2.0 ZIP; its item settings
retain the same keys. Approve the updated host-control capability when Kiosk
requests plugin trust; it is needed for the Wall Art command.

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

Put the package in your HA packages directory (enable packages in
`configuration.yaml` if necessary), then reload scripts/automations and restart
HA if the new input_select is not loaded. Use the example built-in entities card
for `input_select.raspberry_screensaver_source`.

Install Quick Actions & Clock 0.2.0 and expose its commands as Home Assistant
buttons in Kiosk's Plugin Manager. The package uses Jacob's existing prefix
`raspberry_raspberry_pi_4`; change `kiosk_prefix` once for another device.
Buttons are resolved by their standard English titles, so keep those names or
adjust the matching templates. Ensure the configured Kiosk media source is the
existing Nature Frame profile; the script retains that selected source.

- **Nature Frame** enables Keep screen on and Kiosk screensaver, selects
  Home Assistant Media, brings Kiosk to the front and starts Wall Art now.
- **Fotoo** disables the competing Kiosk idle timer and opens Fotoo immediately.
  It prefers an existing combined/Now Playing Fotoo launcher, then attaches
  Quick Actions & Clock, preserving the existing overlay owner.

Call `script.raspberry_apply_art_source` with `source: Nature Frame` or
`source: Fotoo`, or use `script.raspberry_toggle_art_source` as a single button.
The input_select expresses the requested source; it is not an Android app sensor.
The separate plugin commands **Open Fotoo with Quick Actions**, **Attach Quick
Actions to Fotoo**, and **Show Wall Art now** are also available directly.

## Private gallery covers

Update Nature Frame via HACS to the integration version 0.8.2 included in suite
release 0.11.7, restart Home Assistant and refresh the dashboard. Private library
covers now use signed local media preview URLs. Existing image folders and
profile selections are retained. Signatures renew during catalogue refresh;
images are not copied into public `/local` storage.

## Migration from the combined plugin

Do not enable a standalone Now Playing or Doorbell plugin at the same time as
the same feature in the old combined plugin, or duplicate overlays can appear.

Recommended order:

1. Install and configure Now Playing Overlay.
2. Install and configure Doorbell Overlay.
3. Verify both on the Kiosk Satellite screensaver.
4. Disable the old combined Screensaver Overlay.
5. Install Quick Actions and Visualizer independently.
