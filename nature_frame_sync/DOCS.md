# Nature Frame Sync

## Lager
Originale Inky Bird Frame portrait-PNG'er fylder ca. 526 MB. Version 0.2.0 optimerer som standard til JPEG og beholder ikke de hentede PNG-filer permanent.

## Skærmretning
- portrait → upstream portrait.png
- landscape → upstream display.png
- both → begge

## Lovelace
Companion-integrationen opretter `select.nature_frame_gallery`. Kiosk Satellite peger permanent på `nature-frame/active/portrait` på den lodrette skærm.

Fremtidige gallerier som night-sky, mammals og nature bliver separate collections og kan aktiveres individuelt.
