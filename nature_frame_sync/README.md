# Nature Frame Sync

Synkroniserer kuraterede naturillustrationer til Home Assistants `/media`-mappe til Kiosk Satellite.

## Lagerforbrug

Inky Bird Frames originale portrait-PNG'er fylder ca. 526 MB. Fra 0.2.0 er **Optimize images** slået til som standard: billedet hentes, konverteres til JPEG og den store PNG-download kasseres igen.

- `optimize_images: true`
- `jpeg_quality: 88`
- `max_long_edge: 1600`

Der gemmes kun de samlinger, som er aktiveret. Fremtidige gallerier får egne toggles.

## Mapper

- `/media/nature-frame/birds/portrait`
- `/media/nature-frame/birds/landscape`
- `/media/nature-frame/active/portrait`
- `/media/nature-frame/active/landscape`

Companion-integrationen styrer `active` fra Lovelace via `select.nature_frame_gallery`.
