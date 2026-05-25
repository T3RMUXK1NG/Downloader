/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   NOTIFICATION TOAST v3.0.1 ULTIMATE NEXUS                   ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Toast notification system with animations                      ║
 * ║  Features: Multiple types, actions, progress, queue, stacking               ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  CheckCircle,
  AlertCircle,
  AlertTriangle,
  Info,
  X,
  Download,
  Upload,
  RefreshCw,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export type ToastType = 'success' | 'error' | 'warning' | 'info' | 'download' | 'upload' | 'progress';

export interface ToastAction {
  label: string;
  onClick: () => void;
}

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
  progress?: number;
  actions?: ToastAction[];
  icon?: React.ReactNode;
  dismissible?: boolean;
  onDismiss?: () => void;
}

export interface NotificationToastProps {
  /** Toast to display */
  toast: Toast;
  /** On dismiss */
  onDismiss: (id: string) => void;
  /** Position */
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
}

export interface ToastContainerProps {
  /** Toasts to display */
  toasts: Toast[];
  /** On dismiss */
  onDismiss: (id: string) => void;
  /** Position */
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
  /** Max visible toasts */
  maxVisible?: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// TOAST CONTEXT
// ═══════════════════════════════════════════════════════════════════════════════

interface ToastContextValue {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
  updateToast: (id: string, updates: Partial<Toast>) => void;
}

const ToastContext = React.createContext<ToastContextValue | undefined>(undefined);

export const useToast = (): ToastContextValue => {
  const context = React.useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

export interface ToastProviderProps {
  children: React.ReactNode;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
  maxVisible?: number;
}

export const ToastProvider: React.FC<ToastProviderProps> = ({
  children,
  position = 'bottom-right',
  maxVisible = 5,
}) => {
  const [toasts, setToasts] = React.useState<Toast[]>([]);

  const addToast = (toast: Omit<Toast, 'id'>): string => {
    const id = `toast_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newToast = { ...toast, id };

    setToasts((prev) => {
      const updated = [...prev, newToast];
      return updated.slice(-maxVisible);
    });

    // Auto dismiss
    if (toast.duration !== 0) {
      setTimeout(() => {
        removeToast(id);
      }, toast.duration || 5000);
    }

    return id;
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const updateToast = (id: string, updates: Partial<Toast>) => {
    setToasts((prev) =>
      prev.map((t) => (t.id === id ? { ...t, ...updates } : t))
    );
  };

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast, updateToast }}>
      {children}
      <ToastContainer toasts={toasts} onDismiss={removeToast} position={position} maxVisible={maxVisible} />
    </ToastContext.Provider>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// ICON MAPPING
// ═══════════════════════════════════════════════════════════════════════════════

const typeConfig: Record<ToastType, { icon: React.ReactNode; className: string }> = {
  success: {
    icon: <CheckCircle className="w-5 h-5" />,
    className: 'border-green-500/50 bg-green-500/10',
  },
  error: {
    icon: <AlertCircle className="w-5 h-5" />,
    className: 'border-red-500/50 bg-red-500/10',
  },
  warning: {
    icon: <AlertTriangle className="w-5 h-5" />,
    className: 'border-amber-500/50 bg-amber-500/10',
  },
  info: {
    icon: <Info className="w-5 h-5" />,
    className: 'border-blue-500/50 bg-blue-500/10',
  },
  download: {
    icon: <Download className="w-5 h-5" />,
    className: 'border-emerald-500/50 bg-emerald-500/10',
  },
  upload: {
    icon: <Upload className="w-5 h-5" />,
    className: 'border-purple-500/50 bg-purple-500/10',
  },
  progress: {
    icon: <RefreshCw className="w-5 h-5 animate-spin" />,
    className: 'border-primary/50 bg-primary/10',
  },
};

const typeIconColors: Record<ToastType, string> = {
  success: 'text-green-500',
  error: 'text-red-500',
  warning: 'text-amber-500',
  info: 'text-blue-500',
  download: 'text-emerald-500',
  upload: 'text-purple-500',
  progress: 'text-primary',
};

// ═══════════════════════════════════════════════════════════════════════════════
// SINGLE TOAST COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export const NotificationToast: React.FC<NotificationToastProps> = ({
  toast,
  onDismiss,
}) => {
  const config = typeConfig[toast.type];
  const iconColor = typeIconColors[toast.type];
  const dismissible = toast.dismissible !== false;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 50, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.15 } }}
      className={cn(
        'relative flex items-start gap-3 p-4 rounded-xl border shadow-lg',
        'bg-card/95 backdrop-blur-sm',
        config.className
      )}
      role="alert"
    >
      {/* Icon */}
      <div className={cn('flex-shrink-0 mt-0.5', iconColor)}>
        {toast.icon || config.icon}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-foreground">{toast.title}</p>
        {toast.message && (
          <p className="text-xs text-muted-foreground mt-0.5">{toast.message}</p>
        )}

        {/* Progress bar */}
        {toast.type === 'progress' && toast.progress !== undefined && (
          <div className="mt-2 h-1.5 rounded-full bg-muted overflow-hidden">
            <motion.div
              className="h-full bg-primary rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${toast.progress}%` }}
            />
          </div>
        )}

        {/* Actions */}
        {toast.actions && toast.actions.length > 0 && (
          <div className="flex gap-2 mt-2">
            {toast.actions.map((action, index) => (
              <button
                key={index}
                onClick={action.onClick}
                className="text-xs font-medium text-primary hover:underline"
              >
                {action.label}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Dismiss button */}
      {dismissible && (
        <button
          onClick={() => onDismiss(toast.id)}
          className="flex-shrink-0 p-1 rounded-lg hover:bg-muted/50 transition-colors"
          aria-label="Dismiss"
        >
          <X className="w-4 h-4 text-muted-foreground" />
        </button>
      )}
    </motion.div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// TOAST CONTAINER
// ═══════════════════════════════════════════════════════════════════════════════

export const ToastContainer: React.FC<ToastContainerProps> = ({
  toasts,
  onDismiss,
  position = 'bottom-right',
  maxVisible = 5,
}) => {
  const positionClasses: Record<string, string> = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-center': 'top-4 left-1/2 -translate-x-1/2',
    'bottom-center': 'bottom-4 left-1/2 -translate-x-1/2',
  };

  const visibleToasts = toasts.slice(-maxVisible);

  return (
    <div
      className={cn(
        'fixed z-[100] flex flex-col gap-2 w-full max-w-sm pointer-events-none',
        positionClasses[position]
      )}
    >
      <AnimatePresence mode="popLayout">
        {visibleToasts.map((toast) => (
          <div key={toast.id} className="pointer-events-auto">
            <NotificationToast toast={toast} onDismiss={onDismiss} />
          </div>
        ))}
      </AnimatePresence>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

export const createToastHelpers = (addToast: (toast: Omit<Toast, 'id'>) => string) => ({
  success: (title: string, message?: string, options?: Partial<Toast>) =>
    addToast({ type: 'success', title, message, ...options }),
  error: (title: string, message?: string, options?: Partial<Toast>) =>
    addToast({ type: 'error', title, message, ...options }),
  warning: (title: string, message?: string, options?: Partial<Toast>) =>
    addToast({ type: 'warning', title, message, ...options }),
  info: (title: string, message?: string, options?: Partial<Toast>) =>
    addToast({ type: 'info', title, message, ...options }),
  download: (title: string, message?: string, options?: Partial<Toast>) =>
    addToast({ type: 'download', title, message, ...options }),
  upload: (title: string, message?: string, options?: Partial<Toast>) =>
    addToast({ type: 'upload', title, message, ...options }),
  progress: (title: string, progress: number, options?: Partial<Toast>) =>
    addToast({ type: 'progress', title, progress, duration: 0, ...options }),
});

export default NotificationToast;
