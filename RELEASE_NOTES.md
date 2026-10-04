## Screensaver Overlay 0.10.9

Packaging release. Overlay behavior is unchanged.

## Nature Frame 0.7.5

This fixes private collections such as **Zoo · Private** not appearing in the
Lovelace gallery selector after files are added.

Nature Frame now rescans private collection folders automatically and the switch
entities expose live `entity_picture` and `image_count` values instead of
keeping the values from Home Assistant startup.

There is no collection-count limit involved.

After updating, adding images to an existing private collection should make it
appear automatically in an Auto-Entities selector that filters on
`image_count > 0`.
