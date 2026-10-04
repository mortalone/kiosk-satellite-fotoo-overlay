## Screensaver Overlay 0.11.2

### Now Playing reliability

The Home Assistant media_player selected in **Now Playing entity** is now the
authoritative source for whether playback is playing, paused or idle.

Previously, if the same Kiosk Satellite device also had a Music Assistant /
Sendspin player configured, the plugin could successfully read that *different*
MA player's queue and then suppress the selected Home Assistant speaker. This
could make Now Playing disappear completely on Kiosk Satellite's own
screensaver.

Music Assistant remains useful, but is now metadata enrichment only: artwork,
title, album and queue details can supplement the selected Home Assistant
media_player without replacing its playback state.

### Layout controls

Now Playing gains:

- **Position: Top / Center / Bottom**
- **Width: 30–100% of the screen**
- the existing edge offset remains available for Top/Bottom

For a Raspberry Pi touchscreen with clock/weather/battery widgets, a useful
starting point is **Center + 55–65% width**.

Saving settings rebuilds the overlay immediately so position/width changes take
effect without restarting the kiosk.

The optional playlist-name entity field was removed from the settings UI to
remain within Kiosk Satellite SDK 1's 20-setting limit. Playlist/source display
still works from the selected media_player and Music Assistant metadata.

## Nature Frame

No Nature Frame code changes in this release.
