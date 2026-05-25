/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   THEME TOGGLE v3.0.1 ULTIMATE NEXUS                         ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Dark/Light theme toggle with system detection                 ║
 * ║  Features: Animated transitions, system preference, persistent storage       ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sun, Moon, Monitor } from 'lucide-react';
import { cn } from '@/lib/utils';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export type Theme = 'light' | 'dark' | 'system';

export interface ThemeToggleProps {
  /** Current theme */
  theme?: Theme;
  /** On theme change */
  onThemeChange?: (theme: Theme) => void;
  /** Show label */
  showLabel?: boolean;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Show system option */
  showSystemOption?: boolean;
  /** Additional class names */
  className?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// THEME CONTEXT
// ═══════════════════════════════════════════════════════════════════════════════

interface ThemeContextValue {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  resolvedTheme: 'light' | 'dark';
}

const ThemeContext = React.createContext<ThemeContextValue | undefined>(undefined);

export const useTheme = (): ThemeContextValue => {
  const context = React.useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: Theme;
  storageKey?: string;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  defaultTheme = 'system',
  storageKey = 'rs-toolkit-theme',
}) => {
  const [theme, setThemeState] = React.useState<Theme>(defaultTheme);
  const [resolvedTheme, setResolvedTheme] = React.useState<'light' | 'dark'>('dark');

  // Initialize theme from localStorage or system preference
  React.useEffect(() => {
    const stored = localStorage.getItem(storageKey) as Theme | null;
    if (stored && ['light', 'dark', 'system'].includes(stored)) {
      setThemeState(stored);
    }
  }, [storageKey]);

  // Update resolved theme
  React.useEffect(() => {
    const updateResolvedTheme = () => {
      if (theme === 'system') {
        const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        setResolvedTheme(isDark ? 'dark' : 'light');
      } else {
        setResolvedTheme(theme);
      }
    };

    updateResolvedTheme();

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = () => {
      if (theme === 'system') {
        updateResolvedTheme();
      }
    };
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, [theme]);

  // Apply theme to document
  React.useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('light', 'dark');
    root.classList.add(resolvedTheme);
  }, [resolvedTheme]);

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem(storageKey, newTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, resolvedTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export const ThemeToggle: React.FC<ThemeToggleProps> = ({
  theme: controlledTheme,
  onThemeChange,
  showLabel = false,
  size = 'md',
  showSystemOption = true,
  className,
}) => {
  const context = React.useContext(ThemeContext);
  const currentTheme = controlledTheme ?? context?.theme ?? 'system';
  const resolvedTheme = context?.resolvedTheme ?? 'dark';

  const [showDropdown, setShowDropdown] = React.useState(false);
  const dropdownRef = React.useRef<HTMLDivElement>(null);

  const setTheme = (newTheme: Theme) => {
    context?.setTheme(newTheme);
    onThemeChange?.(newTheme);
    setShowDropdown(false);
  };

  // Close dropdown on outside click
  React.useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
  };

  const iconSizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  const themes: { value: Theme; label: string; icon: React.ReactNode }[] = [
    { value: 'light', label: 'Light', icon: <Sun className={iconSizes[size]} /> },
    { value: 'dark', label: 'Dark', icon: <Moon className={iconSizes[size]} /> },
    ...(showSystemOption
      ? [{ value: 'system' as Theme, label: 'System', icon: <Monitor className={iconSizes[size]} /> }]
      : []),
  ];

  const currentThemeData = themes.find((t) => t.value === currentTheme) || themes[1];

  return (
    <div ref={dropdownRef} className={cn('relative', className)}>
      {/* Toggle button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setShowDropdown(!showDropdown)}
        className={cn(
          'relative rounded-xl flex items-center justify-center',
          'bg-muted/50 hover:bg-muted border border-border/50',
          'transition-colors focus:outline-none focus:ring-2 focus:ring-primary/50',
          sizeClasses[size]
        )}
        aria-label={`Theme: ${currentThemeData.label}`}
        aria-expanded={showDropdown}
        aria-haspopup="listbox"
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={currentTheme}
            initial={{ opacity: 0, rotate: -90, scale: 0 }}
            animate={{ opacity: 1, rotate: 0, scale: 1 }}
            exit={{ opacity: 0, rotate: 90, scale: 0 }}
            transition={{ duration: 0.2 }}
            className="text-foreground"
          >
            {currentThemeData.icon}
          </motion.div>
        </AnimatePresence>

        {/* Glow effect */}
        <motion.div
          className="absolute inset-0 rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-500/20 dark:from-purple-500/20 dark:to-blue-500/20"
          initial={{ opacity: 0 }}
          animate={{ opacity: showDropdown ? 1 : 0 }}
        />
      </motion.button>

      {/* Dropdown */}
      <AnimatePresence>
        {showDropdown && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 top-full mt-2 z-50 min-w-[140px] rounded-xl border border-border bg-popover p-1 shadow-xl"
            role="listbox"
          >
            {themes.map((themeOption, index) => (
              <motion.button
                key={themeOption.value}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                onClick={() => setTheme(themeOption.value)}
                className={cn(
                  'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors',
                  currentTheme === themeOption.value
                    ? 'bg-primary/10 text-primary'
                    : 'hover:bg-muted/50 text-foreground'
                )}
                role="option"
                aria-selected={currentTheme === themeOption.value}
              >
                {themeOption.icon}
                <span>{themeOption.label}</span>
                {currentTheme === themeOption.value && (
                  <motion.div
                    layoutId="theme-indicator"
                    className="ml-auto w-1.5 h-1.5 rounded-full bg-primary"
                  />
                )}
              </motion.button>
            ))}

            {/* Divider with system info */}
            {showSystemOption && currentTheme === 'system' && (
              <div className="mt-1 pt-2 border-t border-border/50">
                <p className="px-3 text-xs text-muted-foreground">
                  System preference: {resolvedTheme === 'dark' ? 'Dark' : 'Light'}
                </p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Label */}
      {showLabel && (
        <span className="ml-2 text-sm text-muted-foreground">{currentThemeData.label}</span>
      )}
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// MINI TOGGLE COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export interface MiniThemeToggleProps {
  /** On toggle */
  onToggle?: () => void;
  /** Is dark mode */
  isDark?: boolean;
  /** Size */
  size?: 'sm' | 'md' | 'lg';
  /** Additional class names */
  className?: string;
}

export const MiniThemeToggle: React.FC<MiniThemeToggleProps> = ({
  onToggle,
  isDark = true,
  size = 'md',
  className,
}) => {
  const sizeClasses = {
    sm: 'w-12 h-6',
    md: 'w-14 h-7',
    lg: 'w-16 h-8',
  };

  const thumbSizes = {
    sm: 'w-5 h-5',
    md: 'w-6 h-6',
    lg: 'w-7 h-7',
  };

  return (
    <motion.button
      onClick={onToggle}
      className={cn(
        'relative rounded-full flex items-center px-1 transition-colors duration-300',
        isDark ? 'bg-slate-700' : 'bg-amber-100',
        sizeClasses[size],
        className
      )}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      {/* Background stars (dark mode) */}
      <AnimatePresence>
        {isDark && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 overflow-hidden rounded-full"
          >
            {[...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 bg-white rounded-full"
                style={{
                  top: `${20 + i * 25}%`,
                  left: `${10 + i * 20}%`,
                }}
                animate={{ opacity: [0.3, 1, 0.3] }}
                transition={{ duration: 2, repeat: Infinity, delay: i * 0.3 }}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Thumb */}
      <motion.div
        className={cn(
          'rounded-full flex items-center justify-center shadow-md',
          thumbSizes[size],
          isDark ? 'bg-slate-900' : 'bg-amber-400'
        )}
        animate={{ x: isDark ? 28 : 0 }}
        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
      >
        <AnimatePresence mode="wait">
          {isDark ? (
            <motion.div
              key="moon"
              initial={{ opacity: 0, rotate: -90 }}
              animate={{ opacity: 1, rotate: 0 }}
              exit={{ opacity: 0, rotate: 90 }}
            >
              <Moon className="w-3.5 h-3.5 text-slate-300" />
            </motion.div>
          ) : (
            <motion.div
              key="sun"
              initial={{ opacity: 0, rotate: 90 }}
              animate={{ opacity: 1, rotate: 0 }}
              exit={{ opacity: 0, rotate: -90 }}
            >
              <Sun className="w-3.5 h-3.5 text-amber-600" />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.button>
  );
};

export default ThemeToggle;
