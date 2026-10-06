# Screensaver Overlay for Kiosk Satellite

Native **Now Playing** and **doorbell camera** overlays for Kiosk Satellite.
The same plugin still supports Fotoo, but Fotoo is no longer required.

## Screensaver Overlay Suite 0.11.8

The original combined Screensaver Overlay remains available as a compatibility
plugin. The same GitHub release now also publishes standalone ZIP packages for:

- **Now Playing Overlay 0.1.0**
- **Doorbell Overlay 0.1.0**
- **Quick Actions & Clock 0.2.8**
- **Spectrum Visualizer Overlay 0.1.0**

The standalone plugins are installed with Kiosk Satellite's **Install from ZIP**
while they are being tested. See `PLUGINS.md` for migration and setup.

Now Playing keeps the stable artwork handling and the in-Activity overlay path,
so Kiosk Satellite's own Home Assistant Media / Nature Frame screensaver works
with **Legacy WebView renderer = Off**.

Quick Actions adds a touchable Home Assistant entity/action rail and optional clock.
The same configured actions can now appear over the Kiosk Lovelace dashboard,
Kiosk screensavers and Fotoo. Visibility is selected in the saved Display & clock settings action; Party Mode
hides actions by default and always hides this clock.
For a compact rail, turn off **Show names and states**.

Nature Frame 0.8.2 fixes private gallery covers with signed local preview URLs.
Screensaver engine preference can be changed through the existing Screensaver,
Keep screen on and Screensaver mode setting entities.

 A person
entity can supply the displayed face while a different entity such as
`script.kald_pa_malte` runs when the item is tapped.

Spectrum Visualizer includes both a decorative animated spectrum and an
experimental microphone FFT mode.

The repository continues to package Nature Frame 0.8.2.

The overlay listens to Kiosk Satellite's official `screensaver.state` and
`screensaver.view` plugin events, so it works above Kiosk Satellite's own
screensavers, including Home Assistant Media / Nature Frame.

## Nature Frame 0.8.0

Nature Frame has one independent profile per tablet/screen. Each profile has its
own collection switches, target display ratio and now its own **framing/fill
method**.

Configure a profile under:

**Settings -> Devices & services -> Nature Frame -> Configure**

Available empty-area fill methods:

- **Off**
- **Solid color**
- **Edge stretch**
- **Edge stretch + blur**
- **Mirror**

**Edge stretch** and **Edge stretch + blur** preserve the colors along the
actual image edge. For example, if the top edge contains blue on the left and
cream on the right, those colors continue upward independently instead of
becoming one averaged color.

The profile also exposes:

- **Edge sample size**: 1–32 px
- **Edge blur radius**: 0–30 px

New profiles default to **Edge stretch + blur**, 8 px sample and 10 px blur.
Existing profiles keep the previous Solid color behavior until changed.

Use Kiosk Satellite **Fill the screen = Off**. Nature Frame creates the full
screen-ratio canvas itself while keeping the complete artwork visible.

### Per-screen media source

Choose:

**Nature Frame -> Screens / profiles -> <screen> -> Portrait/Landscape**

Legacy `active/portrait` and `active/landscape` paths remain compatible with
the first/Default profile.

### Collections

Curated collections include Birds, Zoo Public/Private, Kitchen USDA/Köhler/
Mrs Beeton/Mixed, Art Misc, mammal collections and astronomy. Multiple
collections can be enabled simultaneously.

Private Zoo images belong in:

`/media/nature-frame/private/Zoo Private/`

Private collection contents, thumbnails and image counts refresh automatically.

## Install

Use this repository in both Kiosk Satellite Plugin Manager and HACS:

`https://github.com/mortalone/kiosk-satellite-fotoo-overlay`
