/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    USE KEYBOARD HOOK v3.0.1 ULTIMATE NEXUS                    ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Keyboard shortcuts management hook                            ║
 * ║  Features: Global shortcuts, combos, modifiers, scope, help panel           ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module hooks/useKeyboard
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface KeyboardShortcut {
  id: string;
  key: string;
  ctrl?: boolean;
  alt?: boolean;
  shift?: boolean;
  meta?: boolean;
  description: string;
  category?: string;
  handler: (event: KeyboardEvent) => void;
  preventDefault?: boolean;
  stopPropagation?: boolean;
  enabled?: boolean;
  scope?: string;
}

export interface UseKeyboardOptions {
  /** Enable keyboard shortcuts */
  enabled?: boolean;
  /** Default scope */
  scope?: string;
  /** Show help on ? key */
  showHelpOnQuestion?: boolean;
}

export interface UseKeyboardReturn {
  /** Register a shortcut */
  register: (shortcut: KeyboardShortcut) => void;
  /** Unregister a shortcut */
  unregister: (id: string) => void;
  /** Register multiple shortcuts */
  registerAll: (shortcuts: KeyboardShortcut[]) => void;
  /** Clear all shortcuts */
  clear: () => void;
  /** Set scope */
  setScope: (scope: string) => void;
  /** Current scope */
  scope: string;
  /** All registered shortcuts */
  shortcuts: KeyboardShortcut[];
  /** Show help panel */
  showHelp: boolean;
  /** Toggle help panel */
  toggleHelp: () => void;
}

// ═══════════════════════════════════════════════════════════════════════════════
// DEFAULT SHORTCUTS
// ═══════════════════════════════════════════════════════════════════════════════

export const DEFAULT_SHORTCUTS: KeyboardShortcut[] = [
  {
    id: 'toggle-theme',
    key: 'd',
    ctrl: true,
    description: 'Toggle dark/light theme',
    category: 'General',
    handler: () => {
      document.documentElement.classList.toggle('dark');
    },
  },
  {
    id: 'focus-search',
    key: 'k',
    ctrl: true,
    description: 'Focus search input',
    category: 'General',
    handler: () => {
      const searchInput = document.querySelector<HTMLInputElement>('[data-search-input]');
      searchInput?.focus();
    },
  },
  {
    id: 'new-download',
    key: 'n',
    ctrl: true,
    description: 'New download',
    category: 'Download',
    handler: () => {
      const newDownloadBtn = document.querySelector<HTMLButtonElement>('[data-new-download]');
      newDownloadBtn?.click();
    },
  },
];

// ═══════════════════════════════════════════════════════════════════════════════
// HOOK IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * useKeyboard Hook
 * @description Keyboard shortcuts management with scope support
 * @param options Hook options
 * @returns Keyboard controls and state
 */
export function useKeyboard(options: UseKeyboardOptions = {}): UseKeyboardReturn {
  const {
    enabled = true,
    scope: initialScope = 'global',
    showHelpOnQuestion = true,
  } = options;

  // State
  const [shortcuts, setShortcuts] = useState<KeyboardShortcut[]>([]);
  const [scope, setScope] = useState(initialScope);
  const [showHelp, setShowHelp] = useState(false);

  // Refs
  const shortcutsRef = useRef<Map<string, KeyboardShortcut>>(new Map());
  const pressedKeysRef = useRef<Set<string>>(new Set());

  // ═══════════════════════════════════════════════════════════════════════════
  // REGISTER SHORTCUT
  // ═══════════════════════════════════════════════════════════════════════════

  const register = useCallback((shortcut: KeyboardShortcut) => {
    shortcutsRef.current.set(shortcut.id, shortcut);
    setShortcuts(Array.from(shortcutsRef.current.values()));
  }, []);

  const unregister = useCallback((id: string) => {
    shortcutsRef.current.delete(id);
    setShortcuts(Array.from(shortcutsRef.current.values()));
  }, []);

  const registerAll = useCallback((newShortcuts: KeyboardShortcut[]) => {
    newShortcuts.forEach((shortcut) => {
      shortcutsRef.current.set(shortcut.id, shortcut);
    });
    setShortcuts(Array.from(shortcutsRef.current.values()));
  }, []);

  const clear = useCallback(() => {
    shortcutsRef.current.clear();
    setShortcuts([]);
  }, []);

  // ═══════════════════════════════════════════════════════════════════════════
  // HELP PANEL
  // ═══════════════════════════════════════════════════════════════════════════

  const toggleHelp = useCallback(() => {
    setShowHelp((prev) => !prev);
  }, []);

  // ═══════════════════════════════════════════════════════════════════════════
  // KEYBOARD EVENT HANDLER
  // ═══════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    if (!enabled) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      // Ignore if typing in input fields
      const target = event.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        // Allow Escape key
        if (event.key !== 'Escape') {
          return;
        }
      }

      // Track pressed keys
      pressedKeysRef.current.add(event.key);

      // Check for help shortcut (?)
      if (showHelpOnQuestion && event.key === '?' && !event.ctrlKey && !event.altKey && !event.metaKey) {
        toggleHelp();
        return;
      }

      // Escape to close help
      if (event.key === 'Escape' && showHelp) {
        setShowHelp(false);
        return;
      }

      // Find matching shortcut
      for (const shortcut of shortcutsRef.current.values()) {
        // Check if shortcut is enabled
        if (shortcut.enabled === false) continue;

        // Check scope
        if (shortcut.scope && shortcut.scope !== scope && shortcut.scope !== 'global') {
          continue;
        }

        // Check key
        if (shortcut.key.toLowerCase() !== event.key.toLowerCase()) continue;

        // Check modifiers
        if (!!shortcut.ctrl !== event.ctrlKey) continue;
        if (!!shortcut.alt !== event.altKey) continue;
        if (!!shortcut.shift !== event.shiftKey) continue;
        if (!!shortcut.meta !== event.metaKey) continue;

        // Execute handler
        if (shortcut.preventDefault !== false) {
          event.preventDefault();
        }
        if (shortcut.stopPropagation) {
          event.stopPropagation();
        }

        shortcut.handler(event);
        return;
      }
    };

    const handleKeyUp = (event: KeyboardEvent) => {
      pressedKeysRef.current.delete(event.key);
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [enabled, scope, showHelp, showHelpOnQuestion, toggleHelp]);

  // ═══════════════════════════════════════════════════════════════════════════
  // REGISTER DEFAULT SHORTCUTS
  // ═══════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    registerAll(DEFAULT_SHORTCUTS);
  }, [registerAll]);

  // ═══════════════════════════════════════════════════════════════════════════
  // RETURN
  // ═══════════════════════════════════════════════════════════════════════════

  return {
    register,
    unregister,
    registerAll,
    clear,
    setScope,
    scope,
    shortcuts,
    showHelp,
    toggleHelp,
  };
}

export default useKeyboard;
