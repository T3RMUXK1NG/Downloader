/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    UI STORE v3.0.1 ULTIMATE NEXUS                             ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: UI state management with Zustand                               ║
 * ║  Features: Modals, sidebars, toasts, loading, navigation                    ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module store/uiStore
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export type ModalType = 
  | 'download'
  | 'settings'
  | 'info'
  | 'history'
  | 'batch'
  | 'playlist'
  | 'confirm'
  | 'error'
  | 'preview'
  | 'share';

export type SidebarTab = 
  | 'downloads'
  | 'history'
  | 'settings'
  | 'about';

export interface ModalState {
  type: ModalType;
  isOpen: boolean;
  data?: Record<string, unknown>;
  onClose?: () => void;
}

export interface ToastState {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message?: string;
  duration?: number;
  persistent?: boolean;
}

export interface UIStore {
  // ═════════════════════════════════════════════════════════════════════════
  // SIDEBAR STATE
  // ═════════════════════════════════════════════════════════════════════════
  sidebarOpen: boolean;
  sidebarTab: SidebarTab;
  sidebarWidth: number;

  // ═════════════════════════════════════════════════════════════════════════
  // MODAL STATE
  // ═════════════════════════════════════════════════════════════════════════
  modals: Map<ModalType, ModalState>;
  activeModal: ModalType | null;

  // ═════════════════════════════════════════════════════════════════════════
  // TOAST STATE
  // ═════════════════════════════════════════════════════════════════════════
  toasts: ToastState[];

  // ═════════════════════════════════════════════════════════════════════════
  // LOADING STATE
  // ═════════════════════════════════════════════════════════════════════════
  isLoading: boolean;
  loadingMessage: string;
  loadingProgress: number;

  // ═════════════════════════════════════════════════════════════════════════
  // SEARCH STATE
  // ═════════════════════════════════════════════════════════════════════════
  searchOpen: boolean;
  searchQuery: string;

  // ═════════════════════════════════════════════════════════════════════════
  // OTHER UI STATE
  // ═════════════════════════════════════════════════════════════════════════
  isFullScreen: boolean;
  isCompactMode: boolean;
  focusedElement: string | null;

  // ═════════════════════════════════════════════════════════════════════════
  // SIDEBAR ACTIONS
  // ═════════════════════════════════════════════════════════════════════════
  toggleSidebar: () => void;
  openSidebar: () => void;
  closeSidebar: () => void;
  setSidebarTab: (tab: SidebarTab) => void;
  setSidebarWidth: (width: number) => void;

  // ═════════════════════════════════════════════════════════════════════════
  // MODAL ACTIONS
  // ═════════════════════════════════════════════════════════════════════════
  openModal: (type: ModalType, data?: Record<string, unknown>, onClose?: () => void) => void;
  closeModal: (type: ModalType) => void;
  closeAllModals: () => void;
  updateModalData: (type: ModalType, data: Record<string, unknown>) => void;

  // ═════════════════════════════════════════════════════════════════════════
  // TOAST ACTIONS
  // ═════════════════════════════════════════════════════════════════════════
  addToast: (toast: Omit<ToastState, 'id'>) => string;
  removeToast: (id: string) => void;
  clearToasts: () => void;

  // ═════════════════════════════════════════════════════════════════════════
  // LOADING ACTIONS
  // ═════════════════════════════════════════════════════════════════════════
  setLoading: (loading: boolean, message?: string) => void;
  setLoadingProgress: (progress: number) => void;

  // ═════════════════════════════════════════════════════════════════════════
  // SEARCH ACTIONS
  // ═════════════════════════════════════════════════════════════════════════
  toggleSearch: () => void;
  openSearch: () => void;
  closeSearch: () => void;
  setSearchQuery: (query: string) => void;

  // ═════════════════════════════════════════════════════════════════════════
  // OTHER ACTIONS
  // ═════════════════════════════════════════════════════════════════════════
  toggleFullScreen: () => void;
  toggleCompactMode: () => void;
  setFocusedElement: (element: string | null) => void;
}

// ═══════════════════════════════════════════════════════════════════════════════
// STORE IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

export const useUIStore = create<UIStore>()(
  immer((set) => ({
    // ═════════════════════════════════════════════════════════════════════════
    // INITIAL STATE
    // ═════════════════════════════════════════════════════════════════════════
    sidebarOpen: true,
    sidebarTab: 'downloads',
    sidebarWidth: 280,
    modals: new Map(),
    activeModal: null,
    toasts: [],
    isLoading: false,
    loadingMessage: '',
    loadingProgress: 0,
    searchOpen: false,
    searchQuery: '',
    isFullScreen: false,
    isCompactMode: false,
    focusedElement: null,

    // ═════════════════════════════════════════════════════════════════════════
    // SIDEBAR ACTIONS
    // ═════════════════════════════════════════════════════════════════════════

    toggleSidebar: () => {
      set((state) => {
        state.sidebarOpen = !state.sidebarOpen;
      });
    },

    openSidebar: () => {
      set((state) => {
        state.sidebarOpen = true;
      });
    },

    closeSidebar: () => {
      set((state) => {
        state.sidebarOpen = false;
      });
    },

    setSidebarTab: (tab) => {
      set((state) => {
        state.sidebarTab = tab;
      });
    },

    setSidebarWidth: (width) => {
      set((state) => {
        state.sidebarWidth = Math.max(200, Math.min(500, width));
      });
    },

    // ═════════════════════════════════════════════════════════════════════════
    // MODAL ACTIONS
    // ═════════════════════════════════════════════════════════════════════════

    openModal: (type, data, onClose) => {
      set((state) => {
        state.modals.set(type, {
          type,
          isOpen: true,
          data,
          onClose,
        });
        state.activeModal = type;
      });
    },

    closeModal: (type) => {
      set((state) => {
        const modal = state.modals.get(type);
        if (modal?.onClose) {
          modal.onClose();
        }
        state.modals.delete(type);
        if (state.activeModal === type) {
          state.activeModal = null;
        }
      });
    },

    closeAllModals: () => {
      set((state) => {
        state.modals.forEach((modal) => {
          if (modal.onClose) {
            modal.onClose();
          }
        });
        state.modals.clear();
        state.activeModal = null;
      });
    },

    updateModalData: (type, data) => {
      set((state) => {
        const modal = state.modals.get(type);
        if (modal) {
          modal.data = { ...modal.data, ...data };
        }
      });
    },

    // ═════════════════════════════════════════════════════════════════════════
    // TOAST ACTIONS
    // ═════════════════════════════════════════════════════════════════════════

    addToast: (toast) => {
      const id = `toast_${Date.now()}_${Math.random().toString(36).substring(2, 10)}`;
      set((state) => {
        state.toasts.push({ ...toast, id });
      });
      return id;
    },

    removeToast: (id) => {
      set((state) => {
        state.toasts = state.toasts.filter((t) => t.id !== id);
      });
    },

    clearToasts: () => {
      set((state) => {
        state.toasts = [];
      });
    },

    // ═════════════════════════════════════════════════════════════════════════
    // LOADING ACTIONS
    // ═════════════════════════════════════════════════════════════════════════

    setLoading: (loading, message) => {
      set((state) => {
        state.isLoading = loading;
        state.loadingMessage = message || '';
        if (!loading) {
          state.loadingProgress = 0;
        }
      });
    },

    setLoadingProgress: (progress) => {
      set((state) => {
        state.loadingProgress = Math.min(100, Math.max(0, progress));
      });
    },

    // ═════════════════════════════════════════════════════════════════════════
    // SEARCH ACTIONS
    // ═════════════════════════════════════════════════════════════════════════

    toggleSearch: () => {
      set((state) => {
        state.searchOpen = !state.searchOpen;
      });
    },

    openSearch: () => {
      set((state) => {
        state.searchOpen = true;
      });
    },

    closeSearch: () => {
      set((state) => {
        state.searchOpen = false;
        state.searchQuery = '';
      });
    },

    setSearchQuery: (query) => {
      set((state) => {
        state.searchQuery = query;
      });
    },

    // ═════════════════════════════════════════════════════════════════════════
    // OTHER ACTIONS
    // ═════════════════════════════════════════════════════════════════════════

    toggleFullScreen: () => {
      set((state) => {
        state.isFullScreen = !state.isFullScreen;
      });

      // Actually toggle fullscreen
      if (typeof document !== 'undefined') {
        if (!document.fullscreenElement) {
          document.documentElement.requestFullscreen?.();
        } else {
          document.exitFullscreen?.();
        }
      }
    },

    toggleCompactMode: () => {
      set((state) => {
        state.isCompactMode = !state.isCompactMode;
      });
    },

    setFocusedElement: (element) => {
      set((state) => {
        state.focusedElement = element;
      });
    },
  }))
);

export default useUIStore;
