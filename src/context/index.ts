/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    CONTEXT INDEX v3.0.1 ULTIMATE NEXUS                        ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Central export for all context providers                      ║
 * ║  Features: App, Theme, Notification context management                      ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module context/index
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

// ═══════════════════════════════════════════════════════════════════════════════
// CONTEXT EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export {
  AppProvider,
  useApp,
  type AppConfig,
  type User,
  type Session,
  type AppState,
  type AppContextValue,
  type AppProviderProps,
} from './AppContext';

export {
  ThemeProvider,
  useThemeContext,
  type Theme,
  type ResolvedTheme,
  type AccentColor,
  type ThemeContextValue,
  type ThemeProviderProps,
  ACCENT_COLORS as THEME_ACCENT_COLORS,
} from './ThemeContext';

export {
  NotificationProvider,
  useNotificationContext,
  type NotificationType,
  type NotificationPosition,
  type NotificationAction,
  type Notification,
  type NotificationContextValue,
  type NotificationProviderProps,
} from './NotificationContext';
