package me.jxl.kiosk.plugins.quickactionsoverlay;

public final class BatteryLevelTest {
    public static void main(String[] args) {
        check(BatteryLevel.isBattery("battery", ""), "battery device class");
        check(BatteryLevel.isBattery("", "mdi:battery-30"), "battery icon");
        check(!BatteryLevel.isBattery("", "mdi:percent"), "other percentage sensor");
        check(BatteryLevel.parse("0") == 0, "empty battery");
        check(BatteryLevel.parse("100") == 100, "full battery");
        check(BatteryLevel.parse("49,6") == 50, "decimal comma");
        check(BatteryLevel.parse("-8") == 0, "lower clamp");
        check(BatteryLevel.parse("180") == 100, "upper clamp");
        check(BatteryLevel.fillColor(10, false, 0xFF123456) == 0xFF123456, "text color at low level");
        check(BatteryLevel.fillColor(90, false, 0xFF123456) == 0xFF123456, "text color at high level");
        check(BatteryLevel.fillColor(-1, true, 0xFF123456) == 0xFF123456, "unknown uses text color");
        check(BatteryLevel.fillColor(20, true, 0) == 0xFFEF4444, "red boundary");
        check(BatteryLevel.fillColor(50, true, 0) == 0xFFFACC15, "yellow boundary");
        check(BatteryLevel.fillColor(51, true, 0) == 0xFF22C55E, "green boundary");
        for (String state : new String[] {null, "", "unknown", "unavailable", "NaN", "Infinity", "-Infinity"}) {
            check(BatteryLevel.parse(state) == -1, "unknown battery: " + state);
        }
        System.out.println("Battery level checks passed");
    }

    private static void check(boolean ok, String message) {
        if (!ok) throw new AssertionError(message);
    }
}
