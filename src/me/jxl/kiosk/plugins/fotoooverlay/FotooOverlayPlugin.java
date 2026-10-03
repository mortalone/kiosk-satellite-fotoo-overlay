// SPDX-License-Identifier: MIT
package me.jxl.kiosk.plugins.fotoooverlay;

import android.app.Application;
import android.app.Activity;
import android.app.ActivityManager;
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
import android.os.Bundle;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;

import java.io.InputStream;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLConnection;
import java.time.Instant;
import java.util.Collections;
import java.util.HashSet;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import me.jxl.kiosk.plugins.KioskPlugin;
import me.jxl.kiosk.plugins.PluginHost;

/**
 * Native Android overlays shown while Fotoo is active. DreamService mode\n * is detected exactly; ordinary-app mode uses the Kiosk Activity leaving\n * the foreground because this AOSP build does not report Fotoo through\n * UsageStats.
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
    private Application application;
    private Application.ActivityLifecycleCallbacks lifecycleCallbacks;
    private boolean dreaming;
    private boolean manualFotoo;
    private boolean inferredFotoo;

    private final Set<String> subscribedEntities = new HashSet<>();
    private String nowPlayingEntity = "";
    private String playlistEntity = "";
    private String nextTrackEntity = "";
    private String doorbellEntity = "";
    private String doorbellEntity2 = "";
    private String doorbellCameraEntity = "";
    private boolean showPaused = true;
    private String nowPlayingPosition = "Bottom";
    private int nowPlayingOffset = 34;
    private int nowPlayingOpacity = 90;
    private boolean showProgress = true;
    private String timeLabels = "Elapsed / remaining";
    private boolean showPlaylist = false;
    private boolean showNextTrack = false;
    private int doorbellSeconds = 20;
    private int cameraOpacity = 100;
    private boolean cameraTestMode = false;

    private String haBaseUrl;
    private String mediaState;
    private Map<?, ?> mediaAttributes = Collections.emptyMap();
    private String playlistState = "";
    private String nextTrackState = "";
    private Map<?, ?> cameraAttributes = Collections.emptyMap();
    private String lastDoorbellState;
    private boolean doorbellInitialSeen;
    private String lastDoorbellState2;
    private boolean doorbellInitialSeen2;

    private View nowPlayingView;
    private ImageView mediaImage;
    private TextView mediaTitle;
    private TextView mediaArtist;
    private TextView mediaAlbum;
    private TextView mediaPlaylist;
    private TextView mediaNext;
    private ProgressBar mediaProgress;
    private TextView mediaTime;
    private String loadedMediaPicture;
    private boolean mediaFetchPending;

    private View doorbellView;
    private ImageView doorbellImage;
    private TextView doorbellLabel;
    private boolean cameraFetchPending;

    private final Runnable progressTickTask = new Runnable() {
        @Override public void run() {
            if (nowPlayingView == null) return;
            updateProgress();
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
        registerActivityLifecycle();
        applySettings(settings);
        readHomeAssistantBaseUrl();
        main.postDelayed(this::detectAlreadyRunningFotoo, 800);
        host.status("Ready. Fotoo DreamService is automatic. Use the 'Open Fotoo with overlay' action for manual app mode.", false);
    }

    @Override
    public synchronized void configure(Map<String, Object> settings) {
        this.settings = settings;
        if (host != null) applySettings(settings);
    }

    @Override
    public synchronized void execute(String command, Map<String, Object> arguments) {
        if ("openFotoo".equals(command)) {
            openFotoo();
        } else if ("test".equals(command)) {
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

        if (!playlistEntity.isEmpty() && entityId.equals(playlistEntity)) {
            playlistState = state == null ? "" : state;
            main.post(this::updateNowPlaying);
        }

        if (!nextTrackEntity.isEmpty() && entityId.equals(nextTrackEntity)) {
            nextTrackState = state == null ? "" : state;
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

        if (entityId.equals(doorbellEntity2)) {
            boolean trigger = false;
            if (!doorbellInitialSeen2) {
                doorbellInitialSeen2 = true;
            } else if (doorbellEntity2.startsWith("event.")) {
                trigger = !Objects.equals(lastDoorbellState2, state);
            } else {
                trigger = "on".equalsIgnoreCase(state) && !"on".equalsIgnoreCase(lastDoorbellState2);
            }
            lastDoorbellState2 = state;
            if (trigger && fotooActive()) main.post(this::showDoorbell);
        }
    }

    @Override
    public synchronized void stop() {
        if (context != null && dreamReceiver != null) {
            try { context.unregisterReceiver(dreamReceiver); } catch (Throwable ignored) {}
        }
        dreamReceiver = null;
        if (application != null && lifecycleCallbacks != null) {
            try { application.unregisterActivityLifecycleCallbacks(lifecycleCallbacks); } catch (Throwable ignored) {}
        }
        lifecycleCallbacks = null;
        application = null;
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

    private void registerActivityLifecycle() {
        Context appContext = context == null ? null : context.getApplicationContext();
        if (!(appContext instanceof Application)) return;
        application = (Application) appContext;
        lifecycleCallbacks = new Application.ActivityLifecycleCallbacks() {
            @Override public void onActivityCreated(Activity activity, Bundle state) {}
            @Override public void onActivityStarted(Activity activity) {}
            @Override public void onActivityResumed(Activity activity) {
                if (!activity.getPackageName().equals(context.getPackageName())) return;
                if (manualFotoo || inferredFotoo) {
                    manualFotoo = false;
                    inferredFotoo = false;
                    updatePresentation();
                }
            }
            @Override public void onActivityPaused(Activity activity) {}
            @Override public void onActivityStopped(Activity activity) {}
            @Override public void onActivitySaveInstanceState(Activity activity, Bundle state) {}
            @Override public void onActivityDestroyed(Activity activity) {}
        };
        application.registerActivityLifecycleCallbacks(lifecycleCallbacks);
    }

    private void detectAlreadyRunningFotoo() {
        if (context == null || dreaming || manualFotoo || inferredFotoo) return;
        try {
            ActivityManager manager =
                    (ActivityManager) context.getSystemService(Context.ACTIVITY_SERVICE);
            if (manager == null) return;
            java.util.List<ActivityManager.RunningAppProcessInfo> processes =
                    manager.getRunningAppProcesses();
            if (processes == null) return;
            for (ActivityManager.RunningAppProcessInfo process : processes) {
                boolean fotoo = FOTOO_PACKAGE.equals(process.processName);
                if (!fotoo && process.pkgList != null) {
                    for (String pkg : process.pkgList) {
                        if (FOTOO_PACKAGE.equals(pkg)) {
                            fotoo = true;
                            break;
                        }
                    }
                }
                if (fotoo && process.importance <= ActivityManager.RunningAppProcessInfo.IMPORTANCE_VISIBLE) {
                    inferredFotoo = true;
                    updatePresentation();
                    host.status("Attached to an already-running Fotoo session.", false);
                    return;
                }
            }
        } catch (Throwable ignored) {
        }
    }

    private void openFotoo() {
        if (context == null) return;
        try {
            Intent launch = context.getPackageManager().getLaunchIntentForPackage(FOTOO_PACKAGE);
            if (launch == null) {
                host.status("Fotoo is not installed or has no launchable activity.", true);
                return;
            }
            manualFotoo = true;
            launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(launch);
            main.postDelayed(this::updatePresentation, 500);
        } catch (Throwable error) {
            manualFotoo = false;
            host.status("Could not open Fotoo: " + safeMessage(error), true);
        }
    }

    private void applySettings(Map<String, Object> values) {
        String nextNow = stringSetting(values, "nowPlayingEntity");
        String nextPlaylistEntity = stringSetting(values, "playlistEntity");
        String nextNextTrackEntity = stringSetting(values, "nextTrackEntity");
        String nextDoorbell = stringSetting(values, "doorbellEntity");
        String nextDoorbell2 = stringSetting(values, "doorbellEntity2");
        String nextCamera = stringSetting(values, "doorbellCameraEntity");

        Set<String> wanted = new HashSet<>();
        if (!nextNow.isEmpty()) wanted.add(nextNow);
        if (!nextPlaylistEntity.isEmpty()) wanted.add(nextPlaylistEntity);
        if (!nextNextTrackEntity.isEmpty()) wanted.add(nextNextTrackEntity);
        if (!nextDoorbell.isEmpty()) wanted.add(nextDoorbell);
        if (!nextDoorbell2.isEmpty()) wanted.add(nextDoorbell2);
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
        playlistEntity = nextPlaylistEntity;
        nextTrackEntity = nextNextTrackEntity;
        doorbellEntity = nextDoorbell;
        doorbellEntity2 = nextDoorbell2;
        doorbellCameraEntity = nextCamera;
        showPaused = Boolean.TRUE.equals(values.get("showPaused"));
        nowPlayingPosition = "Top".equals(values.get("nowPlayingPosition")) ? "Top" : "Bottom";
        Object offset = values.get("nowPlayingOffset");
        nowPlayingOffset = offset instanceof Number ? Math.max(0, Math.min(500, ((Number) offset).intValue())) : 34;
        Object npOpacity = values.get("nowPlayingOpacity");
        nowPlayingOpacity = npOpacity instanceof Number ? Math.max(10, Math.min(100, ((Number) npOpacity).intValue())) : 90;
        showProgress = values.get("showProgress") == null || Boolean.TRUE.equals(values.get("showProgress"));
        String labels = stringSetting(values, "timeLabels");
        timeLabels = labels.isEmpty() ? "Elapsed / remaining" : labels;
        showPlaylist = Boolean.TRUE.equals(values.get("showPlaylist"));
        showNextTrack = Boolean.TRUE.equals(values.get("showNextTrack"));
        Object seconds = values.get("doorbellSeconds");
        doorbellSeconds = seconds instanceof Number ? Math.max(5, Math.min(60, ((Number) seconds).intValue())) : 20;
        Object camOpacity = values.get("cameraOpacity");
        cameraOpacity = camOpacity instanceof Number ? Math.max(10, Math.min(100, ((Number) camOpacity).intValue())) : 100;
        cameraTestMode = Boolean.TRUE.equals(values.get("cameraTestMode"));

        if (nowPlayingView != null) nowPlayingView.setAlpha(nowPlayingOpacity / 100f);
        if (doorbellView != null) doorbellView.setAlpha(cameraOpacity / 100f);

        doorbellInitialSeen = false;
        lastDoorbellState = null;
        doorbellInitialSeen2 = false;
        lastDoorbellState2 = null;
        loadedMediaPicture = null;
        main.post(this::updatePresentation);
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
        return dreaming || manualFotoo || inferredFotoo;
    }

    private void updatePresentation() {
        if (!fotooActive()) {
            hideDoorbell();
            hideNowPlaying();
            return;
        }
        if (cameraTestMode && !doorbellCameraEntity.isEmpty()) {
            showDoorbell();
        }
        updateNowPlaying();
    }

    private void updateNowPlaying() {
        if (!fotooActive() || nowPlayingEntity.isEmpty() || !mediaVisible()) {
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

        String playlist = playlistState;
        if (playlist.isEmpty() || "unknown".equalsIgnoreCase(playlist) || "unavailable".equalsIgnoreCase(playlist)) {
            playlist = firstAttr(mediaAttributes,
                    "media_playlist", "playlist_name", "playlist", "source");
        }
        mediaPlaylist.setText(playlist.isEmpty() ? "" : "Playlist: " + playlist);
        mediaPlaylist.setVisibility(showPlaylist && !playlist.isEmpty() ? View.VISIBLE : View.GONE);

        String next = nextTrackState;
        if (next.isEmpty() || "unknown".equalsIgnoreCase(next) || "unavailable".equalsIgnoreCase(next)) {
            next = firstAttr(mediaAttributes,
                    "next_track", "next_title", "media_next_track", "queue_next");
        }
        mediaNext.setText(next.isEmpty() ? "" : "Næste: " + next);
        mediaNext.setVisibility(showNextTrack && !next.isEmpty() ? View.VISIBLE : View.GONE);

        updateProgress();

        String picture = attr(mediaAttributes, "entity_picture", "");
        if (!picture.equals(loadedMediaPicture)) {
            loadedMediaPicture = picture;
            mediaImage.setImageDrawable(null);
            if (!picture.isEmpty()) fetchMediaImage(picture);
        }
    }

    private void updateProgress() {
        if (mediaProgress == null || mediaTime == null) return;

        double duration = numberAttr(mediaAttributes, "media_duration", 0);
        double position = numberAttr(mediaAttributes, "media_position", 0);
        String updated = attr(mediaAttributes, "media_position_updated_at", "");

        if ("playing".equalsIgnoreCase(mediaState) && !updated.isEmpty()) {
            try {
                long updatedMs = Instant.parse(updated).toEpochMilli();
                position += Math.max(0, System.currentTimeMillis() - updatedMs) / 1000.0;
            } catch (Throwable ignored) {}
        }

        if (duration > 0) position = Math.max(0, Math.min(duration, position));
        boolean haveTimeline = duration > 0;
        mediaProgress.setVisibility(showProgress && haveTimeline ? View.VISIBLE : View.GONE);
        if (haveTimeline) {
            mediaProgress.setProgress((int) Math.round((position / duration) * 1000.0));
        }

        String label = "";
        if (!"Off".equals(timeLabels) && haveTimeline) {
            long elapsed = Math.max(0, Math.round(position));
            long total = Math.max(0, Math.round(duration));
            long remaining = Math.max(0, total - elapsed);
            if ("Elapsed / total".equals(timeLabels)) {
                label = formatTime(elapsed) + " / " + formatTime(total);
            } else if ("Remaining only".equals(timeLabels)) {
                label = "-" + formatTime(remaining);
            } else {
                label = formatTime(elapsed) + " / -" + formatTime(remaining);
            }
        }
        mediaTime.setText(label);
        mediaTime.setVisibility(label.isEmpty() ? View.GONE : View.VISIBLE);
    }

    private static String formatTime(long seconds) {
        long h = seconds / 3600;
        long m = (seconds % 3600) / 60;
        long s = seconds % 60;
        return h > 0
                ? String.format(java.util.Locale.ROOT, "%d:%02d:%02d", h, m, s)
                : String.format(java.util.Locale.ROOT, "%d:%02d", m, s);
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
        card.setAlpha(nowPlayingOpacity / 100f);

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
        mediaPlaylist = textView(13, false, 0xFFBDBDBD);
        mediaNext = textView(13, false, 0xFFD8D8D8);
        mediaProgress = new ProgressBar(context, null, android.R.attr.progressBarStyleHorizontal);
        mediaProgress.setMax(1000);
        mediaTime = textView(12, false, 0xFFBDBDBD);

        text.addView(mediaTitle);
        text.addView(mediaArtist);
        text.addView(mediaAlbum);
        text.addView(mediaPlaylist);
        text.addView(mediaNext);

        LinearLayout.LayoutParams progressParams =
                new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(10));
        progressParams.topMargin = dp(8);
        text.addView(mediaProgress, progressParams);
        text.addView(mediaTime);

        card.addView(text, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));

        int width = Math.min(dp(700), Math.max(dp(300), context.getResources().getDisplayMetrics().widthPixels - dp(32)));
        WindowManager.LayoutParams params = overlayParams(width, ViewGroup.LayoutParams.WRAP_CONTENT);
        params.gravity = ("Top".equals(nowPlayingPosition) ? Gravity.TOP : Gravity.BOTTOM) | Gravity.CENTER_HORIZONTAL;
        params.y = dp(nowPlayingOffset);

        try {
            windowManager.addView(card, params);
            nowPlayingView = card;
            main.removeCallbacks(progressTickTask);
            main.post(progressTickTask);
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
        main.removeCallbacks(hideDoorbellTask);
        main.removeCallbacks(cameraRefreshTask);

        if (doorbellView == null) {
            FrameLayout frame = new FrameLayout(context);
            frame.setBackground(cardBackground(0xF0151517, 22));
            frame.setAlpha(cameraOpacity / 100f);

            doorbellImage = new ImageView(context);
            doorbellImage.setScaleType(ImageView.ScaleType.CENTER_CROP);
            frame.addView(doorbellImage, new FrameLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));

            doorbellLabel = textView(18, true, Color.WHITE);
            doorbellLabel.setText(cameraTestMode ? "Dørklokke – TEST" : "Dørklokke");
            TextView label = doorbellLabel;
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

        if (doorbellLabel != null) {
            doorbellLabel.setText(cameraTestMode ? "Dørklokke – TEST" : "Dørklokke");
        }
        refreshDoorbellImage();
        main.post(cameraRefreshTask);
        if (!cameraTestMode) {
            main.postDelayed(hideDoorbellTask, doorbellSeconds * 1000L);
        }
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
        doorbellLabel = null;
        cameraFetchPending = false;
        if (view != null && windowManager != null) {
            try { windowManager.removeViewImmediate(view); } catch (Throwable ignored) {}
        }
    }

    private void hideNowPlaying() {
        hideNowPlayingImmediate();
    }

    private void hideNowPlayingImmediate() {
        main.removeCallbacks(progressTickTask);
        View view = nowPlayingView;
        nowPlayingView = null;
        mediaImage = null;
        mediaTitle = null;
        mediaArtist = null;
        mediaAlbum = null;
        mediaPlaylist = null;
        mediaNext = null;
        mediaProgress = null;
        mediaTime = null;
        mediaFetchPending = false;
        if (view != null && windowManager != null) {
            try { windowManager.removeViewImmediate(view); } catch (Throwable ignored) {}
        }
    }

    private void showTestOverlay() {
        if (context == null || windowManager == null) return;
        TextView test = textView(18, true, Color.WHITE);
        test.setText("Fotoo Overlay 0.7 test");
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

    private static String firstAttr(Map<?, ?> attributes, String... keys) {
        for (String key : keys) {
            String value = attr(attributes, key, "");
            if (!value.isEmpty() && !"unknown".equalsIgnoreCase(value) &&
                    !"unavailable".equalsIgnoreCase(value)) return value;
        }
        return "";
    }

    private static double numberAttr(Map<?, ?> attributes, String key, double fallback) {
        Object value = attributes == null ? null : attributes.get(key);
        if (value instanceof Number) return ((Number) value).doubleValue();
        if (value != null) {
            try { return Double.parseDouble(String.valueOf(value)); }
            catch (Throwable ignored) {}
        }
        return fallback;
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
