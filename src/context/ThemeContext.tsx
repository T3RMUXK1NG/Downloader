/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    THEME CONTEXT v3.0.1 ULTIMATE NEXUS                        ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Theme context provider with next-themes                       ║
 * ║  Features: Light/dark/system, accent colors, animations, persistence       ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module context/ThemeContext
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

'use client';

import React, { createContext, useContext, useCallback, useEffect, useMemo, useState } from 'react';

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

export interface ThemeContextValue {
  // Theme
  theme: Theme;
  resolvedTheme: ResolvedTheme;
  isDark: boolean;
  isLight: boolean;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;

  // Accent color
  accentColor: string;
  setAccentColor: (color: string) => void;
  accentColors: AccentColor[];

  // System preference
  systemPreference: ResolvedTheme;

  // Animations
  animationsEnabled: boolean;
  setAnimationsEnabled: (enabled: boolean) => void;
  reducedMotion: boolean;

  // CSS Variables
  cssVariables: Record<string, string>;
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

const STORAGE_KEY_THEME = 'rs-toolkit-theme';
const STORAGE_KEY_ACCENT = 'rs-toolkit-accent';
const STORAGE_KEY_ANIMATIONS = 'rs-toolkit-animations';

// ═══════════════════════════════════════════════════════════════════════════════
// CONTEXT
// ═══════════════════════════════════════════════════════════════════════════════

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

// ═══════════════════════════════════════════════════════════════════════════════
// PROVIDER
// ═══════════════════════════════════════════════════════════════════════════════

export interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: Theme;
  defaultAccentColor?: string;
  defaultAnimationsEnabled?: boolean;
  storageKey?: string;
  enableSystem?: boolean;
}

export function ThemeProvider({
  children,
  defaultTheme = 'system',
  defaultAccentColor = '#10b981',
  defaultAnimationsEnabled = true,
  storageKey = STORAGE_KEY_THEME,
  enableSystem = true,
}: ThemeProviderProps): React.ReactElement {
  // State
  const [theme, setThemeState] = useState<Theme>(defaultTheme);
  const [resolvedTheme, setResolvedTheme] = useState<ResolvedTheme>('dark');
  const [accentColor, setAccentColorState] = useState<string>(defaultAccentColor);
  const [animationsEnabled, setAnimationsEnabledState] = useState(defaultAnimationsEnabled);
  const [systemPreference, setSystemPreference] = useState<ResolvedTheme>('dark');
  const [reducedMotion, setReducedMotion] = useState(false);

  // ═════════════════════════════════════════════════════════════════════════
  // SYSTEM PREFERENCE DETECTION
  // ═════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    if (!enableSystem || typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    const updatePreferences = () => {
      setSystemPreference(mediaQuery.matches ? 'dark' : 'light');
      setReducedMotion(motionQuery.matches);
    };

    updatePreferences();

    mediaQuery.addEventListener('change', updatePreferences);
    motionQuery.addEventListener('change', updatePreferences);

    return () => {
      mediaQuery.removeEventListener('change', updatePreferences);
      motionQuery.removeEventListener('change', updatePreferences);
    };
  }, [enableSystem]);

  // ═════════════════════════════════════════════════════════════════════════
  // LOAD FROM STORAGE
  // ═════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    if (typeof window === 'undefined') return;

    try {
      const storedTheme = localStorage.getItem(storageKey);
      if (storedTheme && ['light', 'dark', 'system'].includes(storedTheme)) {
        setThemeState(storedTheme as Theme);
      }

      const storedAccent = localStorage.getItem(STORAGE_KEY_ACCENT);
      if (storedAccent) {
        setAccentColorState(storedAccent);
      }

      const storedAnimations = localStorage.getItem(STORAGE_KEY_ANIMATIONS);
      if (storedAnimations !== null) {
        setAnimationsEnabledState(storedAnimations === 'true');
      }
    } catch (error) {
      console.error('Failed to load theme from storage:', error);
    }
  }, [storageKey]);

  // ═════════════════════════════════════════════════════════════════════════
  // RESOLVE THEME
  // ═════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    const resolved = theme === 'system' ? systemPreference : theme;
    setResolvedTheme(resolved);
  }, [theme, systemPreference]);

  // ═════════════════════════════════════════════════════════════════════════
  // APPLY THEME TO DOM
  // ═════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const root = document.documentElement;

    // Apply theme class
    root.classList.remove('light', 'dark');
    root.classList.add(resolvedTheme);

    // Apply color scheme
    root.style.colorScheme = resolvedTheme;

    // Apply accent color
    root.style.setProperty('--accent', accentColor);
    root.style.setProperty('--accent-foreground', resolvedTheme === 'dark' ? '#ffffff' : '#000000');

    // Apply animation preference
    if (!animationsEnabled || reducedMotion) {
      root.style.setProperty('--animation-duration', '0s');
    } else {
      root.style.removeProperty('--animation-duration');
    }
  }, [resolvedTheme, accentColor, animationsEnabled, reducedMotion]);

  // ═════════════════════════════════════════════════════════════════════════
  // THEME ACTIONS
  // ═════════════════════════════════════════════════════════════════════════

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
      localStorage.setItem(STORAGE_KEY_ACCENT, color);
    } catch (error) {
      console.error('Failed to save accent color:', error);
    }
  }, []);

  const setAnimationsEnabled = useCallback((enabled: boolean) => {
    setAnimationsEnabledState(enabled);

    try {
      localStorage.setItem(STORAGE_KEY_ANIMATIONS, String(enabled));
    } catch (error) {
      console.error('Failed to save animation preference:', error);
    }
  }, []);

  // ═════════════════════════════════════════════════════════════════════════
  // CSS VARIABLES
  // ═════════════════════════════════════════════════════════════════════════

  const cssVariables = useMemo(() => ({
    '--accent': accentColor,
    '--accent-foreground': resolvedTheme === 'dark' ? '#ffffff' : '#000000',
    '--color-scheme': resolvedTheme,
    '--animation-duration': (!animationsEnabled || reducedMotion) ? '0s' : undefined,
  } as Record<string, string>), [accentColor, resolvedTheme, animationsEnabled, reducedMotion]);

  // ═════════════════════════════════════════════════════════════════════════
  // CONTEXT VALUE
  // ═════════════════════════════════════════════════════════════════════════

  const value = useMemo<ThemeContextValue>(
    () => ({
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
      animationsEnabled,
      setAnimationsEnabled,
      reducedMotion,
      cssVariables,
    }),
    [
      theme,
      resolvedTheme,
      setTheme,
      toggleTheme,
      accentColor,
      setAccentColor,
      systemPreference,
      animationsEnabled,
      setAnimationsEnabled,
      reducedMotion,
      cssVariables,
    ]
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// HOOK
// ═══════════════════════════════════════════════════════════════════════════════

export function useThemeContext(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useThemeContext must be used within a ThemeProvider');
  }
  return context;
}

export default ThemeContext;
