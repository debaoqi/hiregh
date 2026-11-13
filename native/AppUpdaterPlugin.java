package com.hiregh.app;

import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.provider.Settings;
import androidx.core.content.FileProvider;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;

/** JobPaw 应用内更新：下载新版 APK（带进度），然后调起系统安装界面 */
@CapacitorPlugin(name = "AppUpdater")
public class AppUpdaterPlugin extends Plugin {
    private volatile boolean cancelled = false;
    private volatile boolean busy = false;
    private volatile HttpURLConnection cur = null;

    private File apkFile() { return new File(getContext().getCacheDir(), "update/JobPaw-update.apk"); }

    @PluginMethod
    public void download(final PluginCall call) {
        final String u = call.getString("url");
        if (u == null) { call.reject("no url"); return; }
        if (busy) { call.reject("busy"); return; }
        busy = true; cancelled = false;
        new Thread(() -> {
            HttpURLConnection c = null;
            try {
                File f = apkFile(); f.getParentFile().mkdirs(); if (f.exists()) f.delete();
                String url = u; int hops = 0;
                while (true) {
                    c = (HttpURLConnection) new URL(url).openConnection(); cur = c;
                    c.setInstanceFollowRedirects(false);
                    c.setConnectTimeout(15000); c.setReadTimeout(20000);
                    c.setRequestProperty("User-Agent", "JobPaw-Updater");
                    int code = c.getResponseCode();
                    if (code >= 300 && code < 400 && hops++ < 6) { url = new URL(new URL(url), c.getHeaderField("Location")).toString(); c.disconnect(); continue; }
                    if (code != 200) throw new Exception("HTTP " + code);
                    break;
                }
                long total = c.getContentLengthLong(); long done = 0; int lastPct = -1; long lastT = 0;
                try (InputStream in = c.getInputStream(); FileOutputStream out = new FileOutputStream(f)) {
                    byte[] buf = new byte[64 * 1024]; int n;
                    while ((n = in.read(buf)) > 0) {
                        if (cancelled) throw new Exception("cancelled");
                        out.write(buf, 0, n); done += n;
                        int pct = total > 0 ? (int) (done * 100 / total) : -1; long now = System.currentTimeMillis();
                        if (pct != lastPct && now - lastT > 150) { lastPct = pct; lastT = now;
                            JSObject p = new JSObject(); p.put("pct", pct); p.put("done", done); p.put("total", total); notifyListeners("progress", p); }
                    }
                }
                if (total > 0 && done < total) throw new Exception("incomplete");
                if (done < 500000) throw new Exception("too small");
                JSObject r = new JSObject(); r.put("path", f.getAbsolutePath()); r.put("size", done); call.resolve(r);
            } catch (Exception e) {
                call.reject(cancelled ? "cancelled" : String.valueOf(e.getMessage()));
            } finally { if (c != null) c.disconnect(); cur = null; busy = false; }
        }).start();
    }

    @PluginMethod
    public void cancel(PluginCall call) { cancelled = true; HttpURLConnection x = cur; if (x != null) try { x.disconnect(); } catch (Exception ignored) {} call.resolve(); }

    @PluginMethod
    public void canInstall(PluginCall call) {
        JSObject r = new JSObject();
        r.put("allowed", Build.VERSION.SDK_INT < 26 || getContext().getPackageManager().canRequestPackageInstalls());
        r.put("downloaded", apkFile().exists());
        call.resolve(r);
    }

    @PluginMethod
    public void openInstallSettings(PluginCall call) {
        if (Build.VERSION.SDK_INT >= 26) {
            Intent i = new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:" + getContext().getPackageName()));
            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            getContext().startActivity(i);
        }
        call.resolve();
    }

    @PluginMethod
    public void install(PluginCall call) {
        File f = apkFile();
        if (!f.exists()) { call.reject("not downloaded"); return; }
        if (Build.VERSION.SDK_INT >= 26 && !getContext().getPackageManager().canRequestPackageInstalls()) {
            JSObject r = new JSObject(); r.put("needPermission", true); call.resolve(r); return;
        }
        Uri uri = FileProvider.getUriForFile(getContext(), getContext().getPackageName() + ".fileprovider", f);
        Intent i = new Intent(Intent.ACTION_VIEW);
        i.setDataAndType(uri, "application/vnd.android.package-archive");
        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
        getContext().startActivity(i);
        JSObject r = new JSObject(); r.put("started", true); call.resolve(r);
    }
}
