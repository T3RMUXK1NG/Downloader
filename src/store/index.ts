/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    STORE INDEX v3.0.1 ULTIMATE NEXUS                          ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Central export for all Zustand stores                         ║
 * ║  Features: Download, Settings, History, UI state management                 ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module store/index
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

// ═══════════════════════════════════════════════════════════════════════════════
// STORE EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export {
  useDownloadStore,
  type DownloadStore,
  type DownloadQueueItem,
} from './downloadStore';

export {
  useSettingsStore,
  type SettingsStore,
  type AppSettings,
  type DownloadSettings,
  type SubtitleSettings,
  type MetadataSettings,
  type NetworkSettings,
  type UISettings,
  type HistorySettings,
  type SecuritySettings,
  DEFAULT_APP_SETTINGS,
} from './settingsStore';

export {
  useHistoryStore,
  type HistoryStore,
  type HistoryItem,
  type HistoryStats,
} from './historyStore';

export {
  useUIStore,
  type UIStore,
  type ModalType,
  type SidebarTab,
  type ModalState,
  type ToastState,
} from './uiStore';
