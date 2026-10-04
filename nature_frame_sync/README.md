# Nature Frame Sync

Synkroniserer kuraterede naturillustrationer til Home Assistants `/media`-mappe, så de kan bruges direkte af f.eks. Kiosk Satellite **Home Assistant Media**-pauseskærmen.

Første provider er [Inky Bird Frame](https://github.com/veteranbv/inky-bird-frame). Add-on'en downloader ikke hele upstream-repositoryet; den finder kun de relevante godkendte `portrait.png`/`display.png`-filer og springer uændrede billeder over ved senere synkroniseringer.

## Mapper

- `/media/nature-frame/birds/portrait` – Inky `portrait.png`, 1200×1600
- `/media/nature-frame/birds/landscape` – Inky `display.png`, 1600×1200

Vælg den mappe, der passer til skærmens retning. `orientation: both` henter begge varianter.

## Indstillinger

- **inky_birds** – synkronisér Inky Bird Frame.
- **orientation** – `portrait`, `landscape` eller `both`.
- **update_interval_hours** – hvor ofte upstream kontrolleres.
- **delete_removed** – fjern lokale billeder, der er fjernet fra upstream, i den/de retninger der synkroniseres.

## Kiosk Satellite

Vælg **Screensaver → Home Assistant Media** og vælg f.eks. `nature-frame/birds/portrait`. Slå Shuffle til, og vælg det ønskede interval/transition.

## Andre dyr

Koden bruger en provider-struktur, så flere kuraterede samlinger kan tilføjes senere uden at ændre mappestrukturen. Pattedyr, insekter, krybdyr osv. får deres egne mapper under `/media/nature-frame/`.
