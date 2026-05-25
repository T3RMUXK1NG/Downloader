/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   COMPONENTS INDEX v3.0.1 ULTIMATE NEXUS                     ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Export all UI components for RS TOOLKIT                        ║
 * ║  Features: 15 production-ready components with animations & accessibility    ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

// ═══════════════════════════════════════════════════════════════════════════════
// DOWNLOAD & MEDIA COMPONENTS
// ═══════════════════════════════════════════════════════════════════════════════

export { DownloadCard, type DownloadCardProps } from './DownloadCard';
export { VideoPlayer, type VideoPlayerProps } from './VideoPlayer';
export { AudioWaveform, type AudioWaveformProps } from './AudioWaveform';
export { ProgressBar, CircularProgress, type ProgressBarProps, type CircularProgressProps } from './ProgressBar';

// ═══════════════════════════════════════════════════════════════════════════════
// SETTINGS & CONFIGURATION COMPONENTS
// ═══════════════════════════════════════════════════════════════════════════════

export { SettingsPanel, type SettingsPanelProps, type SettingItem, type SettingsCategory } from './SettingsPanel';
export { SpeedLimiter, type SpeedLimiterProps, type SpeedPreset } from './SpeedLimiter';
export { ProxyConfig, type ProxyConfigProps, type ProxyConfig as ProxyConfigType } from './ProxyConfig';
export { ScheduleDialog, type ScheduleDialogProps, type ScheduleConfig } from './ScheduleDialog';

// ═══════════════════════════════════════════════════════════════════════════════
// BROWSING & NAVIGATION COMPONENTS
// ═══════════════════════════════════════════════════════════════════════════════

export { HistoryList, type HistoryListProps, type HistoryItem } from './HistoryList';
export { PlatformGrid, type PlatformGridProps, type Platform } from './PlatformGrid';
export { SearchBar, type SearchBarProps, type SearchSuggestion } from './SearchBar';

// ═══════════════════════════════════════════════════════════════════════════════
// UI & THEMING COMPONENTS
// ═══════════════════════════════════════════════════════════════════════════════

export { ThemeToggle, MiniThemeToggle, ThemeProvider, useTheme, type ThemeToggleProps, type MiniThemeToggleProps, type Theme, type ThemeProviderProps } from './ThemeToggle';
export { LanguageSelector, LanguageProvider, useLanguage, type LanguageSelectorProps, type Language, type LanguageProviderProps } from './LanguageSelector';
export { NotificationToast, ToastContainer, ToastProvider, useToast, createToastHelpers, type NotificationToastProps, type ToastContainerProps, type ToastProviderProps, type Toast, type ToastType, type ToastAction } from './NotificationToast';

// ═══════════════════════════════════════════════════════════════════════════════
// CLOUD & SYNC COMPONENTS
// ═══════════════════════════════════════════════════════════════════════════════

export { CloudSync, type CloudSyncProps, type CloudProvider, type SyncStatus } from './CloudSync';
