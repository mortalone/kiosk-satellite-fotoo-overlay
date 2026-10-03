// SPDX-License-Identifier: MIT
package me.jxl.kiosk.plugins.fotoooverlay;

import android.app.Application;
import android.app.AppOpsManager;
import android.app.usage.UsageEvents;
import android.app.usage.UsageStats;
import android.app.usage.UsageStatsManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.os.Process;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.io.InputStream;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLConnection;
import java.util.Collections;
import java.util.HashSet;
import java.util.Map;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import me.jxl.kiosk.plugins.KioskPlugin;
import me.jxl.kiosk.plugins.PluginHost;

/**
 * Native Android overlays shown while Fotoo is active, either as Android\n * DreamService/screensaver or as the foreground Fotoo app.
 *
 * The public KS SDK does not currently expose an Android Context. This plugin
 * therefore obtains the application Context with a small reflection fallback.
 * Everything that depends on that workaround is isolated in applicationContext().
 */
public final class FotooOverlayPlugin implements KioskPlugin {
    private PluginHost host;
    private Map<String, Object> settings;
    private Context context;
    private WindowManager windowManager;

    private final Handler main = new Handler(Looper.getMainLooper());
    private ExecutorService io;
    private static final String FOTOO_PACKAGE = "com.bo.fotoo";
    private BroadcastReceiver dreamReceiver;
    private boolean dreaming;
    private boolean fotooForeground;
    private String lastForegroundPackage = "";
    private long usageCursor;

    private final Set<String> subscribedEntities = new HashSet<>();
    private String nowPlayingEntity = "";
    private String doorbellEntity = "";
    private String doorbellCameraEntity = "";
    private boolean showPaused = true;
    private String nowPlayingPosition = "Bottom";
    private int doorbellSeconds = 20;

    private String haBaseUrl;
    private String mediaState;
    private Map<?, ?> mediaAttributes = Collections.emptyMap();
    private Map<?, ?> cameraAttributes = Collections.emptyMap();
    private String lastDoorbellState;
    private boolean doorbellInitialSeen;

    private View nowPlayingView;
    private ImageView mediaImage;
    private TextView mediaTitle;
    private TextView mediaArtist;
    private TextView mediaAlbum;
    private String loadedMediaPicture;
    private boolean mediaFetchPending;

    private View doorbellView;
    private ImageView doorbellImage;
    private boolean cameraFetchPending;

    private final Runnable foregroundProbeTask = new Runnable() {
        @Override public void run() {
            if (context == null) return;
            boolean next = isFotooForeground();
            if (next != fotooForeground) {
                fotooForeground = next;
                updatePresentation();
            }
            main.postDelayed(this, 1000);
        }
    };

    private final Runnable hideDoorbellTask = new Runnable() {
        @Override public void run() {
            hideDoorbell();
            updateNowPlaying();
        }
    };

    private final Runnable cameraRefreshTask = new Runnable() {
        @Override public void run() {
            if (doorbellView == null || !fotooActive()) return;
            refreshDoorbellImage();
            main.postDelayed(this, 1000);
        }
    };

    @Override
    public synchronized void start(PluginHost host, Map<String, Object> settings) {
        this.host = host;
        this.settings = settings;
        this.context = applicationContext(host);
        if (context == null) {
            host.status("Could not obtain Android application context.", true);
            return;
        }
        this.windowManager = (WindowManager) context.getSystemService(Context.WINDOW_SERVICE);
        if (Build.VERSION.SDK_INT >= 23 && !Settings.canDrawOverlays(context)) {
            host.status("Grant Display over other apps to Kiosk Satellite.", true);
            return;
        }

        io = Executors.newSingleThreadExecutor(task -> {
            Thread thread = new Thread(task, "fotoo-overlay-images");
            thread.setDaemon(true);
            return thread;
        });

        registerDreamReceiver();
        applySettings(settings);
        readHomeAssistantBaseUrl();
        main.post(foregroundProbeTask);
        host.status(hasUsageAccess()
                ? "Ready. Fotoo is detected as DreamService or foreground app."
                : "Ready for Fotoo DreamService. Grant Usage access to Kiosk Satellite to also detect Fotoo launched as an app.",
                false);
    }

    @Override
    public synchronized void configure(Map<String, Object> settings) {
        this.settings = settings;
        if (host != null) applySettings(settings);
    }

    @Override
    public synchronized void execute(String command, Map<String, Object> arguments) {
        if ("test".equals(command)) {
            showTestOverlay();
        } else if ("hide".equals(command)) {
            main.post(() -> {
                hideDoorbell();
                hideNowPlaying();
            });
        } else {
            throw new IllegalArgumentException("Unknown command: " + command);
        }
    }

    @Override
    public synchronized void onEvent(String event, Map<String, Object> payload) {
        if (!event.startsWith("ks.ha.entity.")) return;
        Object idValue = payload.get("entityId");
        String entityId = idValue == null ? event.substring("ks.ha.entity.".length()) : String.valueOf(idValue);
        String state = payload.get("state") == null ? null : String.valueOf(payload.get("state"));
        Object attrsValue = payload.get("attributes");
        Map<?, ?> attrs = attrsValue instanceof Map ? (Map<?, ?>) attrsValue : Collections.emptyMap();

        if (entityId.equals(nowPlayingEntity)) {
            mediaState = state;
            mediaAttributes = attrs;
            main.post(this::updateNowPlaying);
        }

        if (entityId.equals(doorbellCameraEntity)) {
            cameraAttributes = attrs;
            if (doorbellView != null) main.post(this::refreshDoorbellImage);
        }

        if (entityId.equals(doorbellEntity)) {
            boolean trigger = false;
            if (!doorbellInitialSeen) {
                doorbellInitialSeen = true;
            } else if (doorbellEntity.startsWith("event.")) {
                trigger = !Objects.equals(lastDoorbellState, state);
            } else {
                trigger = "on".equalsIgnoreCase(state) && !"on".equalsIgnoreCase(lastDoorbellState);
            }
            lastDoorbellState = state;
            if (trigger && fotooActive()) main.post(this::showDoorbell);
        }
    }

    @Override
    public synchronized void stop() {
        if (context != null && dreamReceiver != null) {
            try { context.unregisterReceiver(dreamReceiver); } catch (Throwable ignored) {}
        }
        dreamReceiver = null;
        main.removeCallbacksAndMessages(null);
        hideDoorbellImmediate();
        hideNowPlayingImmediate();
        if (io != null) {
            io.shutdownNow();
            io = null;
        }
        subscribedEntities.clear();
        host = null;
        settings = null;
        context = null;
        windowManager = null;
    }

    private void registerDreamReceiver() {
        dreamReceiver = new BroadcastReceiver() {
            @Override public void onReceive(Context ignored, Intent intent) {
                String action = intent.getAction();
                if (Intent.ACTION_DREAMING_STARTED.equals(action)) {
                    dreaming = true;
                    updatePresentation();
                } else if (Intent.ACTION_DREAMING_STOPPED.equals(action)) {
                    dreaming = false;
                    updatePresentation();
                }
            }
        };
        IntentFilter filter = new IntentFilter();
        filter.addAction(Intent.ACTION_DREAMING_STARTED);
        filter.addAction(Intent.ACTION_DREAMING_STOPPED);
        if (Build.VERSION.SDK_INT >= 33) {
            context.registerReceiver(dreamReceiver, filter, Context.RECEIVER_EXPORTED);
        } else {
            context.registerReceiver(dreamReceiver, filter);
        }
    }

    private void applySettings(Map<String, Object> values) {
        String nextNow = stringSetting(values, "nowPlayingEntity");
        String nextDoorbell = stringSetting(values, "doorbellEntity");
        String nextCamera = stringSetting(values, "doorbellCameraEntity");

        Set<String> wanted = new HashSet<>();
        if (!nextNow.isEmpty()) wanted.add(nextNow);
        if (!nextDoorbell.isEmpty()) wanted.add(nextDoorbell);
        if (!nextCamera.isEmpty()) wanted.add(nextCamera);

        for (String old : new HashSet<>(subscribedEntities)) {
            if (!wanted.contains(old)) {
                try { host.unsubscribe("ha.entity." + old); } catch (Throwable ignored) {}
                subscribedEntities.remove(old);
            }
        }
        for (String entity : wanted) {
            if (subscribedEntities.add(entity)) host.subscribe("ha.entity." + entity);
        }

        nowPlayingEntity = nextNow;
        doorbellEntity = nextDoorbell;
        doorbellCameraEntity = nextCamera;
        showPaused = Boolean.TRUE.equals(values.get("showPaused"));
        nowPlayingPosition = "Top".equals(values.get("nowPlayingPosition")) ? "Top" : "Bottom";
        Object seconds = values.get("doorbellSeconds");
        doorbellSeconds = seconds instanceof Number ? Math.max(5, Math.min(60, ((Number) seconds).intValue())) : 20;

        doorbellInitialSeen = false;
        lastDoorbellState = null;
        loadedMediaPicture = null;
        main.post(this::updateNowPlaying);
    }

    private void readHomeAssistantBaseUrl() {
        host.executeCommand("getDashboardState", Collections.emptyMap(), (ok, data, error) -> {
            if (!ok || !(data instanceof Map)) return;
            Object value = ((Map<?, ?>) data).get("homeAssistantUrl");
            if (value != null) haBaseUrl = String.valueOf(value);
            main.post(this::updateNowPlaying);
        });
    }

    private boolean fotooActive() {
        return dreaming || fotooForeground;
    }

    private void updatePresentation() {
        if (!fotooActive()) {
            hideDoorbell();
            hideNowPlaying();
            return;
        }
        updateNowPlaying();
    }

    private boolean hasUsageAccess() {
        if (context == null || Build.VERSION.SDK_INT < 21) return true;
        try {
            AppOpsManager appOps = (AppOpsManager) context.getSystemService(Context.APP_OPS_SERVICE);
            int mode = appOps.checkOpNoThrow(
                    AppOpsManager.OPSTR_GET_USAGE_STATS,
                    Process.myUid(),
                    context.getPackageName());
            return mode == AppOpsManager.MODE_ALLOWED;
        } catch (Throwable ignored) {
            return false;
        }
    }

    private boolean isFotooForeground() {
        if (context == null || !hasUsageAccess()) return false;
        try {
            UsageStatsManager manager =
                    (UsageStatsManager) context.getSystemService(Context.USAGE_STATS_SERVICE);
            if (manager == null) return false;

            long now = System.currentTimeMillis();
            long from = usageCursor == 0 ? now - 5 * 60_000L : Math.max(0, usageCursor - 1000L);
            UsageEvents events = manager.queryEvents(from, now);
            UsageEvents.Event event = new UsageEvents.Event();
            long newest = usageCursor;
            while (events != null && events.hasNextEvent()) {
                events.getNextEvent(event);
                int type = event.getEventType();
                if ((type == UsageEvents.Event.ACTIVITY_RESUMED
                        || type == UsageEvents.Event.MOVE_TO_FOREGROUND)
                        && event.getTimeStamp() >= newest) {
                    newest = event.getTimeStamp();
                    lastForegroundPackage = event.getPackageName();
                }
            }

            // If the plugin starts after Fotoo was already opened and the
            // event window contained nothing, seed the last package from the
            // most recently used app. Subsequent probes use UsageEvents.
            if (usageCursor == 0 && lastForegroundPackage.isEmpty()) {
                List<UsageStats> stats = manager.queryUsageStats(
                        UsageStatsManager.INTERVAL_DAILY, now - 24 * 60 * 60_000L, now);
                long lastUsed = 0;
                if (stats != null) {
                    for (UsageStats stat : stats) {
                        if (stat.getLastTimeUsed() >= lastUsed) {
                            lastUsed = stat.getLastTimeUsed();
                            lastForegroundPackage = stat.getPackageName();
                        }
                    }
                }
            }
            usageCursor = Math.max(newest, now - 1000L);
            return FOTOO_PACKAGE.equals(lastForegroundPackage);
        } catch (Throwable ignored) {
            return false;
        }
    }

    private void updateNowPlaying() {
        if (!fotooActive() || doorbellView != null || nowPlayingEntity.isEmpty() || !mediaVisible()) {
            hideNowPlaying();
            return;
        }
        ensureNowPlayingView();

        String title = attr(mediaAttributes, "media_title", "Now Playing");
        String artist = attr(mediaAttributes, "media_artist", "");
        String album = attr(mediaAttributes, "media_album_name", attr(mediaAttributes, "media_album", ""));

        mediaTitle.setText(title);
        mediaArtist.setText(artist);
        mediaArtist.setVisibility(artist.isEmpty() ? View.GONE : View.VISIBLE);
        mediaAlbum.setText(album);
        mediaAlbum.setVisibility(album.isEmpty() ? View.GONE : View.VISIBLE);

        String picture = attr(mediaAttributes, "entity_picture", "");
        if (!picture.equals(loadedMediaPicture)) {
            loadedMediaPicture = picture;
            mediaImage.setImageDrawable(null);
            if (!picture.isEmpty()) fetchMediaImage(picture);
        }
    }

    private boolean mediaVisible() {
        if ("playing".equalsIgnoreCase(mediaState)) return true;
        return showPaused && "paused".equalsIgnoreCase(mediaState);
    }

    private void ensureNowPlayingView() {
        if (nowPlayingView != null || context == null || windowManager == null) return;

        LinearLayout card = new LinearLayout(context);
        card.setOrientation(LinearLayout.HORIZONTAL);
        card.setGravity(Gravity.CENTER_VERTICAL);
        int pad = dp(16);
        card.setPadding(pad, pad, pad, pad);
        card.setBackground(cardBackground(0xE6212226, 20));

        mediaImage = new ImageView(context);
        mediaImage.setScaleType(ImageView.ScaleType.CENTER_CROP);
        LinearLayout.LayoutParams imageParams = new LinearLayout.LayoutParams(dp(118), dp(118));
        imageParams.rightMargin = dp(16);
        card.addView(mediaImage, imageParams);

        LinearLayout text = new LinearLayout(context);
        text.setOrientation(LinearLayout.VERTICAL);
        text.setGravity(Gravity.CENTER_VERTICAL);
        mediaTitle = textView(21, true, Color.WHITE);
        mediaArtist = textView(17, false, 0xFFE7E7E7);
        mediaAlbum = textView(14, false, 0xFFBDBDBD);
        text.addView(mediaTitle);
        text.addView(mediaArtist);
        text.addView(mediaAlbum);
        card.addView(text, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));

        int width = Math.min(dp(700), Math.max(dp(300), context.getResources().getDisplayMetrics().widthPixels - dp(32)));
        WindowManager.LayoutParams params = overlayParams(width, ViewGroup.LayoutParams.WRAP_CONTENT);
        params.gravity = ("Top".equals(nowPlayingPosition) ? Gravity.TOP : Gravity.BOTTOM) | Gravity.CENTER_HORIZONTAL;
        params.y = dp(34);

        try {
            windowManager.addView(card, params);
            nowPlayingView = card;
        } catch (Throwable error) {
            host.status("Now Playing overlay failed: " + safeMessage(error), true);
        }
    }

    private void fetchMediaImage(String path) {
        if (mediaFetchPending || io == null) return;
        String resolved = resolveHaUrl(path);
        if (resolved == null) return;
        mediaFetchPending = true;
        io.execute(() -> {
            Bitmap bitmap = fetchBitmap(resolved, false);
            main.post(() -> {
                mediaFetchPending = false;
                if (bitmap != null && mediaImage != null && path.equals(loadedMediaPicture)) {
                    mediaImage.setImageBitmap(bitmap);
                }
            });
        });
    }

    private void showDoorbell() {
        if (!fotooActive() || context == null || windowManager == null) return;
        hideNowPlaying();
        main.removeCallbacks(hideDoorbellTask);
        main.removeCallbacks(cameraRefreshTask);

        if (doorbellView == null) {
            FrameLayout frame = new FrameLayout(context);
            frame.setBackground(cardBackground(0xF0151517, 22));

            doorbellImage = new ImageView(context);
            doorbellImage.setScaleType(ImageView.ScaleType.CENTER_CROP);
            frame.addView(doorbellImage, new FrameLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));

            TextView label = textView(18, true, Color.WHITE);
            label.setText("Dørklokke");
            label.setPadding(dp(14), dp(10), dp(14), dp(10));
            label.setBackground(cardBackground(0xB0000000, 14));
            FrameLayout.LayoutParams labelParams = new FrameLayout.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
            labelParams.gravity = Gravity.TOP | Gravity.START;
            labelParams.leftMargin = dp(14);
            labelParams.topMargin = dp(14);
            frame.addView(label, labelParams);

            int width = Math.min(dp(780), Math.max(dp(320), context.getResources().getDisplayMetrics().widthPixels - dp(28)));
            int height = Math.min(dp(520), Math.max(dp(260), context.getResources().getDisplayMetrics().heightPixels * 55 / 100));
            WindowManager.LayoutParams params = overlayParams(width, height);
            params.gravity = Gravity.CENTER;

            try {
                windowManager.addView(frame, params);
                doorbellView = frame;
            } catch (Throwable error) {
                host.status("Doorbell overlay failed: " + safeMessage(error), true);
                return;
            }
        }

        refreshDoorbellImage();
        main.post(cameraRefreshTask);
        main.postDelayed(hideDoorbellTask, doorbellSeconds * 1000L);
    }

    private void refreshDoorbellImage() {
        if (cameraFetchPending || doorbellView == null || io == null) return;
        String picture = attr(cameraAttributes, "entity_picture", "");
        String resolved = resolveHaUrl(picture);
        if (resolved == null) return;

        cameraFetchPending = true;
        io.execute(() -> {
            Bitmap bitmap = fetchBitmap(resolved, true);
            main.post(() -> {
                cameraFetchPending = false;
                if (bitmap != null && doorbellImage != null && doorbellView != null) {
                    doorbellImage.setImageBitmap(bitmap);
                }
            });
        });
    }

    private void hideDoorbell() {
        main.removeCallbacks(hideDoorbellTask);
        main.removeCallbacks(cameraRefreshTask);
        hideDoorbellImmediate();
    }

    private void hideDoorbellImmediate() {
        View view = doorbellView;
        doorbellView = null;
        doorbellImage = null;
        cameraFetchPending = false;
        if (view != null && windowManager != null) {
            try { windowManager.removeViewImmediate(view); } catch (Throwable ignored) {}
        }
    }

    private void hideNowPlaying() {
        hideNowPlayingImmediate();
    }

    private void hideNowPlayingImmediate() {
        View view = nowPlayingView;
        nowPlayingView = null;
        mediaImage = null;
        mediaTitle = null;
        mediaArtist = null;
        mediaAlbum = null;
        mediaFetchPending = false;
        if (view != null && windowManager != null) {
            try { windowManager.removeViewImmediate(view); } catch (Throwable ignored) {}
        }
    }

    private void showTestOverlay() {
        if (context == null || windowManager == null) return;
        TextView test = textView(18, true, Color.WHITE);
        test.setText("Fotoo Overlay 0.3 test");
        test.setPadding(dp(18), dp(16), dp(18), dp(16));
        test.setBackground(cardBackground(0xE6212226, 18));
        WindowManager.LayoutParams params = overlayParams(
                Math.min(dp(520), context.getResources().getDisplayMetrics().widthPixels - dp(32)),
                ViewGroup.LayoutParams.WRAP_CONTENT);
        params.gravity = Gravity.CENTER;
        try {
            windowManager.addView(test, params);
            main.postDelayed(() -> {
                try { windowManager.removeViewImmediate(test); } catch (Throwable ignored) {}
            }, 8000);
        } catch (Throwable error) {
            host.status("Test overlay failed: " + safeMessage(error), true);
        }
    }

    private WindowManager.LayoutParams overlayParams(int width, int height) {
        return new WindowManager.LayoutParams(
                width,
                height,
                Build.VERSION.SDK_INT >= 26
                        ? WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
                        : WindowManager.LayoutParams.TYPE_PHONE,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                        | WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL
                        | WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE
                        | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
                PixelFormat.TRANSLUCENT
        );
    }

    private TextView textView(float size, boolean bold, int color) {
        TextView view = new TextView(context);
        view.setTextSize(size);
        view.setTextColor(color);
        if (bold) view.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        return view;
    }

    private GradientDrawable cardBackground(int color, int radiusDp) {
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(color);
        bg.setCornerRadius(dp(radiusDp));
        return bg;
    }

    private Bitmap fetchBitmap(String source, boolean cacheBust) {
        URLConnection connection = null;
        InputStream stream = null;
        try {
            String address = cacheBust
                    ? source + (source.contains("?") ? "&" : "?") + "_ks=" + System.currentTimeMillis()
                    : source;
            connection = new URL(address).openConnection();
            connection.setConnectTimeout(3000);
            connection.setReadTimeout(5000);
            connection.setUseCaches(false);
            if (connection instanceof HttpURLConnection) {
                ((HttpURLConnection) connection).setInstanceFollowRedirects(true);
            }
            stream = connection.getInputStream();
            return BitmapFactory.decodeStream(stream);
        } catch (Throwable ignored) {
            return null;
        } finally {
            try { if (stream != null) stream.close(); } catch (Throwable ignored) {}
            if (connection instanceof HttpURLConnection) ((HttpURLConnection) connection).disconnect();
        }
    }

    private String resolveHaUrl(String path) {
        if (path == null || path.isEmpty()) return null;
        if (path.startsWith("http://") || path.startsWith("https://")) return path;
        if (haBaseUrl == null || haBaseUrl.isEmpty()) return null;
        String base = haBaseUrl.endsWith("/") ? haBaseUrl.substring(0, haBaseUrl.length() - 1) : haBaseUrl;
        return base + (path.startsWith("/") ? path : "/" + path);
    }

    private static String attr(Map<?, ?> attributes, String key, String fallback) {
        Object value = attributes == null ? null : attributes.get(key);
        if (value == null) return fallback;
        String text = String.valueOf(value);
        return "null".equals(text) ? fallback : text;
    }

    private static String stringSetting(Map<String, Object> values, String key) {
        Object value = values.get(key);
        return value == null ? "" : String.valueOf(value).trim();
    }

    private int dp(int value) {
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
                try {
                    for (Field field : c.getDeclaredFields()) {
                        field.setAccessible(true);
                        Object value = field.get(current);
                        if (value instanceof Context) return ((Context) value).getApplicationContext();
                    }
                } catch (Throwable ignored) {}
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
