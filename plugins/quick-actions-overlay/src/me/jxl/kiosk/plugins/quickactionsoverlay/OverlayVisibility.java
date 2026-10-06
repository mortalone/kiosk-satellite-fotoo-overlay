// SPDX-License-Identifier: MIT
package me.jxl.kiosk.plugins.quickactionsoverlay;

/** Shared, testable rules for the action rail and the independent clock. */
final class OverlayVisibility {
    static final int HIDDEN = 0, DASHBOARD = 1, KIOSK = 2, FOTOO = 3, PARTY = 4;

    static int surface(boolean foreground, boolean dreaming, boolean screensaver,
                       boolean blank, boolean party) {
        if (foreground && party) return PARTY;
        if (dreaming) return FOTOO;
        if (!foreground) return HIDDEN;
        if (screensaver) return blank ? HIDDEN : KIOSK;
        return DASHBOARD;
    }

    static boolean visible(int surface, boolean dashboard, boolean kiosk,
                           boolean fotoo, boolean party) {
        return surface == DASHBOARD ? dashboard : surface == KIOSK ? kiosk
            : surface == FOTOO ? fotoo : surface == PARTY && party;
    }
}
