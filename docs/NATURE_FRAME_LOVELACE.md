# Nature Frame Lovelace collection card

Nature Frame 0.7.1 exposes a representative thumbnail as the
`entity_picture` of every collection switch. Home Assistant's built-in
Picture Entity card can therefore be used without Mushroom, button-card or
card-mod.

Create one grid per Nature Frame screen profile. For a profile named
**Køkken tablet**, new entities are suggested with IDs like these:

```yaml
type: grid
columns: 2
square: false
cards:
  - type: picture-entity
    entity: switch.nature_frame_kokken_tablet_birds_inky_bird_frame
    show_entity_picture: true
    show_name: true
    show_state: true
    aspect_ratio: "4:3"
    fit_mode: cover
    tap_action:
      action: toggle
    hold_action:
      action: more-info
    state_filter:
      "off": grayscale(100%) brightness(55%)
      "on": brightness(105%) saturate(1.1)

  - type: picture-entity
    entity: switch.nature_frame_kokken_tablet_zoo_public_swainson
    show_entity_picture: true
    show_name: true
    show_state: true
    aspect_ratio: "4:3"
    fit_mode: cover
    tap_action:
      action: toggle
    hold_action:
      action: more-info
    state_filter:
      "off": grayscale(100%) brightness(55%)
      "on": brightness(105%) saturate(1.1)

  - type: picture-entity
    entity: switch.nature_frame_kokken_tablet_zoo_private
    show_entity_picture: true
    show_name: true
    show_state: true
    aspect_ratio: "4:3"
    fit_mode: cover
    tap_action:
      action: toggle
    hold_action:
      action: more-info
    state_filter:
      "off": grayscale(100%) brightness(55%)
      "on": brightness(105%) saturate(1.1)

  - type: picture-entity
    entity: switch.nature_frame_kokken_tablet_kitchen_usda_pomological_watercolors
    show_entity_picture: true
    show_name: true
    show_state: true
    aspect_ratio: "4:3"
    fit_mode: cover
    tap_action:
      action: toggle
    hold_action:
      action: more-info
    state_filter:
      "off": grayscale(100%) brightness(55%)
      "on": brightness(105%) saturate(1.1)

  - type: picture-entity
    entity: switch.nature_frame_kokken_tablet_kitchen_kohler_botanical_plates
    show_entity_picture: true
    show_name: true
    show_state: true
    aspect_ratio: "4:3"
    fit_mode: cover
    tap_action:
      action: toggle
    hold_action:
      action: more-info
    state_filter:
      "off": grayscale(100%) brightness(55%)
      "on": brightness(105%) saturate(1.1)

  - type: picture-entity
    entity: switch.nature_frame_kokken_tablet_kitchen_mrs_beeton_plates
    show_entity_picture: true
    show_name: true
    show_state: true
    aspect_ratio: "4:3"
    fit_mode: cover
    tap_action:
      action: toggle
    hold_action:
      action: more-info
    state_filter:
      "off": grayscale(100%) brightness(55%)
      "on": brightness(105%) saturate(1.1)

  - type: picture-entity
    entity: switch.nature_frame_kokken_tablet_kitchen_mixed
    show_entity_picture: true
    show_name: true
    show_state: true
    aspect_ratio: "4:3"
    fit_mode: cover
    tap_action:
      action: toggle
    hold_action:
      action: more-info
    state_filter:
      "off": grayscale(100%) brightness(55%)
      "on": brightness(105%) saturate(1.1)

  - type: picture-entity
    entity: switch.nature_frame_kokken_tablet_art_misc_curated
    show_entity_picture: true
    show_name: true
    show_state: true
    aspect_ratio: "4:3"
    fit_mode: cover
    tap_action:
      action: toggle
    hold_action:
      action: more-info
    state_filter:
      "off": grayscale(100%) brightness(55%)
      "on": brightness(105%) saturate(1.1)
```

Existing entities keep their existing entity IDs. If a copied example does not
match, open the Nature Frame device for that profile in Home Assistant and copy
the actual switch entity ID.

Each switch also exposes the attributes `profile`, `gallery_key`,
`image_count`, `source`, `private` and `virtual`.
