/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    HOOKS INDEX v3.0.1 ULTIMATE NEXUS                          ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Central export for all custom hooks                           ║
 * ║  Features: Download, History, Settings, WebSocket, Theme, i18n, etc.        ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module hooks/index
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

// ═══════════════════════════════════════════════════════════════════════════════
// HOOK EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export { useDownload, type UseDownloadOptions, type UseDownloadReturn, type DownloadOptions } from './useDownload';
export { useHistory, type UseHistoryOptions, type UseHistoryReturn, type HistoryItem, type HistoryFilter, type HistorySort, type HistoryStats } from './useHistory';
export { useSettings, type UseSettingsOptions, type UseSettingsReturn, type AppSettings, DEFAULT_SETTINGS } from './useSettings';
export { useWebSocket, type UseWebSocketOptions, type UseWebSocketReturn, type ConnectionStatus } from './useWebSocket';
export { useTheme, type UseThemeOptions, type UseThemeReturn, type Theme, type ResolvedTheme, type AccentColor, ACCENT_COLORS } from './useTheme';
export { useLanguage, type UseLanguageOptions, type UseLanguageReturn, type LanguageCode, type Language, LANGUAGES } from './useLanguage';
export { useNotifications, type UseNotificationsOptions, type UseNotificationsReturn, type Notification, type NotificationType, type NotificationPosition, type NotificationAction } from './useNotifications';
export { useKeyboard, type UseKeyboardOptions, type UseKeyboardReturn, type KeyboardShortcut, DEFAULT_SHORTCUTS } from './useKeyboard';
export { useDragDrop, type DragDropOptions, type UseDragDropReturn, type DroppedFile } from './useDragDrop';
export { useMediaQuery, type UseMediaQueryOptions, type UseMediaQueryReturn, type Breakpoint, type BreakpointConfig, DEFAULT_BREAKPOINTS } from './useMediaQuery';
