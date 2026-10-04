# Nature Frame Home Assistant integration

Nature Frame is a streaming Media Source for Home Assistant. It builds small
remote catalog indexes and resolves an image only when it is displayed. It does
not need to download entire remote galleries to the Home Assistant machine.

## 0.5.0

- Multiple collections can be active at the same time.
- Every collection gets a Home Assistant switch. Turn on any combination of
  collections and keep Kiosk Satellite pointed at the stable **Active
  collections** folder.
- The old `select.nature_frame_gallery` remains as a compatibility helper:
  choosing an item there intentionally returns to one active collection.
- Adds **Zoo art & posters · Wikimedia Commons**.
- Adds private/local collections. Every first-level folder under
  `/media/nature-frame/private/` becomes a collection after the integration is
  reloaded. Supported images are JPG/JPEG, PNG, WebP and GIF.
- Private images are exposed in both Portrait and Landscape playlists so that
  artwork is not filtered out merely because its aspect ratio differs from the
  tablet.
- Existing thumbnails and Commons streaming remain in place.

Built-in streaming collections currently include:

- Birds · Inky Bird Frame
- Mammal illustrations · Joseph Smit
- Mammals · Featured photography
- Night sky · Featured astronomy
- Aurora · Featured pictures
- Galaxies · Featured pictures
- Zoo art & posters · Wikimedia Commons

## Kiosk Satellite

For a portrait kiosk, select:

`media-source://nature_frame/active/portrait`

For a landscape kiosk, select:

`media-source://nature_frame/active/landscape`

Then enable **Shuffle** in Kiosk Satellite and use the Nature Frame collection
switches in Home Assistant to decide which collections participate.

For artwork and posters, set Kiosk Satellite's **Fill the screen** option to
**Smart**. Smart mode fills images that are close to the panel aspect ratio and
keeps strongly mismatched portrait/square images intact over an enlarged,
blurred background. This avoids clipping without black bars.

## Private collections / own images

Create one folder per private collection below:

`/media/nature-frame/private/`

Examples:

- `/media/nature-frame/private/Zoo private/`
- `/media/nature-frame/private/Family art/`
- `/media/nature-frame/private/Own posters/`

Upload or copy images into those folders using Home Assistant's normal local
media/file tools. Reload the Nature Frame integration after creating a new
first-level collection so its switch is created. Adding or replacing images
inside an existing collection is picked up when the Media Source is browsed
again.

Private images are served from Home Assistant local media and are never added
to this public GitHub repository.

## Copyright

Only freely licensed/publicly reusable sources should be built into the public
integration. Copyrighted posters or scans that the household is entitled to use
should stay in a private/local collection and must not be redistributed through
this public repository.
