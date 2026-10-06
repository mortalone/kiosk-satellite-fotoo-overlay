// SPDX-License-Identifier: MIT
package me.jxl.kiosk.plugins.quickactionsoverlay;

final class BatteryLevel {
    private BatteryLevel() {}

    static int fillColor(int level, boolean colored, int textColor) {
        if (!colored || level < 0) return textColor;
        return level <= 20 ? 0xFFEF4444 : level <= 50 ? 0xFFFACC15 : 0xFF22C55E;
    }

    static boolean isBattery(String deviceClass, String icon) {
        return "battery".equalsIgnoreCase(deviceClass) ||
                (icon != null && icon.toLowerCase(java.util.Locale.ROOT).startsWith("mdi:battery"));
    }

    static int parse(String state) {
        if (state == null) return -1;
        try {
            double value = Double.parseDouble(state.trim().replace(',', '.'));
            if (Double.isNaN(value) || Double.isInfinite(value)) return -1;
            return (int) Math.round(Math.max(0.0, Math.min(100.0, value)));
        } catch (NumberFormatException ignored) {
            return -1;
        }
    }
}
