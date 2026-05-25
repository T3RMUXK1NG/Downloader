/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    USE THEME HOOK v3.0.1 ULTIMATE NEXUS                       ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Theme management hook with system preference detection         ║
 * ║  Features: Light/dark/system, persistence, accent colors, animations        ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module hooks/useTheme
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

'use client';

import { useCallback, useEffect, useState } from 'react';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export type Theme = 'light' | 'dark' | 'system';
export type ResolvedTheme = 'light' | 'dark';

export interface AccentColor {
  name: string;
  value: string;
  lightValue?: string;
}

export interface UseThemeOptions {
  /** Storage key */
  storageKey?: string;
  /** Default theme */
  defaultTheme?: Theme;
  /** Default accent color */
  defaultAccent?: string;
  /** Enable animations */
  enableAnimations?: boolean;
}

export interface UseThemeReturn {
  /** Current theme setting */
  theme: Theme;
  /** Resolved theme (light or dark) */
  resolvedTheme: ResolvedTheme;
  /** Is dark mode */
  isDark: boolean;
  /** Is light mode */
  isLight: boolean;
  /** Set theme */
  setTheme: (theme: Theme) => void;
  /** Toggle theme */
  toggleTheme: () => void;
  /** Accent color */
  accentColor: string;
  /** Set accent color */
  setAccentColor: (color: string) => void;
  /** Available accent colors */
  accentColors: AccentColor[];
  /** System preference */
  systemPreference: ResolvedTheme;
}

// ═══════════════════════════════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════════════════════════════

export const ACCENT_COLORS: AccentColor[] = [
  { name: 'Emerald', value: '#10b981', lightValue: '#059669' },
  { name: 'Violet', value: '#8b5cf6', lightValue: '#7c3aed' },
  { name: 'Rose', value: '#f43f5e', lightValue: '#e11d48' },
  { name: 'Amber', value: '#f59e0b', lightValue: '#d97706' },
  { name: 'Cyan', value: '#06b6d4', lightValue: '#0891b2' },
  { name: 'Lime', value: '#84cc16', lightValue: '#65a30d' },
  { name: 'Orange', value: '#f97316', lightValue: '#ea580c' },
  { name: 'Pink', value: '#ec4899', lightValue: '#db2777' },
  { name: 'Teal', value: '#14b8a6', lightValue: '#0d9488' },
  { name: 'Sky', value: '#0ea5e9', lightValue: '#0284c7' },
];

// ═══════════════════════════════════════════════════════════════════════════════
// HOOK IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * useTheme Hook
 * @description Theme management with system preference detection and persistence
 * @param options Hook options
 * @returns Theme controls and state
 */
export function useTheme(options: UseThemeOptions = {}): UseThemeReturn {
  const {
    storageKey = 'rs-toolkit-theme',
    defaultTheme = 'system',
    defaultAccent = '#10b981',
    enableAnimations = true,
  } = options;

  // State
  const [theme, setThemeState] = useState<Theme>(defaultTheme);
  const [resolvedTheme, setResolvedTheme] = useState<ResolvedTheme>('dark');
  const [accentColor, setAccentColorState] = useState<string>(defaultAccent);
  const [systemPreference, setSystemPreference] = useState<ResolvedTheme>('dark');

  // ═══════════════════════════════════════════════════════════════════════════
  // SYSTEM PREFERENCE DETECTION
  // ═══════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e: MediaQueryListEvent | MediaQueryList) => {
      setSystemPreference(e.matches ? 'dark' : 'light');
    };

    // Initial check
    handleChange(mediaQuery);

    // Listen for changes
    mediaQuery.addEventListener('change', handleChange);

    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);

  // ═══════════════════════════════════════════════════════════════════════════
  // LOAD FROM STORAGE
  // ═══════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    if (typeof window === 'undefined') return;

    try {
      const storedTheme = localStorage.getItem(storageKey);
      const storedAccent = localStorage.getItem(`${storageKey}-accent`);

      if (storedTheme && ['light', 'dark', 'system'].includes(storedTheme)) {
        setThemeState(storedTheme as Theme);
      }

      if (storedAccent) {
        setAccentColorState(storedAccent);
      }
    } catch (error) {
      console.error('Failed to load theme from storage:', error);
    }
  }, [storageKey]);

  // ═══════════════════════════════════════════════════════════════════════════
  // RESOLVE THEME
  // ═══════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    const resolved = theme === 'system' ? systemPreference : theme;
    setResolvedTheme(resolved);
  }, [theme, systemPreference]);

  // ═══════════════════════════════════════════════════════════════════════════
  // APPLY THEME TO DOM
  // ═══════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const root = document.documentElement;

    // Apply dark/light class
    if (resolvedTheme === 'dark') {
      root.classList.add('dark');
      root.classList.remove('light');
    } else {
      root.classList.add('light');
      root.classList.remove('dark');
    }

    // Apply color scheme
    root.style.colorScheme = resolvedTheme;

    // Apply accent color as CSS variable
    root.style.setProperty('--accent', accentColor);
    root.style.setProperty('--accent-foreground', resolvedTheme === 'dark' ? '#ffffff' : '#000000');

    // Apply animation preference
    if (!enableAnimations) {
      root.style.setProperty('--animation-duration', '0s');
    } else {
      root.style.removeProperty('--animation-duration');
    }
  }, [resolvedTheme, accentColor, enableAnimations]);

  // ═══════════════════════════════════════════════════════════════════════════
  // THEME FUNCTIONS
  // ═══════════════════════════════════════════════════════════════════════════

  const setTheme = useCallback((newTheme: Theme) => {
    setThemeState(newTheme);

    try {
      localStorage.setItem(storageKey, newTheme);
    } catch (error) {
      console.error('Failed to save theme:', error);
    }
  }, [storageKey]);

  const toggleTheme = useCallback(() => {
    const nextTheme = resolvedTheme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
  }, [resolvedTheme, setTheme]);

  const setAccentColor = useCallback((color: string) => {
    setAccentColorState(color);

    try {
      localStorage.setItem(`${storageKey}-accent`, color);
    } catch (error) {
      console.error('Failed to save accent color:', error);
    }
  }, [storageKey]);

  // ═══════════════════════════════════════════════════════════════════════════
  // RETURN
  // ═══════════════════════════════════════════════════════════════════════════

  return {
    theme,
    resolvedTheme,
    isDark: resolvedTheme === 'dark',
    isLight: resolvedTheme === 'light',
    setTheme,
    toggleTheme,
    accentColor,
    setAccentColor,
    accentColors: ACCENT_COLORS,
    systemPreference,
  };
}

export default useTheme;
