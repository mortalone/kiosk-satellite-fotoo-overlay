# Nature Frame Home Assistant integration

Nature Frame is now a **streaming media source** for Home Assistant.

It no longer needs to download an entire gallery before Kiosk Satellite can use it. The integration fetches a small catalog/index from the source repository, exposes the images through Home Assistant's Media Source browser, and Kiosk Satellite resolves each image URL only when that slide is shown.

## Lovelace

The integration creates:

`select.nature_frame_gallery`

Use it as a dropdown/tile on Lovelace. Kiosk Satellite can stay pointed at:

**Nature Frame → Active gallery · Portrait**

Changing the select changes which gallery the active folder exposes the next time Kiosk Satellite builds its playlist.

## Storage

Streaming mode stores no full image collection on the Home Assistant machine. The old **Nature Frame Sync** app/add-on remains optional for a future offline-cache mode, but it is not required for normal use.

## Orientation

- Active gallery · Portrait → portrait assets
- Active gallery · Landscape → landscape assets

The Inky Bird Frame provider currently exposes 176 approved species in each orientation.

## Future collections

Additional providers (night sky, mammals, nature, insects, etc.) can be added as separate galleries. They will appear as extra options in `select.nature_frame_gallery`.
