/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    UI STORE v3.2.0 ULTIMATE NEXUS                             ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Enhanced UI state management with Zustand                      ║
 * ║  Features: Modals, sidebars, toasts, loading, navigation, persistence        ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module store/uiStore
 * @version 3.2.0
 * @author RAJSARASWATI JATAV (RS)
 */

import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { persist, createJSONStorage } from 'zustand/middleware';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Modal type enumeration
 */
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
  | 'share'
  | 'schedule'
  | 'rules'
  | 'categories'
  | 'tags'
  | 'export'
  | 'import'
  | 'about'
  | 'update'
  | 'shortcuts';

/**
 * Sidebar tab enumeration
 */
export type SidebarTab = 
  | 'downloads'
  | 'history'
  | 'queue'
  | 'favorites'
  | 'settings'
  | 'about';

/**
 * View mode enumeration
 */
export type ViewMode = 'grid' | 'list' | 'compact' | 'table';

/**
 * Panel position
 */
export type PanelPosition = 'left' | 'right' | 'bottom' | 'top';

/**
 * Modal state interface
 */
export interface ModalState {
  type: ModalType;
  isOpen: boolean;
  data?: Record<string, unknown>;
  onClose?: () => void;
  priority?: number;
  closeOnEscape?: boolean;
  closeOnBackdrop?: boolean;
}

/**
 * Toast type enumeration
 */
export type ToastType = 'info' | 'success' | 'warning' | 'error' | 'loading';

/**
 * Toast state interface
 */
export interface ToastState {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
  persistent?: boolean;
  progress?: number;
  icon?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  createdAt: Date;
}

/**
 * Panel state interface
 */
export interface PanelState {
  id: string;
  position: PanelPosition;
  size: number;
  isOpen: boolean;
  isResizable: boolean;
  minSize?: number;
  maxSize?: number;
}

/**
 * Column configuration for tables
 */
export interface ColumnConfig {
  id: string;
  label: string;
  visible: boolean;
  width: number;
  sortable: boolean;
  resizable: boolean;
}

/**
 * Layout preferences
 */
export interface LayoutPreferences {
  viewMode: ViewMode;
  columns: ColumnConfig[];
  sortBy: string;
  sortDirection: 'asc' | 'desc';
  groupBy?: string;
  showThumbnails: boolean;
  thumbnailSize: number;
  showDetails: boolean;
  compactRows: boolean;
}

/**
 * Drag state
 */
export interface DragState {
  isDragging: boolean;
  draggedItemIds: string[];
  draggedFrom: string;
  draggedTo?: string;
  position?: { x: number; y: number };
}

/**
 * Context menu state
 */
export interface ContextMenuState {
  isOpen: boolean;
  position: { x: number; y: number };
  targetId?: string;
  targetType?: string;
  items: ContextMenuItem[];
}

/**
 * Context menu item
 */
export interface ContextMenuItem {
  id: string;
  label: string;
  icon?: string;
  shortcut?: string;
  disabled?: boolean;
  separator?: boolean;
  danger?: boolean;
  onClick?: () => void;
  submenu?: ContextMenuItem[];
}

/**
 * Undo/redo state
 */
interface UndoState {
  state: Partial<UIStoreState>;
  timestamp: number;
  action: string;
}

/**
 * Store state interface
 */
export interface UIStoreState {
  // Sidebar state
  sidebarOpen: boolean;
  sidebarTab: SidebarTab;
  sidebarWidth: number;
  sidebarCollapsed: boolean;
  
  // Modal state
  modals: Record<ModalType, ModalState>;
  activeModal: ModalType | null;
  modalStack: ModalType[];
  
  // Toast state
  toasts: ToastState[];
  maxToasts: number;
  
  // Loading state
  isLoading: boolean;
  loadingMessage: string;
  loadingProgress: number;
  loadingIndeterminate: boolean;
  loadingOperations: Record<string, { progress: number; message: string }>;
  
  // Search state
  searchOpen: boolean;
  searchQuery: string;
  searchHistory: string[];
  maxSearchHistory: number;
  
  // Layout state
  layout: LayoutPreferences;
  
  // Panel state
  panels: Record<string, PanelState>;
  
  // Selection state
  selectedItems: string[];
  lastSelectedIndex: number;
  
  // Drag state
  drag: DragState;
  
  // Context menu state
  contextMenu: ContextMenuState;
  
  // Other UI state
  isFullScreen: boolean;
  isCompactMode: boolean;
  focusedElement: string | null;
  hoveredItemId: string | null;
  editingItemId: string | null;
  
  // Window state
  windowSize: { width: number; height: number };
  windowPosition: { x: number; y: number };
  isMaximized: boolean;
  
  // Undo/redo
  undoStack: UndoState[];
  redoStack: UndoState[];
  maxUndoSteps: number;
  
  // Persistence
  lastSaved: Date | null;
  isHydrated: boolean;
}

/**
 * Store actions interface
 */
export interface UIStoreActions {
  // Sidebar actions
  toggleSidebar: () => void;
  openSidebar: () => void;
  closeSidebar: () => void;
  setSidebarTab: (tab: SidebarTab) => void;
  setSidebarWidth: (width: number) => void;
  toggleSidebarCollapsed: () => void;
  
  // Modal actions
  openModal: (type: ModalType, data?: Record<string, unknown>, options?: Partial<ModalState>) => void;
  closeModal: (type: ModalType) => void;
  closeAllModals: () => void;
  closeTopModal: () => void;
  updateModalData: (type: ModalType, data: Record<string, unknown>) => void;
  getModalStack: () => ModalType[];
  
  // Toast actions
  addToast: (toast: Omit<ToastState, 'id' | 'createdAt'>) => string;
  updateToast: (id: string, updates: Partial<ToastState>) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
  addSuccessToast: (title: string, message?: string) => string;
  addErrorToast: (title: string, message?: string) => string;
  addWarningToast: (title: string, message?: string) => string;
  addLoadingToast: (title: string, message?: string) => string;
  
  // Loading actions
  setLoading: (loading: boolean, message?: string) => void;
  setLoadingProgress: (progress: number) => void;
  setLoadingIndeterminate: (indeterminate: boolean) => void;
  startLoadingOperation: (id: string, message: string) => void;
  updateLoadingOperation: (id: string, progress: number, message?: string) => void;
  endLoadingOperation: (id: string) => void;
  clearLoadingOperations: () => void;
  
  // Search actions
  toggleSearch: () => void;
  openSearch: () => void;
  closeSearch: () => void;
  setSearchQuery: (query: string) => void;
  addToSearchHistory: (query: string) => void;
  clearSearchHistory: () => void;
  
  // Layout actions
  setViewMode: (mode: ViewMode) => void;
  toggleColumn: (columnId: string) => void;
  setColumnWidth: (columnId: string, width: number) => void;
  setSort: (sortBy: string, direction: 'asc' | 'desc') => void;
  setGroupBy: (groupBy: string | undefined) => void;
  toggleThumbnails: () => void;
  setThumbnailSize: (size: number) => void;
  toggleDetails: () => void;
  toggleCompactRows: () => void;
  resetLayout: () => void;
  
  // Panel actions
  openPanel: (id: string, position: PanelPosition, size: number) => void;
  closePanel: (id: string) => void;
  togglePanel: (id: string) => void;
  setPanelSize: (id: string, size: number) => void;
  
  // Selection actions
  selectItem: (id: string, index?: number) => void;
  deselectItem: (id: string) => void;
  toggleSelectItem: (id: string, index?: number) => void;
  selectRange: (start: number, end: number) => void;
  selectAll: (ids: string[]) => void;
  deselectAll: () => void;
  getSelectedItems: () => string[];
  
  // Drag actions
  startDrag: (itemIds: string[], from: string, position: { x: number; y: number }) => void;
  updateDragPosition: (position: { x: number; y: number }) => void;
  endDrag: () => void;
  setDragTarget: (to: string) => void;
  
  // Context menu actions
  openContextMenu: (position: { x: number; y: number }, items: ContextMenuItem[], targetId?: string, targetType?: string) => void;
  closeContextMenu: () => void;
  
  // Other actions
  toggleFullScreen: () => void;
  setFullScreen: (fullScreen: boolean) => void;
  toggleCompactMode: () => void;
  setFocusedElement: (element: string | null) => void;
  setHoveredItem: (id: string | null) => void;
  setEditingItem: (id: string | null) => void;
  
  // Window actions
  updateWindowSize: (size: { width: number; height: number }) => void;
  updateWindowPosition: (position: { x: number; y: number }) => void;
  toggleMaximized: () => void;
  
  // Undo/Redo
  undo: () => boolean;
  redo: () => boolean;
  canUndo: () => boolean;
  canRedo: () => boolean;
  clearHistory: () => void;
  
  // Persistence
  saveToStorage: () => void;
  loadFromStorage: () => void;
  setHydrated: (hydrated: boolean) => void;
  resetUI: () => void;
}

/**
 * Combined store type
 */
export type UIStore = UIStoreState & UIStoreActions;

// ═══════════════════════════════════════════════════════════════════════════════
// DEFAULT VALUES
// ═══════════════════════════════════════════════════════════════════════════════

const DEFAULT_COLUMNS: ColumnConfig[] = [
  { id: 'thumbnail', label: 'Thumbnail', visible: true, width: 64, sortable: false, resizable: false },
  { id: 'title', label: 'Title', visible: true, width: 300, sortable: true, resizable: true },
  { id: 'status', label: 'Status', visible: true, width: 100, sortable: true, resizable: true },
  { id: 'size', label: 'Size', visible: true, width: 100, sortable: true, resizable: true },
  { id: 'progress', label: 'Progress', visible: true, width: 150, sortable: true, resizable: true },
  { id: 'speed', label: 'Speed', visible: true, width: 100, sortable: true, resizable: true },
  { id: 'eta', label: 'ETA', visible: true, width: 80, sortable: true, resizable: true },
  { id: 'actions', label: 'Actions', visible: true, width: 100, sortable: false, resizable: false },
];

const DEFAULT_LAYOUT: LayoutPreferences = {
  viewMode: 'list',
  columns: DEFAULT_COLUMNS,
  sortBy: 'date',
  sortDirection: 'desc',
  showThumbnails: true,
  thumbnailSize: 64,
  showDetails: false,
  compactRows: false,
};

// ═══════════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

const generateId = (): string => `${Date.now()}_${Math.random().toString(36).substring(2, 10)}`;

// ═══════════════════════════════════════════════════════════════════════════════
// STORE IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

export const useUIStore = create<UIStore>()(
  persist(
    immer((set, get) => ({
      // ═════════════════════════════════════════════════════════════════════════
      // INITIAL STATE
      // ═════════════════════════════════════════════════════════════════════════
      sidebarOpen: true,
      sidebarTab: 'downloads',
      sidebarWidth: 280,
      sidebarCollapsed: false,
      
      modals: {} as Record<ModalType, ModalState>,
      activeModal: null,
      modalStack: [],
      
      toasts: [],
      maxToasts: 5,
      
      isLoading: false,
      loadingMessage: '',
      loadingProgress: 0,
      loadingIndeterminate: false,
      loadingOperations: {},
      
      searchOpen: false,
      searchQuery: '',
      searchHistory: [],
      maxSearchHistory: 20,
      
      layout: { ...DEFAULT_LAYOUT },
      
      panels: {},
      
      selectedItems: [],
      lastSelectedIndex: -1,
      
      drag: {
        isDragging: false,
        draggedItemIds: [],
        draggedFrom: '',
      },
      
      contextMenu: {
        isOpen: false,
        position: { x: 0, y: 0 },
        items: [],
      },
      
      isFullScreen: false,
      isCompactMode: false,
      focusedElement: null,
      hoveredItemId: null,
      editingItemId: null,
      
      windowSize: { width: 1280, height: 720 },
      windowPosition: { x: 0, y: 0 },
      isMaximized: false,
      
      undoStack: [],
      redoStack: [],
      maxUndoSteps: 20,
      
      lastSaved: null,
      isHydrated: false,

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

      toggleSidebarCollapsed: () => {
        set((state) => {
          state.sidebarCollapsed = !state.sidebarCollapsed;
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // MODAL ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      openModal: (type, data, options) => {
        set((state) => {
          state.modals[type] = {
            type,
            isOpen: true,
            data,
            closeOnEscape: true,
            closeOnBackdrop: true,
            ...options,
          };
          state.activeModal = type;
          
          // Add to modal stack
          if (!state.modalStack.includes(type)) {
            state.modalStack.push(type);
          }
        });
      },

      closeModal: (type) => {
        set((state) => {
          const modal = state.modals[type];
          if (modal?.onClose) {
            modal.onClose();
          }
          delete state.modals[type];
          
          // Remove from modal stack
          state.modalStack = state.modalStack.filter((t) => t !== type);
          
          // Set active modal to previous in stack
          state.activeModal = state.modalStack[state.modalStack.length - 1] || null;
        });
      },

      closeAllModals: () => {
        set((state) => {
          Object.values(state.modals).forEach((modal) => {
            if (modal.onClose) {
              modal.onClose();
            }
          });
          state.modals = {};
          state.modalStack = [];
          state.activeModal = null;
        });
      },

      closeTopModal: () => {
        const state = get();
        if (state.modalStack.length > 0) {
          const topModal = state.modalStack[state.modalStack.length - 1];
          get().closeModal(topModal);
        }
      },

      updateModalData: (type, data) => {
        set((state) => {
          const modal = state.modals[type];
          if (modal) {
            modal.data = { ...modal.data, ...data };
          }
        });
      },

      getModalStack: () => get().modalStack,

      // ═════════════════════════════════════════════════════════════════════════
      // TOAST ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      addToast: (toast) => {
        const id = `toast_${generateId()}`;
        set((state) => {
          state.toasts.push({ ...toast, id, createdAt: new Date() });
          
          // Remove oldest if exceeding max
          if (state.toasts.length > state.maxToasts) {
            state.toasts.shift();
          }
        });
        return id;
      },

      updateToast: (id, updates) => {
        set((state) => {
          const index = state.toasts.findIndex((t) => t.id === id);
          if (index !== -1) {
            state.toasts[index] = { ...state.toasts[index], ...updates };
          }
        });
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

      addSuccessToast: (title, message) => {
        return get().addToast({ type: 'success', title, message, duration: 5000 });
      },

      addErrorToast: (title, message) => {
        return get().addToast({ type: 'error', title, message, duration: 8000 });
      },

      addWarningToast: (title, message) => {
        return get().addToast({ type: 'warning', title, message, duration: 6000 });
      },

      addLoadingToast: (title, message) => {
        return get().addToast({ type: 'loading', title, message, persistent: true });
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
            state.loadingIndeterminate = false;
          }
        });
      },

      setLoadingProgress: (progress) => {
        set((state) => {
          state.loadingProgress = Math.min(100, Math.max(0, progress));
        });
      },

      setLoadingIndeterminate: (indeterminate) => {
        set((state) => {
          state.loadingIndeterminate = indeterminate;
        });
      },

      startLoadingOperation: (id, message) => {
        set((state) => {
          state.loadingOperations[id] = { progress: 0, message };
          state.isLoading = true;
        });
      },

      updateLoadingOperation: (id, progress, message) => {
        set((state) => {
          if (state.loadingOperations[id]) {
            state.loadingOperations[id].progress = progress;
            if (message) {
              state.loadingOperations[id].message = message;
            }
          }
        });
      },

      endLoadingOperation: (id) => {
        set((state) => {
          delete state.loadingOperations[id];
          state.isLoading = Object.keys(state.loadingOperations).length > 0;
        });
      },

      clearLoadingOperations: () => {
        set((state) => {
          state.loadingOperations = {};
          state.isLoading = false;
          state.loadingProgress = 0;
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

      addToSearchHistory: (query) => {
        set((state) => {
          // Remove if exists
          state.searchHistory = state.searchHistory.filter((q) => q !== query);
          // Add to beginning
          state.searchHistory.unshift(query);
          // Limit size
          if (state.searchHistory.length > state.maxSearchHistory) {
            state.searchHistory = state.searchHistory.slice(0, state.maxSearchHistory);
          }
        });
      },

      clearSearchHistory: () => {
        set((state) => {
          state.searchHistory = [];
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // LAYOUT ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      setViewMode: (mode) => {
        set((state) => {
          state.layout.viewMode = mode;
        });
      },

      toggleColumn: (columnId) => {
        set((state) => {
          const column = state.layout.columns.find((c) => c.id === columnId);
          if (column) {
            column.visible = !column.visible;
          }
        });
      },

      setColumnWidth: (columnId, width) => {
        set((state) => {
          const column = state.layout.columns.find((c) => c.id === columnId);
          if (column && column.resizable) {
            column.width = Math.max(50, Math.min(500, width));
          }
        });
      },

      setSort: (sortBy, direction) => {
        set((state) => {
          state.layout.sortBy = sortBy;
          state.layout.sortDirection = direction;
        });
      },

      setGroupBy: (groupBy) => {
        set((state) => {
          state.layout.groupBy = groupBy;
        });
      },

      toggleThumbnails: () => {
        set((state) => {
          state.layout.showThumbnails = !state.layout.showThumbnails;
        });
      },

      setThumbnailSize: (size) => {
        set((state) => {
          state.layout.thumbnailSize = Math.max(32, Math.min(256, size));
        });
      },

      toggleDetails: () => {
        set((state) => {
          state.layout.showDetails = !state.layout.showDetails;
        });
      },

      toggleCompactRows: () => {
        set((state) => {
          state.layout.compactRows = !state.layout.compactRows;
        });
      },

      resetLayout: () => {
        set((state) => {
          state.layout = { ...DEFAULT_LAYOUT };
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // PANEL ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      openPanel: (id, position, size) => {
        set((state) => {
          state.panels[id] = {
            id,
            position,
            size,
            isOpen: true,
            isResizable: true,
          };
        });
      },

      closePanel: (id) => {
        set((state) => {
          if (state.panels[id]) {
            state.panels[id].isOpen = false;
          }
        });
      },

      togglePanel: (id) => {
        set((state) => {
          if (state.panels[id]) {
            state.panels[id].isOpen = !state.panels[id].isOpen;
          }
        });
      },

      setPanelSize: (id, size) => {
        set((state) => {
          const panel = state.panels[id];
          if (panel) {
            const minSize = panel.minSize || 100;
            const maxSize = panel.maxSize || 800;
            panel.size = Math.max(minSize, Math.min(maxSize, size));
          }
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // SELECTION ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      selectItem: (id, index) => {
        set((state) => {
          if (!state.selectedItems.includes(id)) {
            state.selectedItems.push(id);
          }
          if (index !== undefined) {
            state.lastSelectedIndex = index;
          }
        });
      },

      deselectItem: (id) => {
        set((state) => {
          state.selectedItems = state.selectedItems.filter((i) => i !== id);
        });
      },

      toggleSelectItem: (id, index) => {
        set((state) => {
          if (state.selectedItems.includes(id)) {
            state.selectedItems = state.selectedItems.filter((i) => i !== id);
          } else {
            state.selectedItems.push(id);
          }
          if (index !== undefined) {
            state.lastSelectedIndex = index;
          }
        });
      },

      selectRange: (start, end) => {
        set((state) => {
          // This would need to be called with all IDs in range
          state.lastSelectedIndex = end;
        });
      },

      selectAll: (ids) => {
        set((state) => {
          state.selectedItems = [...ids];
        });
      },

      deselectAll: () => {
        set((state) => {
          state.selectedItems = [];
          state.lastSelectedIndex = -1;
        });
      },

      getSelectedItems: () => get().selectedItems,

      // ═════════════════════════════════════════════════════════════════════════
      // DRAG ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      startDrag: (itemIds, from, position) => {
        set((state) => {
          state.drag = {
            isDragging: true,
            draggedItemIds: itemIds,
            draggedFrom: from,
            position,
          };
        });
      },

      updateDragPosition: (position) => {
        set((state) => {
          state.drag.position = position;
        });
      },

      endDrag: () => {
        set((state) => {
          state.drag = {
            isDragging: false,
            draggedItemIds: [],
            draggedFrom: '',
          };
        });
      },

      setDragTarget: (to) => {
        set((state) => {
          state.drag.draggedTo = to;
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // CONTEXT MENU ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      openContextMenu: (position, items, targetId, targetType) => {
        set((state) => {
          state.contextMenu = {
            isOpen: true,
            position,
            targetId,
            targetType,
            items,
          };
        });
      },

      closeContextMenu: () => {
        set((state) => {
          state.contextMenu = {
            isOpen: false,
            position: { x: 0, y: 0 },
            items: [],
          };
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // OTHER ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      toggleFullScreen: () => {
        set((state) => {
          state.isFullScreen = !state.isFullScreen;
        });

        if (typeof document !== 'undefined') {
          if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen?.();
          } else {
            document.exitFullscreen?.();
          }
        }
      },

      setFullScreen: (fullScreen) => {
        set((state) => {
          state.isFullScreen = fullScreen;
        });
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

      setHoveredItem: (id) => {
        set((state) => {
          state.hoveredItemId = id;
        });
      },

      setEditingItem: (id) => {
        set((state) => {
          state.editingItemId = id;
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // WINDOW ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      updateWindowSize: (size) => {
        set((state) => {
          state.windowSize = size;
        });
      },

      updateWindowPosition: (position) => {
        set((state) => {
          state.windowPosition = position;
        });
      },

      toggleMaximized: () => {
        set((state) => {
          state.isMaximized = !state.isMaximized;
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // UNDO/REDO
      // ═════════════════════════════════════════════════════════════════════════

      undo: () => {
        const state = get();
        if (state.undoStack.length === 0) return false;

        const previousState = state.undoStack[state.undoStack.length - 1];
        
        set((s) => {
          s.redoStack.push({
            state: {
              sidebarOpen: s.sidebarOpen,
              sidebarWidth: s.sidebarWidth,
              layout: { ...s.layout },
            },
            timestamp: Date.now(),
            action: 'redo',
          });
          
          if (previousState.state.sidebarOpen !== undefined) {
            s.sidebarOpen = previousState.state.sidebarOpen;
          }
          if (previousState.state.sidebarWidth !== undefined) {
            s.sidebarWidth = previousState.state.sidebarWidth;
          }
          if (previousState.state.layout) {
            s.layout = { ...s.layout, ...previousState.state.layout } as LayoutPreferences;
          }
          
          s.undoStack.pop();
        });

        return true;
      },

      redo: () => {
        const state = get();
        if (state.redoStack.length === 0) return false;

        const nextState = state.redoStack[state.redoStack.length - 1];
        
        set((s) => {
          s.undoStack.push({
            state: {
              sidebarOpen: s.sidebarOpen,
              sidebarWidth: s.sidebarWidth,
              layout: { ...s.layout },
            },
            timestamp: Date.now(),
            action: 'undo',
          });
          
          if (nextState.state.sidebarOpen !== undefined) {
            s.sidebarOpen = nextState.state.sidebarOpen;
          }
          if (nextState.state.sidebarWidth !== undefined) {
            s.sidebarWidth = nextState.state.sidebarWidth;
          }
          if (nextState.state.layout) {
            s.layout = { ...s.layout, ...nextState.state.layout } as LayoutPreferences;
          }
          
          s.redoStack.pop();
        });

        return true;
      },

      canUndo: () => get().undoStack.length > 0,
      canRedo: () => get().redoStack.length > 0,

      clearHistory: () => {
        set((state) => {
          state.undoStack = [];
          state.redoStack = [];
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // PERSISTENCE
      // ═════════════════════════════════════════════════════════════════════════

      saveToStorage: () => {
        set((state) => {
          state.lastSaved = new Date();
        });
      },

      loadFromStorage: () => {
        set((state) => {
          state.isHydrated = true;
        });
      },

      setHydrated: (hydrated) => {
        set((state) => {
          state.isHydrated = hydrated;
        });
      },

      resetUI: () => {
        set((state) => {
          state.sidebarOpen = true;
          state.sidebarTab = 'downloads';
          state.sidebarWidth = 280;
          state.sidebarCollapsed = false;
          state.modals = {};
          state.activeModal = null;
          state.modalStack = [];
          state.toasts = [];
          state.isLoading = false;
          state.searchOpen = false;
          state.searchQuery = '';
          state.layout = { ...DEFAULT_LAYOUT };
          state.panels = {};
          state.selectedItems = [];
          state.isFullScreen = false;
          state.isCompactMode = false;
        });
      },
    })),
    {
      name: 'rs-toolkit-ui',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        sidebarOpen: state.sidebarOpen,
        sidebarWidth: state.sidebarWidth,
        sidebarCollapsed: state.sidebarCollapsed,
        layout: state.layout,
        searchHistory: state.searchHistory.slice(0, 10),
        windowSize: state.windowSize,
        isCompactMode: state.isCompactMode,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.isHydrated = true;
          state.lastSaved = new Date();
        }
      },
    }
  )
);

// ═══════════════════════════════════════════════════════════════════════════════
// SELECTORS
// ═══════════════════════════════════════════════════════════════════════════════

export const selectSidebarOpen = (state: UIStore) => state.sidebarOpen;
export const selectSidebarTab = (state: UIStore) => state.sidebarTab;
export const selectActiveModal = (state: UIStore) => state.activeModal;
export const selectToasts = (state: UIStore) => state.toasts;
export const selectIsLoading = (state: UIStore) => state.isLoading;
export const selectLayout = (state: UIStore) => state.layout;
export const selectViewMode = (state: UIStore) => state.layout.viewMode;
export const selectSelectedItems = (state: UIStore) => state.selectedItems;
export const selectSearchOpen = (state: UIStore) => state.searchOpen;
export const selectContextMenu = (state: UIStore) => state.contextMenu;
export const selectDragState = (state: UIStore) => state.drag;

export default useUIStore;
