## Screensaver Overlay Suite 0.11.7

### Quick Actions & Clock 0.2.0

One action configuration can now appear over the normal Kiosk Lovelace dashboard,
Kiosk screensavers and Fotoo. Enable **Quick actions on dashboard** to reuse the
same buttons. For a compact row, select Horizontal and disable **Show names and
states**. Party Mode hides actions by default.

An optional clock/date has independent dashboard, Kiosk screensaver and Fotoo
visibility, size and position. It is always hidden in Party Mode. All new display
options start off; retain Kiosk's existing clock or enable this one, avoiding a
duplicate clock on the screensaver.

New Fotoo launch/attach and Wall Art commands support the updated HA chooser,
apply script and toggle script in `examples/screensaver-mode-package.yaml`.
Existing combined/Now Playing Fotoo launchers are preferred when installed.
Expose plugin commands as HA buttons. See `PLUGINS.md` for setup.

### Nature Frame 0.8.2

Fixes private gallery covers by signing local media preview URLs. Signatures are
cached and renewed so frequent catalogue updates do not reload images. Update
through HACS, restart HA and refresh Lovelace.

### Packages and checks

Install `quick-actions-overlay-0.2.0.zip` in Kiosk Satellite's Plugin Manager.
The compatibility plugin and other standalone plugins remain available.
Includes automated visibility checks and five private cover/signature tests.
Android compilation and D8 packaging run for all plugin packages.
