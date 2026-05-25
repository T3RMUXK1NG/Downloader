/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   CLOUD SYNC v3.0.1 ULTIMATE NEXUS                           ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Cloud storage sync with multiple providers                     ║
 * ║  Features: Google Drive, Dropbox, OneDrive, S3, auto-sync, status            ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Cloud,
  CloudOff,
  RefreshCw,
  Check,
  AlertCircle,
  Settings,
  Unlink,
  Link2,
  Upload,
  Download,
  HardDrive,
  ChevronRight,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface CloudProvider {
  id: string;
  name: string;
  icon: string;
  connected: boolean;
  email?: string;
  usedSpace?: number;
  totalSpace?: number;
  lastSync?: Date;
}

export interface SyncStatus {
  isSyncing: boolean;
  progress: number;
  filesSynced: number;
  totalFiles: number;
  lastSync?: Date;
  error?: string;
}

export interface CloudSyncProps {
  /** Available providers */
  providers?: CloudProvider[];
  /** Current sync status */
  syncStatus?: SyncStatus;
  /** On connect provider */
  onConnect?: (providerId: string) => void;
  /** On disconnect provider */
  onDisconnect?: (providerId: string) => void;
  /** On sync now */
  onSync?: () => void;
  /** On open settings */
  onOpenSettings?: () => void;
  /** Auto sync enabled */
  autoSyncEnabled?: boolean;
  /** On toggle auto sync */
  onToggleAutoSync?: (enabled: boolean) => void;
  /** Additional class names */
  className?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// DEFAULT PROVIDERS
// ═══════════════════════════════════════════════════════════════════════════════

const defaultProviders: CloudProvider[] = [
  { id: 'google', name: 'Google Drive', icon: '📁', connected: false },
  { id: 'dropbox', name: 'Dropbox', icon: '📦', connected: false },
  { id: 'onedrive', name: 'OneDrive', icon: '☁️', connected: false },
  { id: 's3', name: 'Amazon S3', icon: '🪣', connected: false },
];

// ═══════════════════════════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
};

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export const CloudSync: React.FC<CloudSyncProps> = ({
  providers = defaultProviders,
  syncStatus,
  onConnect,
  onDisconnect,
  onSync,
  onOpenSettings,
  autoSyncEnabled = false,
  onToggleAutoSync,
  className,
}) => {
  const [expandedProvider, setExpandedProvider] = React.useState<string | null>(null);

  const connectedCount = providers.filter((p) => p.connected).length;
  const isSyncing = syncStatus?.isSyncing || false;

  const connectedProviders = providers.filter((p) => p.connected);
  const availableProviders = providers.filter((p) => !p.connected);

  return (
    <div
      className={cn(
        'rounded-2xl overflow-hidden',
        'bg-card/80 backdrop-blur-sm border border-border/50',
        'shadow-xl',
        className
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-border/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className={cn(
                'w-10 h-10 rounded-xl flex items-center justify-center',
                connectedCount > 0 ? 'bg-primary/20' : 'bg-muted/50'
              )}
            >
              {connectedCount > 0 ? (
                <Cloud className="w-5 h-5 text-primary" />
              ) : (
                <CloudOff className="w-5 h-5 text-muted-foreground" />
              )}
            </div>
            <div>
              <h3 className="font-semibold text-foreground">Cloud Sync</h3>
              <p className="text-xs text-muted-foreground">
                {connectedCount > 0
                  ? `${connectedCount} provider${connectedCount > 1 ? 's' : ''} connected`
                  : 'No providers connected'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Auto sync toggle */}
            <label className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-muted/50 cursor-pointer">
              <input
                type="checkbox"
                checked={autoSyncEnabled}
                onChange={(e) => onToggleAutoSync?.(e.target.checked)}
                className="sr-only"
              />
              <span className="text-xs text-muted-foreground">Auto</span>
              <div
                className={cn(
                  'w-8 h-4 rounded-full relative transition-colors',
                  autoSyncEnabled ? 'bg-primary' : 'bg-muted'
                )}
              >
                <motion.div
                  className="absolute top-0.5 w-3 h-3 rounded-full bg-white shadow-sm"
                  animate={{ left: autoSyncEnabled ? 18 : 2 }}
                />
              </div>
            </label>

            {/* Sync button */}
            {connectedCount > 0 && (
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={onSync}
                disabled={isSyncing}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground text-sm font-medium disabled:opacity-50"
              >
                {isSyncing ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <RefreshCw className="w-4 h-4" />
                )}
                Sync
              </motion.button>
            )}
          </div>
        </div>
      </div>

      {/* Sync progress */}
      <AnimatePresence>
        {isSyncing && syncStatus && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="border-b border-border/50 overflow-hidden"
          >
            <div className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Syncing...</span>
                <span className="text-sm font-medium text-foreground">
                  {syncStatus.filesSynced}/{syncStatus.totalFiles} files
                </span>
              </div>
              <div className="h-2 rounded-full bg-muted overflow-hidden">
                <motion.div
                  className="h-full bg-primary"
                  initial={{ width: 0 }}
                  animate={{ width: `${syncStatus.progress}%` }}
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Sync error */}
      <AnimatePresence>
        {syncStatus?.error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="p-3 bg-red-500/10 border-b border-border/50"
          >
            <p className="text-sm text-red-500 flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              {syncStatus.error}
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Connected providers */}
      {connectedProviders.length > 0 && (
        <div className="border-b border-border/50">
          <div className="px-4 py-2 bg-muted/30">
            <span className="text-xs font-medium text-muted-foreground">Connected</span>
          </div>
          <ul className="divide-y divide-border/50">
            {connectedProviders.map((provider) => (
              <li key={provider.id}>
                <button
                  onClick={() => setExpandedProvider(expandedProvider === provider.id ? null : provider.id)}
                  className="w-full p-4 flex items-center justify-between hover:bg-muted/30 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{provider.icon}</span>
                    <div className="text-left">
                      <p className="font-medium text-foreground">{provider.name}</p>
                      {provider.email && (
                        <p className="text-xs text-muted-foreground">{provider.email}</p>
                      )}
                    </div>
                  </div>
                  <ChevronRight
                    className={cn(
                      'w-4 h-4 text-muted-foreground transition-transform',
                      expandedProvider === provider.id && 'rotate-90'
                    )}
                  />
                </button>

                <AnimatePresence>
                  {expandedProvider === provider.id && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="px-4 pb-4 space-y-3">
                        {/* Storage info */}
                        {provider.usedSpace !== undefined && provider.totalSpace !== undefined && (
                          <div className="p-3 rounded-lg bg-muted/30">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-xs text-muted-foreground">Storage</span>
                              <span className="text-xs font-medium">
                                {formatBytes(provider.usedSpace)} / {formatBytes(provider.totalSpace)}
                              </span>
                            </div>
                            <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                              <div
                                className="h-full bg-primary rounded-full"
                                style={{
                                  width: `${(provider.usedSpace / provider.totalSpace) * 100}%`,
                                }}
                              />
                            </div>
                          </div>
                        )}

                        {/* Last sync */}
                        {provider.lastSync && (
                          <p className="text-xs text-muted-foreground">
                            Last synced: {provider.lastSync.toLocaleString()}
                          </p>
                        )}

                        {/* Actions */}
                        <div className="flex gap-2">
                          <button
                            onClick={() => onSync?.()}
                            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-muted/50 hover:bg-muted text-sm"
                          >
                            <RefreshCw className="w-4 h-4" />
                            Sync Now
                          </button>
                          <button
                            onClick={() => onDisconnect?.(provider.id)}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-red-500/10 text-red-500 hover:bg-red-500/20 text-sm"
                          >
                            <Unlink className="w-4 h-4" />
                            Disconnect
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Available providers */}
      {availableProviders.length > 0 && (
        <div>
          <div className="px-4 py-2 bg-muted/30">
            <span className="text-xs font-medium text-muted-foreground">Available Providers</span>
          </div>
          <ul className="divide-y divide-border/50">
            {availableProviders.map((provider) => (
              <motion.li
                key={provider.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <button
                  onClick={() => onConnect?.(provider.id)}
                  className="w-full p-4 flex items-center justify-between hover:bg-muted/30 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{provider.icon}</span>
                    <span className="font-medium text-foreground">{provider.name}</span>
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary/10 text-primary text-sm font-medium"
                  >
                    <Link2 className="w-4 h-4" />
                    Connect
                  </motion.button>
                </button>
              </motion.li>
            ))}
          </ul>
        </div>
      )}

      {/* Footer */}
      <div className="px-4 py-3 border-t border-border/50 bg-muted/30">
        <div className="flex items-center justify-between">
          <p className="text-xs text-muted-foreground flex items-center gap-1">
            <HardDrive className="w-3 h-3" />
            {connectedCount} provider{connectedCount !== 1 ? 's' : ''} connected
          </p>
          {onOpenSettings && (
            <button
              onClick={onOpenSettings}
              className="text-xs text-primary hover:underline flex items-center gap-1"
            >
              <Settings className="w-3 h-3" />
              Settings
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CloudSync;
