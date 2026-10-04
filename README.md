# Screensaver Overlay for Kiosk Satellite

Native **Now Playing** and **doorbell camera** overlays for Kiosk Satellite.
The same plugin still supports Fotoo, but Fotoo is no longer required.

## Screensaver Overlay 0.11.2

Now Playing follows the explicitly selected Home Assistant media_player on both
Kiosk Satellite's own screensavers and Fotoo. If Kiosk Satellite also has a
Music Assistant / Sendspin player configured, MA only enriches metadata and no
longer overrides the selected speaker's playback state.

Now Playing can be positioned at **Top / Center / Bottom** and sized from
**30–100%** of the screen width, which makes it possible to fit the card between
Kiosk Satellite clock/weather/battery widgets.

The repository continues to package Nature Frame 0.8.1.

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
