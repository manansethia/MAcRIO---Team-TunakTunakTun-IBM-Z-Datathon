#!/usr/bin/env python3
"""
Automated Android APK Builder for MAcRIO NutriHealth AI.
Compiles a native Android wrapper with modern WebView, Camera, and File upload support.
Uses Android Build Tools 34.0.0 and signs the APK with standard debug key.
"""

import os
import shutil
import subprocess
import sys

SDK_ROOT = "/opt/homebrew/share/android-commandlinetools"
BUILD_TOOLS = os.path.join(SDK_ROOT, "build-tools", "34.0.0")
ANDROID_JAR = os.path.join(SDK_ROOT, "platforms", "android-34", "android.jar")

AAPT2 = os.path.join(BUILD_TOOLS, "aapt2")
D8 = os.path.join(BUILD_TOOLS, "d8")
ZIPALIGN = os.path.join(BUILD_TOOLS, "zipalign")
APKSIGNER = os.path.join(BUILD_TOOLS, "apksigner")

PROJECT_DIR = "/Users/manan/Documents/TunakTunakTun_MAcRIO_IBMZ/android_project"
SRC_DIR = os.path.join(PROJECT_DIR, "src", "com", "macrio", "nutrihealth")
RES_DIR = os.path.join(PROJECT_DIR, "res")
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
BIN_DIR = os.path.join(PROJECT_DIR, "bin")
OUTPUT_APK = "/Users/manan/Documents/TunakTunakTun_MAcRIO_IBMZ/static/macrio.apk"

def setup_dirs():
    if os.path.exists(PROJECT_DIR):
        shutil.rmtree(PROJECT_DIR)
    os.makedirs(SRC_DIR, exist_ok=True)
    os.makedirs(os.path.join(RES_DIR, "values"), exist_ok=True)
    os.makedirs(os.path.join(RES_DIR, "layout"), exist_ok=True)
    os.makedirs(os.path.join(RES_DIR, "mipmap-hdpi"), exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)
    os.makedirs(BIN_DIR, exist_ok=True)

def create_manifest():
    manifest_content = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.macrio.nutrihealth"
    android:versionCode="2"
    android:versionName="3.0.0">

    <uses-sdk android:minSdkVersion="26" android:targetSdkVersion="34" />

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" android:maxSdkVersion="32" />
    <uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
    <uses-permission android:name="android.permission.VIBRATE" />

    <uses-feature android:name="android.hardware.camera" android:required="false" />
    <uses-feature android:name="android.hardware.camera.autofocus" android:required="false" />

    <application
        android:label="@string/app_name"
        android:icon="@android:drawable/sym_def_app_icon"
        android:theme="@android:style/Theme.NoTitleBar.Fullscreen"
        android:usesCleartextTraffic="true"
        android:hardwareAccelerated="true">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""
    with open(os.path.join(PROJECT_DIR, "AndroidManifest.xml"), "w") as f:
        f.write(manifest_content)

def create_resources():
    strings = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">MAcRIO NutriHealth AI</string>
</resources>
"""
    with open(os.path.join(RES_DIR, "values", "strings.xml"), "w") as f:
        f.write(strings)

    layout = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <WebView
        android:id="@+id/webview"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
</LinearLayout>
"""
    with open(os.path.join(RES_DIR, "layout", "activity_main.xml"), "w") as f:
        f.write(layout)

def copy_assets():
    # Copy static/index.html to assets so the app works offline as well
    src_html = "/Users/manan/Documents/TunakTunakTun_MAcRIO_IBMZ/static/index.html"
    if os.path.exists(src_html):
        shutil.copy(src_html, os.path.join(ASSETS_DIR, "index.html"))

def create_java_source():
    java_code = """package com.macrio.nutrihealth;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebChromeClient;
import android.webkit.PermissionRequest;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceError;
import android.webkit.WebResourceResponse;
import android.content.Intent;
import android.net.Uri;
import android.webkit.ValueCallback;
import android.content.pm.PackageManager;
import android.os.Build;
import android.Manifest;

public class MainActivity extends Activity {
    private WebView webView;
    public static ValueCallback<Uri[]> uploadMessage;
    public final static int FILECHOOSER_RESULTCODE = 1001;

    public static class AppWebViewClient extends WebViewClient {
        @Override
        public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
            view.loadUrl("file:///android_asset/index.html");
        }

        @Override
        public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
            if (request != null && request.isForMainFrame()) {
                view.loadUrl("file:///android_asset/index.html");
            }
        }

        @Override
        public void onReceivedHttpError(WebView view, WebResourceRequest request, WebResourceResponse errorResponse) {
            if (request != null && request.isForMainFrame() && errorResponse != null && errorResponse.getStatusCode() >= 400) {
                view.loadUrl("file:///android_asset/index.html");
            }
        }
    }

    public static class AppWebChromeClient extends WebChromeClient {
        private final Activity activity;

        public AppWebChromeClient(Activity act) {
            this.activity = act;
        }

        @Override
        public void onPermissionRequest(PermissionRequest request) {
            request.grant(request.getResources());
        }

        @Override
        public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> filePathCallback, FileChooserParams fileChooserParams) {
            if (uploadMessage != null) {
                uploadMessage.onReceiveValue(null);
            }
            uploadMessage = filePathCallback;
            Intent intent = fileChooserParams.createIntent();
            try {
                activity.startActivityForResult(intent, FILECHOOSER_RESULTCODE);
            } catch (Exception e) {
                uploadMessage = null;
                return false;
            }
            return true;
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(new String[]{Manifest.permission.CAMERA, Manifest.permission.RECORD_AUDIO}, 101);
            }
        }

        webView = (WebView) findViewById(R.id.webview);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);

        webView.setWebViewClient(new AppWebViewClient());
        webView.setWebChromeClient(new AppWebChromeClient(this));

        webView.loadUrl("https://till-ruling-carlo-programmer.trycloudflare.com/");
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == FILECHOOSER_RESULTCODE) {
            if (uploadMessage == null) return;
            uploadMessage.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(resultCode, data));
            uploadMessage = null;
        }
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
"""
    with open(os.path.join(SRC_DIR, "MainActivity.java"), "w") as f:
        f.write(java_code)

def run_command(cmd, desc):
    print(f"==> {desc}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"ERROR in {desc}:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}")
        sys.exit(1)
    return res.stdout

def build_apk():
    setup_dirs()
    create_manifest()
    create_resources()
    copy_assets()
    create_java_source()

    manifest_file = os.path.join(PROJECT_DIR, "AndroidManifest.xml")
    compiled_res_zip = os.path.join(BIN_DIR, "compiled_res.zip")
    unaligned_apk = os.path.join(BIN_DIR, "app-unaligned.apk")
    aligned_apk = os.path.join(BIN_DIR, "app-aligned.apk")
    r_java_dir = os.path.join(PROJECT_DIR, "gen")
    os.makedirs(r_java_dir, exist_ok=True)

    # 1. Compile resources with aapt2
    run_command(
        f"{AAPT2} compile --dir {RES_DIR} -o {compiled_res_zip}",
        "Compiling resources with aapt2"
    )

    # 2. Link resources and generate R.java
    run_command(
        f"{AAPT2} link -I {ANDROID_JAR} --manifest {manifest_file} {compiled_res_zip} "
        f"--java {r_java_dir} -o {unaligned_apk} -A {ASSETS_DIR} --auto-add-overlay",
        "Linking resources and generating R.java"
    )

    # 3. Compile Java sources (MainActivity.java + R.java)
    classes_dir = os.path.join(BIN_DIR, "classes")
    os.makedirs(classes_dir, exist_ok=True)
    r_java = os.path.join(r_java_dir, "com", "macrio", "nutrihealth", "R.java")
    main_java = os.path.join(SRC_DIR, "MainActivity.java")

    run_command(
        f"javac -source 8 -target 8 -g:none -bootclasspath {ANDROID_JAR} -d {classes_dir} {r_java} {main_java}",
        "Compiling Java sources with javac"
    )

    # 4. Convert .class files to classes.dex using d8
    run_command(
        f"{D8} --lib {ANDROID_JAR} --output {BIN_DIR} {classes_dir}/com/macrio/nutrihealth/*.class",
        "Converting Java bytecode to classes.dex with d8"
    )

    # 5. Add classes.dex into unaligned apk
    dex_file = os.path.join(BIN_DIR, "classes.dex")
    run_command(
        f"cd {BIN_DIR} && zip -u {unaligned_apk} classes.dex",
        "Adding classes.dex into APK"
    )

    # 6. Align APK with zipalign
    run_command(
        f"{ZIPALIGN} -f -p 4 {unaligned_apk} {aligned_apk}",
        "Aligning APK with zipalign"
    )

    # 7. Generate debug keystore if not exists
    keystore = os.path.join(PROJECT_DIR, "debug.keystore")
    if not os.path.exists(keystore):
        run_command(
            f"keytool -genkey -v -keystore {keystore} -storepass android -alias androiddebugkey "
            f"-keypass android -keyalg RSA -keysize 2048 -validity 10000 -dname \"CN=Android Debug,O=Android,C=US\"",
            "Generating Android debug keystore"
        )

    # 8. Sign APK with apksigner
    run_command(
        f"{APKSIGNER} sign --ks {keystore} --ks-pass pass:android --ks-key-alias androiddebugkey --key-pass pass:android --out {OUTPUT_APK} {aligned_apk}",
        "Signing APK with apksigner"
    )

    print(f"\nSUCCESS! Android APK compiled and signed successfully at:\n{OUTPUT_APK}")
    print(f"File size: {os.path.getsize(OUTPUT_APK):,} bytes")

if __name__ == "__main__":
    build_apk()
