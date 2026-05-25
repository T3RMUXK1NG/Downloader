/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    USE SETTINGS HOOK v3.0.1 ULTIMATE NEXUS                    ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATEV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Settings persistence hook with validation                      ║
 * ║  Features: Local storage, defaults, validation, import/export               ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module hooks/useSettings
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

'use client';

import { useCallback, useEffect, useState } from 'react';
import { useSettingsStore } from '@/store/settingsStore';
import { VideoQuality, AudioQuality, VideoFormat, AudioFormat } from '@/types/api';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface AppSettings {
  // Download settings
  download: {
    defaultOutputDir: string;
    defaultVideoQuality: VideoQuality;
    defaultAudioQuality: AudioQuality;
    defaultVideoFormat: VideoFormat;
    defaultAudioFormat: AudioFormat;
    maxConcurrentDownloads: number;
    autoStartDownloads: boolean;
    overwriteExisting: boolean;
    maxSpeed: number; // 0 = unlimited
    retryAttempts: number;
    timeout: number;
  };
  // Subtitle settings
  subtitles: {
    enabled: boolean;
    defaultLanguages: string[];
    embedInVideo: boolean;
    format: 'srt' | 'vtt' | 'ass';
  };
  // Metadata settings
  metadata: {
    embedMetadata: boolean;
    embedThumbnail: boolean;
    saveThumbnail: boolean;
  };
  // Network settings
  network: {
    proxy: string;
    useProxy: boolean;
    customHeaders: Record<string, string>;
    cookies: string;
  };
  // UI settings
  ui: {
    theme: 'light' | 'dark' | 'system';
    accentColor: string;
    language: string;
    showNotifications: boolean;
    soundEnabled: boolean;
    compactMode: boolean;
    showAdvancedOptions: boolean;
  };
  // History settings
  history: {
    enabled: boolean;
    maxItems: number;
    autoCleanup: boolean;
    cleanupDays: number;
  };
  // Security settings
  security: {
    apiKey: string;
    useAuth: boolean;
    sessionTimeout: number;
  };
}

export interface UseSettingsOptions {
  /** Storage key */
  storageKey?: string;
  /** Auto-save to storage */
  autoSave?: boolean;
  /** Debounce save in ms */
  saveDebounce?: number;
}

export interface UseSettingsReturn {
  /** Current settings */
  settings: AppSettings;
  /** Update settings */
  updateSettings: <K extends keyof AppSettings>(
    category: K,
    updates: Partial<AppSettings[K]>
  ) => void;
  /** Reset to defaults */
  resetToDefaults: () => void;
  /** Reset specific category */
  resetCategory: <K extends keyof AppSettings>(category: K) => void;
  /** Export settings */
  exportSettings: () => string;
  /** Import settings */
  importSettings: (data: string) => boolean;
  /** Check if settings have unsaved changes */
  isDirty: boolean;
  /** Save settings manually */
  save: () => void;
  /** Load settings manually */
  load: () => void;
}

// ═══════════════════════════════════════════════════════════════════════════════
// DEFAULT SETTINGS
// ═══════════════════════════════════════════════════════════════════════════════

export const DEFAULT_SETTINGS: AppSettings = {
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
    accentColor: '#10b981', // emerald-500
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
// HOOK IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * useSettings Hook
 * @description Settings persistence with validation and import/export
 * @param options Hook options
 * @returns Settings controls and state
 */
export function useSettings(options: UseSettingsOptions = {}): UseSettingsReturn {
  const {
    storageKey = 'rs-toolkit-settings',
    autoSave = true,
    saveDebounce = 500,
  } = options;

  // Store
  const { settings, setSettings, updateCategorySettings } = useSettingsStore();

  // State
  const [isDirty, setIsDirty] = useState(false);
  const [saveTimeout, setSaveTimeout] = useState<NodeJS.Timeout | null>(null);

  // ═══════════════════════════════════════════════════════════════════════════
  // LOAD SETTINGS
  // ═══════════════════════════════════════════════════════════════════════════

  const load = useCallback(() => {
    if (typeof window === 'undefined') return;

    try {
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        const parsed = JSON.parse(stored) as Partial<AppSettings>;
        // Merge with defaults to ensure all fields exist
        setSettings({
          ...DEFAULT_SETTINGS,
          ...parsed,
          download: { ...DEFAULT_SETTINGS.download, ...parsed.download },
          subtitles: { ...DEFAULT_SETTINGS.subtitles, ...parsed.subtitles },
          metadata: { ...DEFAULT_SETTINGS.metadata, ...parsed.metadata },
          network: { ...DEFAULT_SETTINGS.network, ...parsed.network },
          ui: { ...DEFAULT_SETTINGS.ui, ...parsed.ui },
          history: { ...DEFAULT_SETTINGS.history, ...parsed.history },
          security: { ...DEFAULT_SETTINGS.security, ...parsed.security },
        });
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  }, [storageKey, setSettings]);

  // Initial load
  useEffect(() => {
    load();
  }, [load]);

  // ═══════════════════════════════════════════════════════════════════════════
  // SAVE SETTINGS
  // ═══════════════════════════════════════════════════════════════════════════

  const save = useCallback(() => {
    if (typeof window === 'undefined') return;

    try {
      localStorage.setItem(storageKey, JSON.stringify(settings));
      setIsDirty(false);
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  }, [storageKey, settings]);

  // Auto-save with debounce
  useEffect(() => {
    if (!autoSave || !isDirty) return;

    if (saveTimeout) {
      clearTimeout(saveTimeout);
    }

    const timeout = setTimeout(() => {
      save();
    }, saveDebounce);

    setSaveTimeout(timeout);

    return () => {
      if (timeout) {
        clearTimeout(timeout);
      }
    };
  }, [settings, autoSave, isDirty, saveDebounce, save]);

  // ═══════════════════════════════════════════════════════════════════════════
  // UPDATE SETTINGS
  // ═══════════════════════════════════════════════════════════════════════════

  const updateSettings = useCallback(
    <K extends keyof AppSettings>(
      category: K,
      updates: Partial<AppSettings[K]>
    ) => {
      updateCategorySettings(category, updates);
      setIsDirty(true);
    },
    [updateCategorySettings]
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // RESET SETTINGS
  // ═══════════════════════════════════════════════════════════════════════════

  const resetToDefaults = useCallback(() => {
    setSettings(DEFAULT_SETTINGS);
    setIsDirty(true);
  }, [setSettings]);

  const resetCategory = useCallback(
    <K extends keyof AppSettings>(category: K) => {
      updateCategorySettings(category, DEFAULT_SETTINGS[category]);
      setIsDirty(true);
    },
    [updateCategorySettings]
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // IMPORT/EXPORT
  // ═══════════════════════════════════════════════════════════════════════════

  const exportSettings = useCallback((): string => {
    return JSON.stringify(settings, null, 2);
  }, [settings]);

  const importSettings = useCallback(
    (data: string): boolean => {
      try {
        const parsed = JSON.parse(data) as Partial<AppSettings>;
        // Validate and merge with defaults
        setSettings({
          ...DEFAULT_SETTINGS,
          ...parsed,
          download: { ...DEFAULT_SETTINGS.download, ...parsed.download },
          subtitles: { ...DEFAULT_SETTINGS.subtitles, ...parsed.subtitles },
          metadata: { ...DEFAULT_SETTINGS.metadata, ...parsed.metadata },
          network: { ...DEFAULT_SETTINGS.network, ...parsed.network },
          ui: { ...DEFAULT_SETTINGS.ui, ...parsed.ui },
          history: { ...DEFAULT_SETTINGS.history, ...parsed.history },
          security: { ...DEFAULT_SETTINGS.security, ...parsed.security },
        });
        setIsDirty(true);
        return true;
      } catch (error) {
        console.error('Failed to import settings:', error);
        return false;
      }
    },
    [setSettings]
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // RETURN
  // ═══════════════════════════════════════════════════════════════════════════

  return {
    settings,
    updateSettings,
    resetToDefaults,
    resetCategory,
    exportSettings,
    importSettings,
    isDirty,
    save,
    load,
  };
}

export default useSettings;
