/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    APP CONTEXT v3.0.1 ULTIMATE NEXUS                          ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Global application context provider                           ║
 * ║  Features: App state, config, user, session, global handlers                ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module context/AppContext
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

'use client';

import React, { createContext, useContext, useCallback, useEffect, useMemo, useState } from 'react';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface AppConfig {
  appName: string;
  version: string;
  author: string;
  buildDate: string;
  environment: 'development' | 'production' | 'test';
  features: {
    downloads: boolean;
    batch: boolean;
    playlist: boolean;
    subtitles: boolean;
    metadata: boolean;
    thumbnails: boolean;
    websocket: boolean;
  };
}

export interface User {
  id: string;
  name: string;
  email?: string;
  avatar?: string;
  role: 'guest' | 'user' | 'admin';
  preferences: Record<string, unknown>;
}

export interface Session {
  id: string;
  userId: string;
  startedAt: Date;
  lastActivity: Date;
  ipAddress?: string;
  userAgent?: string;
}

export interface AppState {
  initialized: boolean;
  loading: boolean;
  error: string | null;
  online: boolean;
  config: AppConfig;
  user: User | null;
  session: Session | null;
}

export interface AppContextValue extends AppState {
  // Initialization
  initialize: () => Promise<void>;
  reset: () => void;

  // User actions
  setUser: (user: User | null) => void;
  updateUser: (updates: Partial<User>) => void;
  logout: () => void;

  // Session actions
  setSession: (session: Session | null) => void;
  refreshSession: () => Promise<void>;

  // Error handling
  setError: (error: string | null) => void;
  clearError: () => void;

  // Utilities
  isFeatureEnabled: (feature: keyof AppConfig['features']) => boolean;
  logActivity: (action: string, data?: Record<string, unknown>) => void;
}

// ═══════════════════════════════════════════════════════════════════════════════
// DEFAULTS
// ═══════════════════════════════════════════════════════════════════════════════

const DEFAULT_CONFIG: AppConfig = {
  appName: 'RS TOOLKIT',
  version: '3.1.1',
  author: 'RAJSARASWATI JATAV (RS) - T3rmuxk1ng',
  buildDate: new Date().toISOString(),
  environment: process.env.NODE_ENV as 'development' | 'production' | 'test',
  features: {
    downloads: true,
    batch: true,
    playlist: true,
    subtitles: true,
    metadata: true,
    thumbnails: true,
    websocket: true,
  },
};

const DEFAULT_STATE: AppState = {
  initialized: false,
  loading: true,
  error: null,
  online: true,
  config: DEFAULT_CONFIG,
  user: null,
  session: null,
};

// ═══════════════════════════════════════════════════════════════════════════════
// CONTEXT
// ═══════════════════════════════════════════════════════════════════════════════

const AppContext = createContext<AppContextValue | undefined>(undefined);

// ═══════════════════════════════════════════════════════════════════════════════
// PROVIDER
// ═══════════════════════════════════════════════════════════════════════════════

export interface AppProviderProps {
  children: React.ReactNode;
  config?: Partial<AppConfig>;
  initialUser?: User;
}

export function AppProvider({ children, config, initialUser }: AppProviderProps): React.ReactElement {
  const [state, setState] = useState<AppState>({
    ...DEFAULT_STATE,
    config: { ...DEFAULT_CONFIG, ...config },
    user: initialUser || null,
  });

  // ═════════════════════════════════════════════════════════════════════════
  // ONLINE STATUS
  // ═════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    const handleOnline = () => setState((prev) => ({ ...prev, online: true }));
    const handleOffline = () => setState((prev) => ({ ...prev, online: false }));

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // ═════════════════════════════════════════════════════════════════════════
  // INITIALIZATION
  // ═════════════════════════════════════════════════════════════════════════

  const initialize = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      // Initialize session
      const session: Session = {
        id: `session_${Date.now()}`,
        userId: state.user?.id || 'guest',
        startedAt: new Date(),
        lastActivity: new Date(),
        userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : undefined,
      };

      setState((prev) => ({
        ...prev,
        session,
        initialized: true,
        loading: false,
      }));
    } catch (error) {
      setState((prev) => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Initialization failed',
        loading: false,
      }));
    }
  }, [state.user?.id]);

  // Initialize on mount
  useEffect(() => {
    if (!state.initialized) {
      initialize();
    }
  }, [state.initialized, initialize]);

  // ═════════════════════════════════════════════════════════════════════════
  // RESET
  // ═════════════════════════════════════════════════════════════════════════

  const reset = useCallback(() => {
    setState({
      ...DEFAULT_STATE,
      config: { ...DEFAULT_CONFIG, ...config },
    });
  }, [config]);

  // ═════════════════════════════════════════════════════════════════════════
  // USER ACTIONS
  // ═════════════════════════════════════════════════════════════════════════

  const setUser = useCallback((user: User | null) => {
    setState((prev) => ({ ...prev, user }));
  }, []);

  const updateUser = useCallback((updates: Partial<User>) => {
    setState((prev) => ({
      ...prev,
      user: prev.user ? { ...prev.user, ...updates } : null,
    }));
  }, []);

  const logout = useCallback(() => {
    setState((prev) => ({
      ...prev,
      user: null,
      session: null,
    }));
  }, []);

  // ═════════════════════════════════════════════════════════════════════════
  // SESSION ACTIONS
  // ═════════════════════════════════════════════════════════════════════════

  const setSession = useCallback((session: Session | null) => {
    setState((prev) => ({ ...prev, session }));
  }, []);

  const refreshSession = useCallback(async () => {
    setState((prev) => ({
      ...prev,
      session: prev.session
        ? { ...prev.session, lastActivity: new Date() }
        : null,
    }));
  }, []);

  // ═════════════════════════════════════════════════════════════════════════
  // ERROR HANDLING
  // ═════════════════════════════════════════════════════════════════════════

  const setError = useCallback((error: string | null) => {
    setState((prev) => ({ ...prev, error }));
  }, []);

  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  // ═════════════════════════════════════════════════════════════════════════
  // UTILITIES
  // ═════════════════════════════════════════════════════════════════════════

  const isFeatureEnabled = useCallback(
    (feature: keyof AppConfig['features']): boolean => {
      return state.config.features[feature] ?? false;
    },
    [state.config.features]
  );

  const logActivity = useCallback(
    (action: string, data?: Record<string, unknown>) => {
      console.log(`[AppActivity] ${action}`, {
        timestamp: new Date().toISOString(),
        userId: state.user?.id,
        session: state.session?.id,
        ...data,
      });
    },
    [state.user?.id, state.session?.id]
  );

  // ═════════════════════════════════════════════════════════════════════════
  // CONTEXT VALUE
  // ═════════════════════════════════════════════════════════════════════════

  const value = useMemo<AppContextValue>(
    () => ({
      ...state,
      initialize,
      reset,
      setUser,
      updateUser,
      logout,
      setSession,
      refreshSession,
      setError,
      clearError,
      isFeatureEnabled,
      logActivity,
    }),
    [
      state,
      initialize,
      reset,
      setUser,
      updateUser,
      logout,
      setSession,
      refreshSession,
      setError,
      clearError,
      isFeatureEnabled,
      logActivity,
    ]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// HOOK
// ═══════════════════════════════════════════════════════════════════════════════

export function useApp(): AppContextValue {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}

export default AppContext;
