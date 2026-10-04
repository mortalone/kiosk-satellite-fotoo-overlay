# Screensaver Overlay for Kiosk Satellite

Native **Now Playing** and **doorbell camera** overlays for Kiosk Satellite.
The same plugin still supports Fotoo, but Fotoo is no longer required.

## Screensaver Overlay 0.10.8

The overlay listens to Kiosk Satellite's official `screensaver.state` and
`screensaver.view` plugin events, so it works above Kiosk Satellite's own
screensavers, including Home Assistant Media / Nature Frame.

The plugin manifest now stays within Kiosk Satellite's hard limit of **20
settings**:

- the two destination toggles are consolidated into one **Show overlays on**
  selector;
- **Camera test mode** is no longer a persistent setting and is available as
  **Show doorbell camera test** / **Hide doorbell camera test** actions.

Existing Now Playing, Music Assistant, progress and doorbell camera behavior is
otherwise preserved.

## Nature Frame 0.7.4

Nature Frame now has **one independent profile per tablet/screen**.

The existing installation becomes the backwards-compatible **Default** profile.
Add another Nature Frame integration entry for every screen that needs its own
mix, for example **Køkken tablet**, **Stue** or **1. sal hub**.

Each profile has:

- its own Home Assistant device;
- its own collection switches;
- its own Media Source folder under
  **Nature Frame -> Screens / profiles -> <profile>**.

Nature Frame 0.7.1 also exposes a representative collection thumbnail through
each switch entity's `entity_picture`, so Home Assistant's built-in Picture
Entity card can be used as a visual album selector.

Each Kiosk Satellite screen is then pointed at that profile's Portrait or
Landscape folder. The profile—not the switch itself—is what associates a set of
collections with a particular tablet.

Curated collections include Birds, Zoo Public/Private, the three coherent
Kitchen series, Kitchen Mixed, Art Misc, mammal collections and astronomy.

## Kiosk Satellite media setup

For a named profile, choose:

**Nature Frame -> Screens / profiles -> <that screen> -> Portrait/Landscape**

Enable Shuffle.

Legacy paths `media-source://nature_frame/active/portrait` and
`.../landscape` still resolve to the first/Default profile.

On the tested setup, **Fill the screen = Smart** can crop poster-style artwork.
Use **Fill the screen = Off** if the whole image must remain visible until the
dedicated ambient/blurred no-crop renderer is added.

## Install

Use the repository in both Kiosk Satellite Plugin Manager and HACS:

`https://github.com/mortalone/kiosk-satellite-fotoo-overlay`


### Nature Frame solid framing

Nature Frame 0.7.2 pre-frames screen-profile images to the configured target
aspect ratio. Empty bars use solid median colors sampled from the adjacent
image edge, so poster-style artwork keeps its full frame without black bars.

Use Kiosk Satellite **Fill the screen = Off** with this mode.
