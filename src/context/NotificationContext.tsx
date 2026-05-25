/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    NOTIFICATION CONTEXT v3.0.1 ULTIMATE NEXUS                ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Notification context provider                                 ║
 * ║  Features: Toast notifications, alerts, badges, persistence, actions        ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module context/NotificationContext
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

'use client';

import React, { createContext, useContext, useCallback, useEffect, useRef, useState } from 'react';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export type NotificationType = 'info' | 'success' | 'warning' | 'error';
export type NotificationPosition = 'top-left' | 'top-right' | 'top-center' | 'bottom-left' | 'bottom-right' | 'bottom-center';

export interface NotificationAction {
  label: string;
  onClick: () => void;
  primary?: boolean;
}

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message?: string;
  icon?: string;
  duration?: number;
  persistent?: boolean;
  actions?: NotificationAction[];
  timestamp: Date;
  read: boolean;
  group?: string;
  data?: Record<string, unknown>;
}

export interface NotificationContextValue {
  // Notifications
  notifications: Notification[];
  visibleNotifications: Notification[];
  unreadCount: number;
  position: NotificationPosition;

  // Show notifications
  show: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => string;
  info: (title: string, message?: string) => string;
  success: (title: string, message?: string) => string;
  warning: (title: string, message?: string) => string;
  error: (title: string, message?: string) => string;

  // Dismiss notifications
  dismiss: (id: string) => void;
  dismissAll: () => void;

  // Mark as read
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;

  // Clear
  clear: () => void;
  clearGroup: (group: string) => void;

  // Settings
  setPosition: (position: NotificationPosition) => void;
  setMaxVisible: (max: number) => void;
  setEnableSounds: (enabled: boolean) => void;

  // Events
  onNotification: (callback: (notification: Notification) => void) => () => void;
}

// ═══════════════════════════════════════════════════════════════════════════════
// CONTEXT
// ═══════════════════════════════════════════════════════════════════════════════

const NotificationContext = createContext<NotificationContextValue | undefined>(undefined);

// ═══════════════════════════════════════════════════════════════════════════════
// PROVIDER
// ═══════════════════════════════════════════════════════════════════════════════

export interface NotificationProviderProps {
  children: React.ReactNode;
  position?: NotificationPosition;
  maxVisible?: number;
  enableSounds?: boolean;
  persist?: boolean;
  storageKey?: string;
}

export function NotificationProvider({
  children,
  position: initialPosition = 'top-right',
  maxVisible = 5,
  enableSounds = true,
  persist = true,
  storageKey = 'rs-toolkit-notifications',
}: NotificationProviderProps): React.ReactElement {
  // State
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [position, setPosition] = useState<NotificationPosition>(initialPosition);
  const [maxVisibleState, setMaxVisibleState] = useState(maxVisible);
  const [enableSoundsState, setEnableSoundsState] = useState(enableSounds);

  // Refs
  const timeoutsRef = useRef<Map<string, NodeJS.Timeout>>(new Map());
  const callbacksRef = useRef<Set<(notification: Notification) => void>>(new Set());

  // ═════════════════════════════════════════════════════════════════════════
  // LOAD FROM STORAGE
  // ═════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    if (!persist || typeof window === 'undefined') return;

    try {
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        const parsed = JSON.parse(stored) as Notification[];
        setNotifications(
          parsed.map((n) => ({
            ...n,
            timestamp: new Date(n.timestamp),
          }))
        );
      }
    } catch (error) {
      console.error('Failed to load notifications:', error);
    }
  }, [persist, storageKey]);

  // ═════════════════════════════════════════════════════════════════════════
  // SAVE TO STORAGE
  // ═════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    if (!persist || typeof window === 'undefined') return;

    try {
      localStorage.setItem(storageKey, JSON.stringify(notifications));
    } catch (error) {
      console.error('Failed to save notifications:', error);
    }
  }, [notifications, persist, storageKey]);

  // ═════════════════════════════════════════════════════════════════════════
  // SHOW NOTIFICATION
  // ═════════════════════════════════════════════════════════════════════════

  const show = useCallback(
    (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>): string => {
      const id = `notif_${Date.now()}_${Math.random().toString(36).substring(2, 10)}`;
      const duration = notification.duration ?? 5000;
      const persistent = notification.persistent ?? false;

      const newNotification: Notification = {
        ...notification,
        id,
        timestamp: new Date(),
        read: false,
      };

      setNotifications((prev) => [newNotification, ...prev]);

      // Play sound
      if (enableSoundsState && typeof window !== 'undefined') {
        playNotificationSound(notification.type);
      }

      // Notify callbacks
      callbacksRef.current.forEach((callback) => callback(newNotification));

      // Auto-dismiss
      if (!persistent && duration > 0) {
        const timeout = setTimeout(() => {
          setNotifications((prev) => prev.filter((n) => n.id !== id));
          timeoutsRef.current.delete(id);
        }, duration);
        timeoutsRef.current.set(id, timeout);
      }

      return id;
    },
    [enableSoundsState]
  );

  // ═════════════════════════════════════════════════════════════════════════
  // HELPER FUNCTIONS
  // ═════════════════════════════════════════════════════════════════════════

  const info = useCallback(
    (title: string, message?: string): string => {
      return show({ type: 'info', title, message });
    },
    [show]
  );

  const success = useCallback(
    (title: string, message?: string): string => {
      return show({ type: 'success', title, message });
    },
    [show]
  );

  const warning = useCallback(
    (title: string, message?: string): string => {
      return show({ type: 'warning', title, message });
    },
    [show]
  );

  const errorNotif = useCallback(
    (title: string, message?: string): string => {
      return show({ type: 'error', title, message, duration: 10000 });
    },
    [show]
  );

  // ═════════════════════════════════════════════════════════════════════════
  // DISMISS
  // ═════════════════════════════════════════════════════════════════════════

  const dismiss = useCallback((id: string) => {
    const timeout = timeoutsRef.current.get(id);
    if (timeout) {
      clearTimeout(timeout);
      timeoutsRef.current.delete(id);
    }
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const dismissAll = useCallback(() => {
    timeoutsRef.current.forEach((timeout) => clearTimeout(timeout));
    timeoutsRef.current.clear();
    setNotifications([]);
  }, []);

  // ═════════════════════════════════════════════════════════════════════════
  // MARK AS READ
  // ═════════════════════════════════════════════════════════════════════════

  const markAsRead = useCallback((id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  }, []);

  // ═════════════════════════════════════════════════════════════════════════
  // CLEAR
  // ═════════════════════════════════════════════════════════════════════════

  const clear = useCallback(() => {
    dismissAll();
  }, [dismissAll]);

  const clearGroup = useCallback((group: string) => {
    setNotifications((prev) => prev.filter((n) => n.group !== group));
  }, []);

  // ═════════════════════════════════════════════════════════════════════════
  // SETTINGS
  // ═════════════════════════════════════════════════════════════════════════

  const setPositionHandler = useCallback((newPosition: NotificationPosition) => {
    setPosition(newPosition);
  }, []);

  const setMaxVisibleHandler = useCallback((max: number) => {
    setMaxVisibleState(max);
  }, []);

  const setEnableSoundsHandler = useCallback((enabled: boolean) => {
    setEnableSoundsState(enabled);
  }, []);

  // ═════════════════════════════════════════════════════════════════════════
  // EVENTS
  // ═════════════════════════════════════════════════════════════════════════

  const onNotification = useCallback((callback: (notification: Notification) => void) => {
    callbacksRef.current.add(callback);
    return () => {
      callbacksRef.current.delete(callback);
    };
  }, []);

  // ═════════════════════════════════════════════════════════════════════════
  // COMPUTED
  // ═════════════════════════════════════════════════════════════════════════

  const visibleNotifications = notifications.slice(0, maxVisibleState);
  const unreadCount = notifications.filter((n) => !n.read).length;

  // ═════════════════════════════════════════════════════════════════════════
  // CLEANUP
  // ═════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    return () => {
      timeoutsRef.current.forEach((timeout) => clearTimeout(timeout));
    };
  }, []);

  // ═════════════════════════════════════════════════════════════════════════
  // CONTEXT VALUE
  // ═════════════════════════════════════════════════════════════════════════

  const value = {
    notifications,
    visibleNotifications,
    unreadCount,
    position,
    show,
    info,
    success,
    warning,
    error: errorNotif,
    dismiss,
    dismissAll,
    markAsRead,
    markAllAsRead,
    clear,
    clearGroup,
    setPosition: setPositionHandler,
    setMaxVisible: setMaxVisibleHandler,
    setEnableSounds: setEnableSoundsHandler,
    onNotification,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// HOOK
// ═══════════════════════════════════════════════════════════════════════════════

export function useNotificationContext(): NotificationContextValue {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotificationContext must be used within a NotificationProvider');
  }
  return context;
}

// ═══════════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

function playNotificationSound(type: NotificationType): void {
  try {
    const audioContext = new (window.AudioContext || (window as typeof window & { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    const frequencies: Record<NotificationType, number> = {
      info: 600,
      success: 800,
      warning: 500,
      error: 300,
    };

    oscillator.frequency.value = frequencies[type];
    oscillator.type = 'sine';
    gainNode.gain.value = 0.1;

    oscillator.start();
    oscillator.stop(audioContext.currentTime + 0.1);
  } catch {
    // Audio not supported
  }
}

export default NotificationContext;
