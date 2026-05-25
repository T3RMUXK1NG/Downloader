/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    STORE INDEX v3.2.0 ULTIMATE NEXUS                          ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Central export for all Zustand stores                         ║
 * ║  Features: Download, Settings, History, UI state management                 ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module store/index
 * @version 3.2.0
 * @author RAJSARASWATI JATAV (RS)
 */

// ═══════════════════════════════════════════════════════════════════════════════
// DOWNLOAD STORE EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export {
  useDownloadStore,
  default as downloadStore,
  // Selectors
  selectActiveCount,
  selectQueueLength,
  createSelectByStatus,
  selectProgress,
  selectQueueItem,
  selectCategories,
  selectTags,
  selectRules,
  selectSessionStats,
} from './downloadStore';

export type {
  DownloadStore,
  DownloadStoreState,
  DownloadStoreActions,
  DownloadQueueItem,
  DownloadCategory,
  DownloadTag,
  DownloadRule,
  DownloadRuleCondition,
  DownloadRuleAction,
  DownloadSchedule,
  SpeedLimitRule,
  DownloadStats,
  QueueStats,
} from './downloadStore';

// ═══════════════════════════════════════════════════════════════════════════════
// SETTINGS STORE EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export {
  useSettingsStore,
  default as settingsStore,
  DEFAULT_APP_SETTINGS,
  // Selectors
  selectSettings,
  selectDownloadSettings,
  selectThemeSettings,
  selectNotificationSettings,
  selectShortcuts,
  selectUISettings,
  selectNetworkSettings,
  selectSecuritySettings,
  selectProfiles,
  selectIsDirty,
} from './settingsStore';

export type {
  SettingsStore,
  SettingsStoreState,
  SettingsStoreActions,
  AppSettings,
  DownloadSettings,
  SubtitleSettings,
  MetadataSettings,
  NetworkSettings,
  ThemeSettings,
  KeyboardShortcut,
  KeyboardShortcutsConfig,
  NotificationSettings,
  HistorySettings as HistorySettingsConfig,
  SecuritySettings,
  AdvancedSettings,
  UIPreferences,
  SettingsProfile,
  ValidationResult,
} from './settingsStore';

// ═══════════════════════════════════════════════════════════════════════════════
// HISTORY STORE EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export {
  useHistoryStore,
  default as historyStore,
  // Selectors
  selectHistoryItems,
  selectHistoryFilter,
  selectHistorySort,
  selectHistoryPagination,
  selectSelectedIds,
  selectHistoryStats,
} from './historyStore';

export type {
  HistoryStore,
  HistoryStoreState,
  HistoryStoreActions,
  HistoryItem,
  HistoryMetadata,
  HistoryFilter,
  HistorySort,
  HistoryPagination,
  HistoryStats,
  HistoryExportOptions,
} from './historyStore';

// ═══════════════════════════════════════════════════════════════════════════════
// UI STORE EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export {
  useUIStore,
  default as uiStore,
  // Selectors
  selectSidebarOpen,
  selectSidebarTab,
  selectActiveModal,
  selectToasts,
  selectIsLoading,
  selectLayout,
  selectViewMode,
  selectSelectedItems as selectUISelectedItems,
  selectSearchOpen,
  selectContextMenu,
  selectDragState,
} from './uiStore';

export type {
  UIStore,
  UIStoreState,
  UIStoreActions,
  ModalType,
  SidebarTab,
  ViewMode,
  PanelPosition,
  ModalState,
  ToastType,
  ToastState,
  PanelState,
  ColumnConfig,
  LayoutPreferences,
  DragState,
  ContextMenuState,
  ContextMenuItem,
} from './uiStore';

// ═══════════════════════════════════════════════════════════════════════════════
// COMBINED STORE HOOKS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Hook to access all stores
 */
export const useStores = () => ({
  download: useDownloadStore(),
  settings: useSettingsStore(),
  history: useHistoryStore(),
  ui: useUIStore(),
});

/**
 * Hook to check if stores are hydrated
 */
export const useStoresHydrated = () => ({
  download: useDownloadStore((s) => s.isHydrated),
  settings: useSettingsStore((s) => s.isHydrated),
  history: useHistoryStore((s) => s.isHydrated),
  ui: useUIStore((s) => s.isHydrated),
});

// ═══════════════════════════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Clear all store data
 */
export const clearAllStores = () => {
  useDownloadStore.getState().clearDownloads();
  useDownloadStore.getState().clearQueue();
  useHistoryStore.getState().clearItems();
  useUIStore.getState().resetUI();
  useSettingsStore.getState().resetToDefaults();
};

/**
 * Export all store data
 */
export const exportAllStores = () => {
  return {
    download: useDownloadStore.getState(),
    settings: useSettingsStore.getState(),
    history: useHistoryStore.getState(),
    ui: useUIStore.getState(),
    exportedAt: new Date().toISOString(),
    version: '3.2.0',
  };
};

/**
 * Reset all undo/redo stacks
 */
export const clearAllUndoRedo = () => {
  useDownloadStore.getState().clearHistory();
  useSettingsStore.getState().clearHistory();
  useHistoryStore.getState().clearHistory();
  useUIStore.getState().clearHistory();
};

/**
 * Check if any store has unsaved changes
 */
export const hasUnsavedChanges = () => {
  return useSettingsStore.getState().isDirty;
};

/**
 * Save all stores to localStorage
 */
export const saveAllStores = () => {
  useDownloadStore.getState().saveToStorage();
  useSettingsStore.getState().markSaved();
  useHistoryStore.getState().saveToStorage();
  useUIStore.getState().saveToStorage();
};
