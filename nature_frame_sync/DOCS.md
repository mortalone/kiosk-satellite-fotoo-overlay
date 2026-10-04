# Nature Frame Sync

## Formål

Nature Frame Sync lægger naturillustrationer i Home Assistant Media. Det gør det muligt at bruge Kiosk Satellites indbyggede Home Assistant Media-pauseskærm uden Fotoo.

## Første synkronisering

Inky Bird Frame har mange højopløselige PNG-filer. En enkelt retning fylder omkring et halvt GB, så første synkronisering kan tage nogle minutter. Senere kørsler sammenligner GitHub blob-SHA'er og downloader kun nye eller ændrede filer.

## Skærmretning

- **portrait**: bruger upstream `portrait.png` (1200×1600)
- **landscape**: bruger upstream `display.png` (1600×1200)
- **both**: henter begge

På den lodrette vægskærm vælges `portrait`. Hvis en anden kiosk er vandret, kan `both` bruges, hvorefter hver kiosk vælger sin egen mappe.

## Placering i Home Assistant

Billederne lander i:

```text
/media/nature-frame/
  birds/
    portrait/
    landscape/
```

I Kiosk Satellite vælges **Screensaver → Home Assistant Media → Media source** og den ønskede mappe.

## Opdateringer og fejl

Add-on'en checker upstream efter det valgte antal timer. Uændrede billeder røres ikke. Hvis GitHub eller netværket er utilgængeligt, beholdes eksisterende billeder, og synkroniseringen prøves igen ved næste interval.

## Kilde og licens

Fuglebillederne hentes direkte fra `veteranbv/inky-bird-frame` og pakkes ikke ind i denne add-on. Kildematerialet er underlagt upstream-projektets egne licens- og provenancevilkår.
