# Nature Frame Sync

## Formål

Nature Frame Sync lægger naturillustrationer i Home Assistant Media. Det gør det muligt at bruge Kiosk Satellites indbyggede Home Assistant Media-pauseskærm uden Fotoo.

## Første synkronisering

Inky Bird Frame har mange højopløselige PNG-filer. En enkelt retning fylder omkring et halvt GB, så første synkronisering kan tage nogle minutter. Senere kørsler sammenligner GitHub blob-SHA'er og downloader kun nye eller ændrede filer.

## Skærmretning

- **portrait**: bruger upstream `portrait.png` (1200×1600)
- **landscape**: bruger upstream `display.png` (1600×1200)
- **both**: henter begge

På den lodrette vægskærm vælges `portrait`.

## Placering i Home Assistant

Kildesamlinger lander i:

```text
/media/nature-frame/
  birds/
    portrait/
    landscape/
```

Companion-integrationen **Nature Frame** kan derefter styre det aktive galleri fra Lovelace og bygger:

```text
/media/nature-frame/active/
  portrait/
  landscape/
```

Kiosk Satellite skal pege på `nature-frame/active/portrait` på en lodret skærm.

## Lovelace-styring

Installer companion-integrationen fra samme repository via HACS. Den opretter:

`select.nature_frame_gallery`

Det er denne entity, der bruges som dropdown/tile på Lovelace. Et galleri-skift ændrer active-mappen uden at kopiere hele billedsamlingen.

## Opdateringer og fejl

Add-on'en checker upstream efter det valgte antal timer. Uændrede billeder røres ikke. Hvis GitHub eller netværket er utilgængeligt, beholdes eksisterende billeder, og synkroniseringen prøves igen ved næste interval.

## Kilde og licens

Fuglebillederne hentes direkte fra `veteranbv/inky-bird-frame` og pakkes ikke ind i denne add-on. Kildematerialet er underlagt upstream-projektets egne licens- og provenancevilkår.
