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

Package: `quick-actions-overlay-0.2.8.zip`

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

Quick Actions has its own update repository:
https://github.com/mortalone/kiosk-satellite-quick-actions

Use that URL in Kiosk Satellite Plugin Manager to install and update directly
from GitHub. ZIP installations have no repository source; install once through
Add plugin with this URL to associate the same ID with its update source.
The normal settings retain all six display/action pairs, battery controls,
item order and per-item visibility rules.

Run **Display & clock settings (saved)** in the plugin's Actions to select:

- Quick actions on the normal dashboard in the Android Kiosk app.
- Optional Quick actions in Party Mode (off by default; existing Party opt-in also works).
- Independent clock visibility for dashboard, Kiosk screensaver and Fotoo.
- Date, clock position and size.

Press Save; these display choices persist across restarts and do not consume
Kiosk's limit of 20 regular settings. **Show on** still selects the action rail's
Kiosk/Fotoo screensaver contexts (Kiosk Satellite, Fotoo or both).
The plugin clock is always hidden in Party Mode. Leave it disabled on Kiosk
screensavers if retaining Kiosk's built-in clock, to avoid two clocks.
For a compact action row, select Horizontal and turn off Show names and states.
Approve host.control if Kiosk prompts for updated trust; Wall Art needs it.

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

## Simple idle engine switch (recommended)

`examples/screensaver-engine-script.yaml` is a single script for HA's script YAML
editor. It switches only the three existing Kiosk setting entities: Screensaver,
Keep screen on, and Screensaver mode. With Kiosk screensaver enabled it selects
Fotoo dominance by disabling Kiosk screensaver and Keep screen on. Otherwise it
selects Home Assistant Media and enables both settings for Kiosk dominance.
No helper, package or automation is required. It does not launch Fotoo, start
Wall Art immediately or touch the separate Screensaver active entity. Android
must already have Fotoo configured as its screensaver, as in the existing setup.

Quick Actions is updated through its dedicated repo. From 0.2.9, **Show on**
contains permanent combinations for dashboard, Kiosk screensaver and Fotoo.

## Optional immediate Nature Frame / Fotoo selector

See:

- `examples/screensaver-mode-package.yaml`
- `examples/screensaver-mode-card.yaml`

Put the package in your HA packages directory (enable packages in
`configuration.yaml` if necessary), then reload scripts/automations and restart
HA if the new input_select is not loaded. Use the example built-in entities card
for `input_select.raspberry_screensaver_source`.

Install Quick Actions & Clock 0.2.8 and expose its commands as Home Assistant
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
release 0.11.8, restart Home Assistant and refresh the dashboard. Private library
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
