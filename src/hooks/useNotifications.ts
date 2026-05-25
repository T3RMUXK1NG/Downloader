/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    USE NOTIFICATIONS HOOK v3.0.1 ULTIMATE NEXUS              ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Notifications management hook with persistence                ║
 * ║  Features: Toast, alerts, badges, persistence, actions, grouping            ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module hooks/useNotifications
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

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

export interface UseNotificationsOptions {
  /** Maximum notifications to show */
  maxVisible?: number;
  /** Default duration in ms */
  defaultDuration?: number;
  /** Position of notifications */
  position?: NotificationPosition;
  /** Enable sounds */
  enableSounds?: boolean;
  /** Persist to storage */
  persist?: boolean;
  /** Storage key */
  storageKey?: string;
}

export interface UseNotificationsReturn {
  /** All notifications */
  notifications: Notification[];
  /** Visible notifications */
  visibleNotifications: Notification[];
  /** Unread count */
  unreadCount: number;
  /** Show notification */
  show: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => string;
  /** Show info notification */
  info: (title: string, message?: string) => string;
  /** Show success notification */
  success: (title: string, message?: string) => string;
  /** Show warning notification */
  warning: (title: string, message?: string) => string;
  /** Show error notification */
  error: (title: string, message?: string) => string;
  /** Dismiss notification */
  dismiss: (id: string) => void;
  /** Dismiss all notifications */
  dismissAll: () => void;
  /** Mark as read */
  markAsRead: (id: string) => void;
  /** Mark all as read */
  markAllAsRead: () => void;
  /** Clear all notifications */
  clear: () => void;
  /** Clear by group */
  clearGroup: (group: string) => void;
}

// ═══════════════════════════════════════════════════════════════════════════════
// HOOK IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * useNotifications Hook
 * @description Notifications management with toast, alerts, and badges
 * @param options Hook options
 * @returns Notification controls and state
 */
export function useNotifications(options: UseNotificationsOptions = {}): UseNotificationsReturn {
  const {
    maxVisible = 5,
    defaultDuration = 5000,
    position = 'top-right',
    enableSounds = true,
    persist = true,
    storageKey = 'rs-toolkit-notifications',
  } = options;

  // State
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const timeoutsRef = useRef<Map<string, NodeJS.Timeout>>(new Map());

  // ═══════════════════════════════════════════════════════════════════════════
  // LOAD FROM STORAGE
  // ═══════════════════════════════════════════════════════════════════════════

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

  // ═══════════════════════════════════════════════════════════════════════════
  // SAVE TO STORAGE
  // ═══════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    if (!persist || typeof window === 'undefined') return;

    try {
      localStorage.setItem(storageKey, JSON.stringify(notifications));
    } catch (error) {
      console.error('Failed to save notifications:', error);
    }
  }, [notifications, persist, storageKey]);

  // ═══════════════════════════════════════════════════════════════════════════
  // SHOW NOTIFICATION
  // ═══════════════════════════════════════════════════════════════════════════

  const show = useCallback(
    (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>): string => {
      const id = `notif_${Date.now()}_${Math.random().toString(36).substring(2, 10)}`;
      const duration = notification.duration ?? defaultDuration;
      const persistent = notification.persistent ?? false;

      const newNotification: Notification = {
        ...notification,
        id,
        timestamp: new Date(),
        read: false,
      };

      setNotifications((prev) => [newNotification, ...prev]);

      // Play sound
      if (enableSounds && typeof window !== 'undefined') {
        playNotificationSound(notification.type);
      }

      // Auto-dismiss
      if (!persistent && duration > 0) {
        const timeout = setTimeout(() => {
          dismiss(id);
        }, duration);
        timeoutsRef.current.set(id, timeout);
      }

      return id;
    },
    [defaultDuration, enableSounds]
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // HELPER FUNCTIONS
  // ═══════════════════════════════════════════════════════════════════════════

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

  // ═══════════════════════════════════════════════════════════════════════════
  // DISMISS NOTIFICATION
  // ═══════════════════════════════════════════════════════════════════════════

  const dismiss = useCallback((id: string) => {
    // Clear timeout
    const timeout = timeoutsRef.current.get(id);
    if (timeout) {
      clearTimeout(timeout);
      timeoutsRef.current.delete(id);
    }

    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const dismissAll = useCallback(() => {
    // Clear all timeouts
    timeoutsRef.current.forEach((timeout) => clearTimeout(timeout));
    timeoutsRef.current.clear();

    setNotifications([]);
  }, []);

  // ═══════════════════════════════════════════════════════════════════════════
  // MARK AS READ
  // ═══════════════════════════════════════════════════════════════════════════

  const markAsRead = useCallback((id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  }, []);

  // ═══════════════════════════════════════════════════════════════════════════
  // CLEAR NOTIFICATIONS
  // ═══════════════════════════════════════════════════════════════════════════

  const clear = useCallback(() => {
    dismissAll();
  }, [dismissAll]);

  const clearGroup = useCallback((group: string) => {
    setNotifications((prev) => prev.filter((n) => n.group !== group));
  }, []);

  // ═══════════════════════════════════════════════════════════════════════════
  // COMPUTED VALUES
  // ═══════════════════════════════════════════════════════════════════════════

  const visibleNotifications = notifications.slice(0, maxVisible);

  const unreadCount = notifications.filter((n) => !n.read).length;

  // ═══════════════════════════════════════════════════════════════════════════
  // CLEANUP
  // ═══════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    return () => {
      timeoutsRef.current.forEach((timeout) => clearTimeout(timeout));
    };
  }, []);

  // ═══════════════════════════════════════════════════════════════════════════
  // RETURN
  // ═══════════════════════════════════════════════════════════════════════════

  return {
    notifications,
    visibleNotifications,
    unreadCount,
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
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Play notification sound
 */
function playNotificationSound(type: NotificationType): void {
  try {
    // Create audio context for notification sounds
    const audioContext = new (window.AudioContext || (window as typeof window & { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    // Different frequencies for different types
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
    // Audio not supported or blocked
  }
}

export default useNotifications;
