/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    USE LANGUAGE HOOK v3.0.1 ULTIMATE NEXUS                    ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Internationalization hook with pluralization support           ║
 * ║  Features: Multi-language, pluralization, interpolation, persistence        ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module hooks/useLanguage
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

'use client';

import { useCallback, useEffect, useState, useMemo } from 'react';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export type LanguageCode = 'en' | 'hi' | 'es' | 'fr' | 'de' | 'ja' | 'zh' | 'pt' | 'ru' | 'ar';

export interface Language {
  code: LanguageCode;
  name: string;
  nativeName: string;
  rtl?: boolean;
}

export interface TranslationValue {
  [key: string]: string | TranslationValue;
}

export interface UseLanguageOptions {
  /** Default language */
  defaultLanguage?: LanguageCode;
  /** Storage key */
  storageKey?: string;
  /** Fallback language */
  fallbackLanguage?: LanguageCode;
}

export interface UseLanguageReturn {
  /** Current language */
  language: LanguageCode;
  /** Set language */
  setLanguage: (lang: LanguageCode) => void;
  /** Available languages */
  languages: Language[];
  /** Translation function */
  t: (key: string, params?: Record<string, string | number>) => string;
  /** Plural translation */
  plural: (key: string, count: number, params?: Record<string, string | number>) => string;
  /** Check if current language is RTL */
  isRTL: boolean;
  /** Get direction */
  direction: 'ltr' | 'rtl';
  /** Format number */
  formatNumber: (num: number, options?: Intl.NumberFormatOptions) => string;
  /** Format date */
  formatDate: (date: Date, options?: Intl.DateTimeFormatOptions) => string;
  /** Format relative time */
  formatRelativeTime: (value: number, unit: Intl.RelativeTimeFormatUnit) => string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════════════════════════════

export const LANGUAGES: Language[] = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी' },
  { code: 'es', name: 'Spanish', nativeName: 'Español' },
  { code: 'fr', name: 'French', nativeName: 'Français' },
  { code: 'de', name: 'German', nativeName: 'Deutsch' },
  { code: 'ja', name: 'Japanese', nativeName: '日本語' },
  { code: 'zh', name: 'Chinese', nativeName: '中文' },
  { code: 'pt', name: 'Portuguese', nativeName: 'Português' },
  { code: 'ru', name: 'Russian', nativeName: 'Русский' },
  { code: 'ar', name: 'Arabic', nativeName: 'العربية', rtl: true },
];

// ═══════════════════════════════════════════════════════════════════════════════
// TRANSLATIONS
// ═══════════════════════════════════════════════════════════════════════════════

const translations: Record<LanguageCode, TranslationValue> = {
  en: {
    common: {
      appName: 'RS TOOLKIT',
      download: 'Download',
      pause: 'Pause',
      resume: 'Resume',
      cancel: 'Cancel',
      retry: 'Retry',
      settings: 'Settings',
      history: 'History',
      search: 'Search',
      filter: 'Filter',
      sort: 'Sort',
      export: 'Export',
      import: 'Import',
      clear: 'Clear',
      delete: 'Delete',
      edit: 'Edit',
      save: 'Save',
      close: 'Close',
      confirm: 'Confirm',
      yes: 'Yes',
      no: 'No',
      loading: 'Loading...',
      error: 'Error',
      success: 'Success',
      warning: 'Warning',
      info: 'Info',
    },
    download: {
      title: 'Download Manager',
      enterUrl: 'Enter URL',
      startDownload: 'Start Download',
      downloadComplete: 'Download Complete',
      downloadFailed: 'Download Failed',
      downloadPaused: 'Download Paused',
      downloadCancelled: 'Download Cancelled',
      downloading: 'Downloading...',
      processing: 'Processing...',
      validating: 'Validating...',
      speed: 'Speed',
      eta: 'ETA',
      progress: 'Progress',
      fileSize: 'File Size',
      quality: 'Quality',
      format: 'Format',
      subtitles: 'Subtitles',
      thumbnail: 'Thumbnail',
      metadata: 'Metadata',
    },
    history: {
      title: 'Download History',
      noDownloads: 'No downloads yet',
      today: 'Today',
      yesterday: 'Yesterday',
      thisWeek: 'This Week',
      thisMonth: 'This Month',
      older: 'Older',
      clearHistory: 'Clear History',
      exportHistory: 'Export History',
      importHistory: 'Import History',
      downloads: '{count} downloads',
      totalSize: 'Total Size: {size}',
    },
    settings: {
      title: 'Settings',
      general: 'General',
      download: 'Download',
      network: 'Network',
      ui: 'User Interface',
      security: 'Security',
      about: 'About',
      resetToDefaults: 'Reset to Defaults',
      resetConfirm: 'Are you sure you want to reset all settings?',
      save: 'Save Settings',
    },
    notifications: {
      downloadStarted: 'Download started: {title}',
      downloadComplete: 'Download complete: {title}',
      downloadFailed: 'Download failed: {title}',
      downloadPaused: 'Download paused: {title}',
      downloadCancelled: 'Download cancelled: {title}',
    },
    errors: {
      invalidUrl: 'Invalid URL provided',
      networkError: 'Network error occurred',
      downloadError: 'Download error: {error}',
      fileError: 'File error: {error}',
      permissionDenied: 'Permission denied',
      storageFull: 'Storage is full',
    },
  },
  hi: {
    common: {
      appName: 'RS टूलकिट',
      download: 'डाउनलोड',
      pause: 'रोकें',
      resume: 'फिर से शुरू करें',
      cancel: 'रद्द करें',
      retry: 'पुन: प्रयास करें',
      settings: 'सेटिंग्स',
      history: 'इतिहास',
      search: 'खोजें',
      filter: 'फ़िल्टर',
      sort: 'क्रमबद्ध',
      export: 'निर्यात',
      import: 'आयात',
      clear: 'साफ़ करें',
      delete: 'हटाएं',
      edit: 'संपादित करें',
      save: 'सहेजें',
      close: 'बंद करें',
      confirm: 'पुष्टि करें',
      yes: 'हाँ',
      no: 'नहीं',
      loading: 'लोड हो रहा है...',
      error: 'त्रुटि',
      success: 'सफल',
      warning: 'चेतावनी',
      info: 'जानकारी',
    },
    download: {
      title: 'डाउनलोड मैनेजर',
      enterUrl: 'URL दर्ज करें',
      startDownload: 'डाउनलोड शुरू करें',
      downloadComplete: 'डाउनलोड पूर्ण',
      downloadFailed: 'डाउनलोड विफल',
      downloading: 'डाउनलोड हो रहा है...',
      speed: 'गति',
      eta: 'समय शेष',
      progress: 'प्रगति',
    },
    history: {
      title: 'डाउनलोड इतिहास',
      noDownloads: 'अभी तक कोई डाउनलोड नहीं',
    },
    settings: {
      title: 'सेटिंग्स',
      general: 'सामान्य',
      download: 'डाउनलोड',
      resetToDefaults: 'डिफ़ॉल्ट पर रीसेट करें',
    },
    notifications: {
      downloadStarted: 'डाउनलोड शुरू: {title}',
      downloadComplete: 'डाउनलोड पूर्ण: {title}',
    },
    errors: {
      invalidUrl: 'अमान्य URL',
      networkError: 'नेटवर्क त्रुटि',
    },
  },
  es: {
    common: {
      appName: 'RS TOOLKIT',
      download: 'Descargar',
      pause: 'Pausar',
      resume: 'Reanudar',
      cancel: 'Cancelar',
      settings: 'Configuración',
      history: 'Historial',
      loading: 'Cargando...',
      error: 'Error',
      success: 'Éxito',
    },
    download: {
      title: 'Gestor de Descargas',
      downloading: 'Descargando...',
    },
    settings: {
      title: 'Configuración',
    },
  },
  fr: {
    common: {
      appName: 'RS TOOLKIT',
      download: 'Télécharger',
      pause: 'Pause',
      resume: 'Reprendre',
      cancel: 'Annuler',
      settings: 'Paramètres',
      history: 'Historique',
    },
    download: {
      title: 'Gestionnaire de Téléchargement',
    },
  },
  de: {
    common: {
      appName: 'RS TOOLKIT',
      download: 'Herunterladen',
      pause: 'Pause',
      resume: 'Fortsetzen',
      cancel: 'Abbrechen',
      settings: 'Einstellungen',
    },
  },
  ja: {
    common: {
      appName: 'RS ツールキット',
      download: 'ダウンロード',
      pause: '一時停止',
      resume: '再開',
      cancel: 'キャンセル',
      settings: '設定',
    },
  },
  zh: {
    common: {
      appName: 'RS 工具包',
      download: '下载',
      pause: '暂停',
      resume: '继续',
      cancel: '取消',
      settings: '设置',
    },
  },
  pt: {
    common: {
      appName: 'RS TOOLKIT',
      download: 'Baixar',
      pause: 'Pausar',
      resume: 'Retomar',
      cancel: 'Cancelar',
      settings: 'Configurações',
    },
  },
  ru: {
    common: {
      appName: 'RS TOOLKIT',
      download: 'Скачать',
      pause: 'Пауза',
      resume: 'Продолжить',
      cancel: 'Отмена',
      settings: 'Настройки',
    },
  },
  ar: {
    common: {
      appName: 'أدوات RS',
      download: 'تحميل',
      pause: 'إيقاف مؤقت',
      resume: 'استئناف',
      cancel: 'إلغاء',
      settings: 'الإعدادات',
    },
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// HOOK IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * useLanguage Hook
 * @description Internationalization with pluralization and interpolation
 * @param options Hook options
 * @returns Language controls and translation functions
 */
export function useLanguage(options: UseLanguageOptions = {}): UseLanguageReturn {
  const {
    defaultLanguage = 'en',
    storageKey = 'rs-toolkit-language',
    fallbackLanguage = 'en',
  } = options;

  // State
  const [language, setLanguageState] = useState<LanguageCode>(defaultLanguage);

  // ═══════════════════════════════════════════════════════════════════════════
  // LOAD FROM STORAGE
  // ═══════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    if (typeof window === 'undefined') return;

    try {
      const stored = localStorage.getItem(storageKey);
      if (stored && Object.keys(translations).includes(stored)) {
        setLanguageState(stored as LanguageCode);
      } else {
        // Detect browser language
        const browserLang = navigator.language.split('-')[0] as LanguageCode;
        if (Object.keys(translations).includes(browserLang)) {
          setLanguageState(browserLang);
        }
      }
    } catch (error) {
      console.error('Failed to load language:', error);
    }
  }, [storageKey]);

  // ═══════════════════════════════════════════════════════════════════════════
  // SET LANGUAGE
  // ═══════════════════════════════════════════════════════════════════════════

  const setLanguage = useCallback((lang: LanguageCode) => {
    setLanguageState(lang);

    try {
      localStorage.setItem(storageKey, lang);
    } catch (error) {
      console.error('Failed to save language:', error);
    }

    // Update HTML lang attribute
    if (typeof document !== 'undefined') {
      document.documentElement.lang = lang;
    }
  }, [storageKey]);

  // ═══════════════════════════════════════════════════════════════════════════
  // TRANSLATION FUNCTION
  // ═══════════════════════════════════════════════════════════════════════════

  const t = useCallback(
    (key: string, params?: Record<string, string | number>): string => {
      const keys = key.split('.');
      let value: string | TranslationValue | undefined = translations[language];

      // Navigate to the key
      for (const k of keys) {
        if (typeof value === 'object' && k in value) {
          value = value[k];
        } else {
          // Try fallback language
          value = translations[fallbackLanguage];
          for (const fk of keys) {
            if (typeof value === 'object' && fk in value) {
              value = value[fk];
            } else {
              return key; // Return key if not found
            }
          }
          break;
        }
      }

      if (typeof value !== 'string') {
        return key;
      }

      // Interpolate parameters
      if (params) {
        return Object.entries(params).reduce(
          (str, [paramKey, paramValue]) =>
            str.replace(new RegExp(`\\{${paramKey}\\}`, 'g'), String(paramValue)),
          value
        );
      }

      return value;
    },
    [language, fallbackLanguage]
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // PLURALIZATION
  // ═══════════════════════════════════════════════════════════════════════════

  const plural = useCallback(
    (key: string, count: number, params?: Record<string, string | number>): string => {
      const pluralRules = new Intl.PluralRules(language);
      const rule = pluralRules.select(count);

      // Try plural key first
      const pluralKey = `${key}_${rule}`;
      const translated = t(pluralKey, { ...params, count });

      // If no specific plural form, fall back to base key
      if (translated === pluralKey) {
        return t(key, { ...params, count });
      }

      return translated;
    },
    [t, language]
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // RTL CHECK
  // ═══════════════════════════════════════════════════════════════════════════

  const isRTL = useMemo(() => {
    return LANGUAGES.find((l) => l.code === language)?.rtl || false;
  }, [language]);

  const direction = useMemo(() => (isRTL ? 'rtl' : 'ltr'), [isRTL]);

  // ═══════════════════════════════════════════════════════════════════════════
  // FORMATTING
  // ═══════════════════════════════════════════════════════════════════════════

  const formatNumber = useCallback(
    (num: number, options?: Intl.NumberFormatOptions): string => {
      return new Intl.NumberFormat(language, options).format(num);
    },
    [language]
  );

  const formatDate = useCallback(
    (date: Date, options?: Intl.DateTimeFormatOptions): string => {
      return new Intl.DateTimeFormat(language, options).format(date);
    },
    [language]
  );

  const formatRelativeTime = useCallback(
    (value: number, unit: Intl.RelativeTimeFormatUnit): string => {
      return new Intl.RelativeTimeFormat(language, { numeric: 'auto' }).format(
        value,
        unit
      );
    },
    [language]
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // RETURN
  // ═══════════════════════════════════════════════════════════════════════════

  return {
    language,
    setLanguage,
    languages: LANGUAGES,
    t,
    plural,
    isRTL,
    direction,
    formatNumber,
    formatDate,
    formatRelativeTime,
  };
}

export default useLanguage;
