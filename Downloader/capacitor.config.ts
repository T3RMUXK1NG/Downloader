/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * RS TOOLKIT v3.0.1 ULTIMATE NEXUS - Capacitor Configuration
 * ═══════════════════════════════════════════════════════════════════════════════
 *
 * Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng
 * License: OMNIPOTENT SOVEREIGN NEXUS
 *
 * Cross-platform mobile app configuration for:
 * - Android APK builds
 * - iOS builds
 * - PWA support
 * - Native plugins
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import type { CapacitorConfig } from '@capacitor/cli';

// ═══════════════════════════════════════════════════════════════════════════════
// ENVIRONMENT CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

const isDev = process.env.NODE_ENV === 'development';
const isProd = process.env.NODE_ENV === 'production';

// Server URL configuration
const serverUrl = isDev
  ? 'http://localhost:3000'
  : 'https://t3rmuxk1ng.com';

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN CAPACITOR CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

const config: CapacitorConfig = {
  // ─────────────────────────────────────────────────────────────────────────────
  // APP IDENTIFICATION
  // ─────────────────────────────────────────────────────────────────────────────

  appId: 'com.t3rmuxk1ng.rstoolkit',
  appName: 'RS Toolkit',
  webDir: 'out',
  bundledWebRuntime: false,

  // ─────────────────────────────────────────────────────────────────────────────
  // SERVER CONFIGURATION
  // ─────────────────────────────────────────────────────────────────────────────

  server: {
    url: isDev ? serverUrl : undefined,
    cleartext: isDev,
    androidScheme: 'https',
    iosScheme: 'https',
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // SOURCE MAPS
  // ─────────────────────────────────────────────────────────────────────────────

  sourceMap: isDev ? 'inline' : false,

  // ─────────────────────────────────────────────────────────────────────────────
  // ANDROID CONFIGURATION
  // ─────────────────────────────────────────────────────────────────────────────

  android: {
    allowMixedContent: isDev,
    captureInput: true,
    webContentsDebuggingEnabled: isDev,
    backgroundColor: '#0f0f19',

    // Build configuration
    buildOptions: {
      keystorePath: './android/keystore/release.keystore',
      keystorePassword: process.env.ANDROID_KEYSTORE_PASSWORD,
      keystoreAlias: 'rstoolkit',
      keystoreAliasPassword: process.env.ANDROID_KEY_ALIAS_PASSWORD,
      signingType: 'apksigner',
    },

    // Display configuration
    display: {
      backgroundColor: '#0f0f19',
    },

    // Theme configuration
    theme: '#00c8ff',

    // Navigation color
    navigationColor: '#0f0f19',

    // Status bar
    statusBar: {
      style: 'Dark',
      backgroundColor: '#0f0f19',
      visible: true,
    },
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // IOS CONFIGURATION
  // ─────────────────────────────────────────────────────────────────────────────

  ios: {
    allowsLinkPreview: false,
    allowsBackForwardNavigationGestures: true,
    contentInset: 'automatic',
    scrollEnabled: true,
    backgroundColor: '#0f0f19',

    // Scheme configuration
    scheme: 'rstoolkit',

    // Preferred content mode
    preferredContentMode: 'mobile',

    // Cordova preferences
    preferences: {
      ScrollEnabled: true,
      'EnableSwift': true,
      'MinCompileVersion': '13.0',
      'SwiftVersion': '5.5',
      'UseSwiftLanguageVersion': '5',
    },

    // Build configuration
    buildOptions: {
      provisioningProfile: process.env.IOS_PROVISIONING_PROFILE,
      teamId: process.env.IOS_TEAM_ID,
      signType: 'app-store',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // SPLASH SCREEN CONFIGURATION
  // ─────────────────────────────────────────────────────────────────────────────

  plugins: {
    SplashScreen: {
      launchShowDuration: 3000,
      launchAutoHide: false,
      backgroundColor: '#0f0f19',
      androidSplashResourceName: 'splash',
      androidScaleType: 'CENTER_CROP',
      showSpinner: true,
      androidSpinnerStyle: 'large',
      iosSpinnerStyle: 'small',
      spinnerColor: '#00c8ff',
      splashFullScreen: true,
      splashImmersive: true,
      showSpinnerDuration: 0,
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // STATUS BAR CONFIGURATION
    // ─────────────────────────────────────────────────────────────────────────────

    StatusBar: {
      style: 'Dark',
      backgroundColor: '#0f0f19',
      animation: 'slide',
      iosOverlaysWebView: true,
      androidOverlaysWebView: false,
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // KEYBOARD CONFIGURATION
    // ─────────────────────────────────────────────────────────────────────────────

    Keyboard: {
      resize: 'body',
      resizeOnFullScreen: true,
      style: 'dark',
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // PUSH NOTIFICATIONS CONFIGURATION
    // ─────────────────────────────────────────────────────────────────────────────

    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert'],
      appName: 'RS Toolkit',
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // BROWSER CONFIGURATION
    // ─────────────────────────────────────────────────────────────────────────────

    Browser: {
      windowName: '_blank',
      toolbarColor: '#0f0f19',
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // CAMERA CONFIGURATION
    // ─────────────────────────────────────────────────────────────────────────────

    Camera: {
      permissions: ['camera', 'photos'],
      correctOrientation: true,
      saveToGallery: true,
      quality: 90,
      allowEditing: false,
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // FILESYSTEM CONFIGURATION
    // ─────────────────────────────────────────────────────────────────────────────

    Filesystem: {
      permissions: {
        read: true,
        write: true,
      },
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // NETWORK CONFIGURATION
    // ─────────────────────────────────────────────────────────────────────────────

    Network: {
      monitor: true,
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // HAPTICS CONFIGURATION
    // ─────────────────────────────────────────────────────────────────────────────

    Haptics: {
      enabled: true,
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // TOAST CONFIGURATION
    // ─────────────────────────────────────────────────────────────────────────────

    Toast: {
      duration: 'long',
      position: 'bottom',
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // SHARE CONFIGURATION
    // ─────────────────────────────────────────────────────────────────────────────

    Share: {
      dialogTitle: 'Share RS Toolkit',
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // GEOLOCATION CONFIGURATION
    // ─────────────────────────────────────────────────────────────────────────────

    Geolocation: {
      permissions: ['location', 'locationAlways', 'locationWhenInUse'],
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0,
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // DEVICE CONFIGURATION
    // ─────────────────────────────────────────────────────────────────────────────

    Device: {
      collectDeviceId: true,
    },
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // APP CONFIGURATION
  // ─────────────────────────────────────────────────────────────────────────────

  app: {
    logLevel: isDev ? 'debug' : 'error',
    launchUrl: '',
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // CORDOVA PREFERENCES (Legacy Support)
  // ─────────────────────────────────────────────────────────────────────────────

  cordova: {
    preferences: {
      KeepRunning: true,
      Background: true,
      'EnableMulticastDNS': true,
      'EnableViewportScale': true,
      'AllowInlineMediaPlayback': true,
      'MediaPlaybackRequiresUserAction': false,
    },
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // PWA CONFIGURATION
  // ─────────────────────────────────────────────────────────────────────────────

  pwa: {
    enabled: true,
    manifest: {
      name: 'RS Toolkit',
      short_name: 'RSToolkit',
      description: 'Elite Security Toolkit by T3rmuxk1ng',
      start_url: '/',
      display: 'standalone',
      orientation: 'any',
      background_color: '#0f0f19',
      theme_color: '#00c8ff',
      icons: [
        {
          src: '/icons/icon-72x72.png',
          sizes: '72x72',
          type: 'image/png',
        },
        {
          src: '/icons/icon-96x96.png',
          sizes: '96x96',
          type: 'image/png',
        },
        {
          src: '/icons/icon-128x128.png',
          sizes: '128x128',
          type: 'image/png',
        },
        {
          src: '/icons/icon-144x144.png',
          sizes: '144x144',
          type: 'image/png',
        },
        {
          src: '/icons/icon-152x152.png',
          sizes: '152x152',
          type: 'image/png',
        },
        {
          src: '/icons/icon-192x192.png',
          sizes: '192x192',
          type: 'image/png',
        },
        {
          src: '/icons/icon-384x384.png',
          sizes: '384x384',
          type: 'image/png',
        },
        {
          src: '/icons/icon-512x512.png',
          sizes: '512x512',
          type: 'image/png',
        },
      ],
      screenshots: [
        {
          src: '/screenshots/home.png',
          sizes: '1280x720',
          type: 'image/png',
          form_factor: 'wide',
        },
        {
          src: '/screenshots/mobile.png',
          sizes: '720x1280',
          type: 'image/png',
          form_factor: 'narrow',
        },
      ],
      categories: ['utilities', 'productivity'],
      shortcuts: [
        {
          name: 'Download',
          short_name: 'Download',
          description: 'Download media files',
          url: '/download',
          icons: [{ src: '/icons/download.png', sizes: '96x96' }],
        },
        {
          name: 'Tools',
          short_name: 'Tools',
          description: 'Security tools',
          url: '/tools',
          icons: [{ src: '/icons/tools.png', sizes: '96x96' }],
        },
      ],
    },
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // SECURITY CONFIGURATION
  // ─────────────────────────────────────────────────────────────────────────────

  security: {
    // Content Security Policy
    csp: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: blob: https:",
      "connect-src 'self' https: wss:",
      "media-src 'self' blob:",
    ].join('; '),

    // SSL pinning for production
    sslPinning: isProd
      ? {
          enabled: true,
          certificates: ['certs/t3rmuxk1ng.com.crt'],
        }
      : undefined,
  },

  // ─────────────────────────────────────────────────────────────────────────────
  // EXTENSIONS
  // ─────────────────────────────────────────────────────────────────────────────

  extensions: {
    // Capacitor Updater for OTA updates
    capacitorUpdater: {
      enabled: true,
      autoUpdate: true,
      resetWhenUpdate: true,
    },
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORT CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

export default config;
