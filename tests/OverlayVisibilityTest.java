package me.jxl.kiosk.plugins.quickactionsoverlay;

public final class OverlayVisibilityTest {
    private static void check(boolean value) { if (!value) throw new AssertionError(); }
    public static void main(String[] args) {
        check(OverlayVisibility.surface(true,false,false,false,false)==OverlayVisibility.DASHBOARD);
        check(OverlayVisibility.surface(false,false,false,false,false)==OverlayVisibility.HIDDEN);
        check(OverlayVisibility.surface(true,false,true,false,false)==OverlayVisibility.KIOSK);
        check(OverlayVisibility.surface(true,false,true,true,false)==OverlayVisibility.HIDDEN);
        check(OverlayVisibility.surface(false,true,false,false,false)==OverlayVisibility.FOTOO);
        check(OverlayVisibility.surface(true,true,true,false,true)==OverlayVisibility.PARTY);
        check(!OverlayVisibility.visible(OverlayVisibility.PARTY,true,true,true,false));
        check(OverlayVisibility.visible(OverlayVisibility.PARTY,false,false,false,true));
        check(!OverlayVisibility.visible(OverlayVisibility.HIDDEN,true,true,true,true));
        check(OverlayVisibility.visible(OverlayVisibility.DASHBOARD,true,false,false,false));
        check(!OverlayVisibility.visible(OverlayVisibility.DASHBOARD,false,true,true,false));
        check(OverlayVisibility.visible(OverlayVisibility.KIOSK,false,true,false,false));
        check(OverlayVisibility.visible(OverlayVisibility.FOTOO,false,false,true,false));
        System.out.println("13 foreground, screensaver, Fotoo and Party visibility checks passed");
    }
}
