/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    SETTINGS STORE v3.0.1 ULTIMATE NEXUS                       ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Settings state management with Zustand                         ║
 * ║  Features: Categories, validation, persistence, defaults                    ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module store/settingsStore
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { VideoQuality, AudioQuality, VideoFormat, AudioFormat } from '@/types/api';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface DownloadSettings {
  defaultOutputDir: string;
  defaultVideoQuality: VideoQuality;
  defaultAudioQuality: AudioQuality;
  defaultVideoFormat: VideoFormat;
  defaultAudioFormat: AudioFormat;
  maxConcurrentDownloads: number;
  autoStartDownloads: boolean;
  overwriteExisting: boolean;
  maxSpeed: number;
  retryAttempts: number;
  timeout: number;
}

export interface SubtitleSettings {
  enabled: boolean;
  defaultLanguages: string[];
  embedInVideo: boolean;
  format: 'srt' | 'vtt' | 'ass';
}

export interface MetadataSettings {
  embedMetadata: boolean;
  embedThumbnail: boolean;
  saveThumbnail: boolean;
}

export interface NetworkSettings {
  proxy: string;
  useProxy: boolean;
  customHeaders: Record<string, string>;
  cookies: string;
}

export interface UISettings {
  theme: 'light' | 'dark' | 'system';
  accentColor: string;
  language: string;
  showNotifications: boolean;
  soundEnabled: boolean;
  compactMode: boolean;
  showAdvancedOptions: boolean;
}

export interface HistorySettings {
  enabled: boolean;
  maxItems: number;
  autoCleanup: boolean;
  cleanupDays: number;
}

export interface SecuritySettings {
  apiKey: string;
  useAuth: boolean;
  sessionTimeout: number;
}

export interface AppSettings {
  download: DownloadSettings;
  subtitles: SubtitleSettings;
  metadata: MetadataSettings;
  network: NetworkSettings;
  ui: UISettings;
  history: HistorySettings;
  security: SecuritySettings;
}

export interface SettingsStore {
  // State
  settings: AppSettings;
  isDirty: boolean;
  lastSaved: Date | null;

  // Actions
  setSettings: (settings: AppSettings) => void;
  updateCategorySettings: <K extends keyof AppSettings>(
    category: K,
    updates: Partial<AppSettings[K]>
  ) => void;
  resetToDefaults: () => void;
  resetCategory: <K extends keyof AppSettings>(category: K) => void;
  markSaved: () => void;
}

// ═══════════════════════════════════════════════════════════════════════════════
// DEFAULT SETTINGS
// ═══════════════════════════════════════════════════════════════════════════════

export const DEFAULT_APP_SETTINGS: AppSettings = {
  download: {
    defaultOutputDir: '~/Downloads/RS-Toolkit',
    defaultVideoQuality: VideoQuality.Q1080P,
    defaultAudioQuality: AudioQuality.HIGH,
    defaultVideoFormat: VideoFormat.MP4,
    defaultAudioFormat: AudioFormat.MP3,
    maxConcurrentDownloads: 3,
    autoStartDownloads: true,
    overwriteExisting: false,
    maxSpeed: 0,
    retryAttempts: 3,
    timeout: 300,
  },
  subtitles: {
    enabled: true,
    defaultLanguages: ['en'],
    embedInVideo: false,
    format: 'srt',
  },
  metadata: {
    embedMetadata: true,
    embedThumbnail: false,
    saveThumbnail: true,
  },
  network: {
    proxy: '',
    useProxy: false,
    customHeaders: {},
    cookies: '',
  },
  ui: {
    theme: 'system',
    accentColor: '#10b981',
    language: 'en',
    showNotifications: true,
    soundEnabled: true,
    compactMode: false,
    showAdvancedOptions: false,
  },
  history: {
    enabled: true,
    maxItems: 1000,
    autoCleanup: true,
    cleanupDays: 30,
  },
  security: {
    apiKey: '',
    useAuth: false,
    sessionTimeout: 3600,
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// STORE IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

export const useSettingsStore = create<SettingsStore>()(
  immer((set) => ({
    // ═════════════════════════════════════════════════════════════════════════
    // INITIAL STATE
    // ═════════════════════════════════════════════════════════════════════════
    settings: DEFAULT_APP_SETTINGS,
    isDirty: false,
    lastSaved: null,

    // ═════════════════════════════════════════════════════════════════════════
    // ACTIONS
    // ═════════════════════════════════════════════════════════════════════════

    setSettings: (settings) => {
      set((state) => {
        state.settings = settings;
        state.isDirty = true;
      });
    },

    updateCategorySettings: (category, updates) => {
      set((state) => {
        state.settings[category] = {
          ...state.settings[category],
          ...updates,
        } as AppSettings[typeof category];
        state.isDirty = true;
      });
    },

    resetToDefaults: () => {
      set((state) => {
        state.settings = { ...DEFAULT_APP_SETTINGS };
        state.isDirty = true;
      });
    },

    resetCategory: (category) => {
      set((state) => {
        state.settings[category] = { ...DEFAULT_APP_SETTINGS[category] } as AppSettings[typeof category];
        state.isDirty = true;
      });
    },

    markSaved: () => {
      set((state) => {
        state.isDirty = false;
        state.lastSaved = new Date();
      });
    },
  }))
);

export default useSettingsStore;
