// SPDX-License-Identifier: MIT
package me.jxl.kiosk.plugins.fotoooverlay;

import android.app.Application;
import android.content.Context;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.util.DisplayMetrics;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.widget.TextView;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Map;

import me.jxl.kiosk.plugins.KioskPlugin;
import me.jxl.kiosk.plugins.PluginHost;

public final class FotooOverlayPlugin implements KioskPlugin {
    private PluginHost host;
    private Map<String, Object> settings;
    private Context context;
    private WindowManager windowManager;
    private View overlayView;
    private final Handler main = new Handler(Looper.getMainLooper());

    @Override
    public synchronized void start(PluginHost host, Map<String, Object> settings) throws Exception {
        this.host = host;
        this.settings = settings;
        this.context = applicationContext(host);
        if (context == null) {
            host.status("Could not obtain Android application context.", true);
            return;
        }
        this.windowManager = (WindowManager) context.getSystemService(Context.WINDOW_SERVICE);
        if (Build.VERSION.SDK_INT >= 23 && !Settings.canDrawOverlays(context)) {
            host.status("Display over other apps is not granted to Kiosk Satellite.", true);
            return;
        }
        host.status("Ready. Let Android start Fotoo and verify the test card stays visible.", false);
        if (Boolean.TRUE.equals(settings.get("showOnStart"))) show();
    }

    @Override
    public synchronized void configure(Map<String, Object> settings) {
        this.settings = settings;
        if (overlayView != null) {
            hide();
            if (Boolean.TRUE.equals(settings.get("showOnStart"))) show();
        }
    }

    @Override
    public synchronized void execute(String command, Map<String, Object> arguments) {
        if ("show".equals(command)) show();
        else if ("hide".equals(command)) hide();
        else throw new IllegalArgumentException("Unknown command: " + command);
    }

    @Override
    public void onEvent(String event, Map<String, Object> payload) {}

    @Override
    public synchronized void stop() {
        hide();
        host = null;
        context = null;
        windowManager = null;
        settings = null;
    }

    private void show() {
        final Context ctx = context;
        final WindowManager wm = windowManager;
        final PluginHost h = host;
        if (ctx == null || wm == null || h == null) return;

        main.post(() -> {
            synchronized (FotooOverlayPlugin.this) {
                if (overlayView != null || context == null || windowManager == null) return;
                try {
                    TextView card = new TextView(ctx);
                    String message = settings == null ? null : String.valueOf(settings.get("message"));
                    if (message == null || "null".equals(message) || message.trim().isEmpty()) {
                        message = "KS native overlay test";
                    }
                    card.setText(message);
                    card.setTextColor(Color.WHITE);
                    card.setTextSize(18f);
                    int pad = dp(ctx, 18);
                    card.setPadding(pad, pad, pad, pad);

                    GradientDrawable background = new GradientDrawable();
                    background.setColor(0xE6202124);
                    background.setCornerRadius(dp(ctx, 18));
                    card.setBackground(background);

                    DisplayMetrics dm = ctx.getResources().getDisplayMetrics();
                    int width = Math.min(dp(ctx, 560), Math.max(dp(ctx, 220), dm.widthPixels - dp(ctx, 32)));

                    WindowManager.LayoutParams params = new WindowManager.LayoutParams(
                            width,
                            ViewGroup.LayoutParams.WRAP_CONTENT,
                            overlayWindowType(),
                            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                                    | WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL
                                    | WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE
                                    | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
                            PixelFormat.TRANSLUCENT
                    );
                    params.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL;
                    params.y = dp(ctx, 36);

                    wm.addView(card, params);
                    overlayView = card;
                    h.status("System overlay is visible.", false);
                } catch (Throwable error) {
                    h.status("System overlay failed: " + safeMessage(error), true);
                }
            }
        });
    }

    private void hide() {
        final WindowManager wm = windowManager;
        main.post(() -> {
            synchronized (FotooOverlayPlugin.this) {
                View view = overlayView;
                overlayView = null;
                if (view == null || wm == null) return;
                try { wm.removeViewImmediate(view); } catch (Throwable ignored) {}
            }
        });
    }

    private static int overlayWindowType() {
        return Build.VERSION.SDK_INT >= 26
                ? WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
                : WindowManager.LayoutParams.TYPE_PHONE;
    }

    private static int dp(Context context, int value) {
        return Math.round(value * context.getResources().getDisplayMetrics().density);
    }

    private static String safeMessage(Throwable error) {
        String message = error.getMessage();
        return error.getClass().getSimpleName() + (message == null ? "" : ": " + message);
    }

    private static Context applicationContext(PluginHost host) {
        try {
            Class<?> activityThread = Class.forName("android.app.ActivityThread");
            Method currentApplication = activityThread.getDeclaredMethod("currentApplication");
            currentApplication.setAccessible(true);
            Object value = currentApplication.invoke(null);
            if (value instanceof Application) return ((Application) value).getApplicationContext();
            if (value instanceof Context) return ((Context) value).getApplicationContext();
        } catch (Throwable ignored) {}

        Object current = host;
        for (int depth = 0; current != null && depth < 5; depth++) {
            Class<?> type = current.getClass();
            for (Class<?> c = type; c != null; c = c.getSuperclass()) {
                Field[] fields;
                try { fields = c.getDeclaredFields(); }
                catch (Throwable ignored) { continue; }
                for (Field field : fields) {
                    try {
                        field.setAccessible(true);
                        Object value = field.get(current);
                        if (value instanceof Context) return ((Context) value).getApplicationContext();
                    } catch (Throwable ignored) {}
                }
            }

            Object enclosing = null;
            for (Class<?> c = type; c != null && enclosing == null; c = c.getSuperclass()) {
                try {
                    for (Field field : c.getDeclaredFields()) {
                        if (!field.getName().startsWith("this$")) continue;
                        field.setAccessible(true);
                        Object value = field.get(current);
                        if (value != null && value.getClass().getName().startsWith("me.jxl.")) {
                            enclosing = value;
                            break;
                        }
                    }
                } catch (Throwable ignored) {}
            }
            current = enclosing;
        }
        return null;
    }
}
