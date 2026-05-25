/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   DOWNLOAD CARD v3.0.1 ULTIMATE NEXUS                        ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Beautiful download progress card with animations               ║
 * ║  Features: Progress tracking, speed display, ETA, pause/resume/cancel        ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Download,
  Pause,
  Play,
  X,
  CheckCircle,
  AlertCircle,
  Clock,
  HardDrive,
  Zap,
  MoreVertical,
  FolderOpen,
  Trash2,
  RefreshCw,
} from 'lucide-react';
import { DownloadStatus } from '@/types/api';
import { ProgressBar } from './ProgressBar';
import { cn } from '@/lib/utils';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface DownloadCardProps {
  /** Unique download identifier */
  id: string;
  /** Download title/filename */
  title: string;
  /** Source URL */
  url: string;
  /** Current download status */
  status: DownloadStatus;
  /** Download progress percentage (0-100) */
  progress: number;
  /** Downloaded bytes */
  downloadedBytes: number;
  /** Total bytes (0 if unknown) */
  totalBytes: number;
  /** Download speed in bytes/sec */
  speed: number;
  /** Estimated time remaining in seconds */
  eta: number;
  /** File type */
  fileType?: 'video' | 'audio' | 'image' | 'document' | 'unknown';
  /** Thumbnail URL */
  thumbnail?: string;
  /** Error message if failed */
  error?: string;
  /** On pause callback */
  onPause?: () => void;
  /** On resume callback */
  onResume?: () => void;
  /** On cancel callback */
  onCancel?: () => void;
  /** On retry callback */
  onRetry?: () => void;
  /** On delete callback */
  onDelete?: () => void;
  /** On open folder callback */
  onOpenFolder?: () => void;
  /** Additional class names */
  className?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

const formatSpeed = (bytesPerSec: number): string => {
  return `${formatBytes(bytesPerSec)}/s`;
};

const formatETA = (seconds: number): string => {
  if (seconds <= 0 || !isFinite(seconds)) return '--:--';
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
};

const getStatusColor = (status: DownloadStatus): string => {
  const colors: Record<DownloadStatus, string> = {
    [DownloadStatus.PENDING]: 'text-amber-500',
    [DownloadStatus.DOWNLOADING]: 'text-emerald-500',
    [DownloadStatus.PAUSED]: 'text-orange-500',
    [DownloadStatus.COMPLETED]: 'text-green-500',
    [DownloadStatus.FAILED]: 'text-red-500',
    [DownloadStatus.CANCELLED]: 'text-gray-500',
    [DownloadStatus.RETRYING]: 'text-yellow-500',
    [DownloadStatus.VALIDATING]: 'text-blue-500',
    [DownloadStatus.PROCESSING]: 'text-purple-500',
  };
  return colors[status] || 'text-gray-500';
};

const getStatusBgColor = (status: DownloadStatus): string => {
  const colors: Record<DownloadStatus, string> = {
    [DownloadStatus.PENDING]: 'bg-amber-500/10',
    [DownloadStatus.DOWNLOADING]: 'bg-emerald-500/10',
    [DownloadStatus.PAUSED]: 'bg-orange-500/10',
    [DownloadStatus.COMPLETED]: 'bg-green-500/10',
    [DownloadStatus.FAILED]: 'bg-red-500/10',
    [DownloadStatus.CANCELLED]: 'bg-gray-500/10',
    [DownloadStatus.RETRYING]: 'bg-yellow-500/10',
    [DownloadStatus.VALIDATING]: 'bg-blue-500/10',
    [DownloadStatus.PROCESSING]: 'bg-purple-500/10',
  };
  return colors[status] || 'bg-gray-500/10';
};

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export const DownloadCard: React.FC<DownloadCardProps> = ({
  id,
  title,
  url,
  status,
  progress,
  downloadedBytes,
  totalBytes,
  speed,
  eta,
  fileType = 'unknown',
  thumbnail,
  error,
  onPause,
  onResume,
  onCancel,
  onRetry,
  onDelete,
  onOpenFolder,
  className,
}) => {
  const [showMenu, setShowMenu] = React.useState(false);
  const menuRef = React.useRef<HTMLDivElement>(null);

  // Close menu on outside click
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const isDownloading = status === DownloadStatus.DOWNLOADING;
  const isPaused = status === DownloadStatus.PAUSED;
  const isCompleted = status === DownloadStatus.COMPLETED;
  const isFailed = status === DownloadStatus.FAILED;
  const isCancelled = status === DownloadStatus.CANCELLED;
  const isActive = isDownloading || isPaused;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      whileHover={{ scale: 1.01 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      className={cn(
        'relative overflow-hidden rounded-xl border border-border/50 bg-card/80 backdrop-blur-sm',
        'shadow-lg hover:shadow-xl transition-shadow duration-300',
        'dark:bg-card/60 dark:border-border/30',
        className
      )}
      role="article"
      aria-label={`Download: ${title}`}
    >
      {/* Progress glow effect */}
      {isActive && (
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-emerald-500/5 via-transparent to-emerald-500/5"
          animate={{
            opacity: [0.3, 0.6, 0.3],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      )}

      <div className="relative p-4 sm:p-5">
        {/* Header */}
        <div className="flex items-start gap-3 sm:gap-4">
          {/* Thumbnail/Icon */}
          <div className="relative flex-shrink-0">
            {thumbnail ? (
              <img
                src={thumbnail}
                alt={title}
                className="w-16 h-16 sm:w-20 sm:h-20 rounded-lg object-cover ring-2 ring-border/50"
              />
            ) : (
              <div
                className={cn(
                  'w-16 h-16 sm:w-20 sm:h-20 rounded-lg flex items-center justify-center',
                  'bg-gradient-to-br from-primary/20 to-primary/5',
                  getStatusBgColor(status)
                )}
              >
                <Download className="w-6 h-6 sm:w-8 sm:h-8 text-primary/60" />
              </div>
            )}

            {/* Status badge */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className={cn(
                'absolute -bottom-1 -right-1 w-5 h-5 sm:w-6 sm:h-6 rounded-full',
                'flex items-center justify-center shadow-md',
                getStatusBgColor(status)
              )}
            >
              {isCompleted ? (
                <CheckCircle className={cn('w-3.5 h-3.5 sm:w-4 sm:h-4', getStatusColor(status))} />
              ) : isFailed ? (
                <AlertCircle className={cn('w-3.5 h-3.5 sm:w-4 sm:h-4', getStatusColor(status))} />
              ) : (
                <Download className={cn('w-3 h-3 sm:w-3.5 sm:h-3.5', getStatusColor(status))} />
              )}
            </motion.div>
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-foreground truncate text-sm sm:text-base" title={title}>
                  {title}
                </h3>
                <p className="text-xs text-muted-foreground truncate mt-0.5" title={url}>
                  {url}
                </p>
              </div>

              {/* Menu button */}
              <div className="relative" ref={menuRef}>
                <button
                  onClick={() => setShowMenu(!showMenu)}
                  className="p-1.5 rounded-lg hover:bg-muted/50 transition-colors"
                  aria-label="More options"
                  aria-expanded={showMenu}
                >
                  <MoreVertical className="w-4 h-4 text-muted-foreground" />
                </button>

                <AnimatePresence>
                  {showMenu && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95, y: -10 }}
                      animate={{ opacity: 1, scale: 1, y: 0 }}
                      exit={{ opacity: 0, scale: 0.95, y: -10 }}
                      className="absolute right-0 top-full mt-1 z-50 min-w-[140px] rounded-lg border border-border bg-popover p-1 shadow-lg"
                    >
                      {onOpenFolder && (
                        <button
                          onClick={() => {
                            onOpenFolder();
                            setShowMenu(false);
                          }}
                          className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-md hover:bg-muted/50 transition-colors"
                        >
                          <FolderOpen className="w-4 h-4" />
                          Open Folder
                        </button>
                      )}
                      {onRetry && (isFailed || isCancelled) && (
                        <button
                          onClick={() => {
                            onRetry();
                            setShowMenu(false);
                          }}
                          className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-md hover:bg-muted/50 transition-colors"
                        >
                          <RefreshCw className="w-4 h-4" />
                          Retry
                        </button>
                      )}
                      {onDelete && (
                        <button
                          onClick={() => {
                            onDelete();
                            setShowMenu(false);
                          }}
                          className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-md hover:bg-destructive/10 text-destructive transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                          Delete
                        </button>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>

            {/* Status */}
            <div className="flex items-center gap-2 mt-2">
              <span
                className={cn(
                  'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium',
                  getStatusBgColor(status),
                  getStatusColor(status)
                )}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </span>
              {fileType !== 'unknown' && (
                <span className="text-xs text-muted-foreground capitalize">{fileType}</span>
              )}
            </div>
          </div>
        </div>

        {/* Progress bar */}
        {(isActive || isCompleted) && (
          <div className="mt-4">
            <ProgressBar
              value={progress}
              max={100}
              showLabel
              animated={isDownloading}
              className="h-2"
            />
          </div>
        )}

        {/* Error message */}
        {isFailed && error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-3 p-3 rounded-lg bg-destructive/10 border border-destructive/20"
          >
            <p className="text-xs text-destructive flex items-start gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </p>
          </motion.div>
        )}

        {/* Stats */}
        <div className="flex flex-wrap items-center gap-3 sm:gap-4 mt-4 text-xs text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <HardDrive className="w-3.5 h-3.5" />
            <span>
              {formatBytes(downloadedBytes)}
              {totalBytes > 0 && ` / ${formatBytes(totalBytes)}`}
            </span>
          </div>

          {isDownloading && speed > 0 && (
            <div className="flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-emerald-500" />
              <span>{formatSpeed(speed)}</span>
            </div>
          )}

          {isDownloading && eta > 0 && (
            <div className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5" />
              <span>{formatETA(eta)} left</span>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 mt-4">
          {isDownloading && onPause && (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onPause}
              className={cn(
                'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium',
                'bg-orange-500/10 text-orange-600 hover:bg-orange-500/20',
                'dark:text-orange-400 dark:hover:bg-orange-500/20',
                'transition-colors focus:outline-none focus:ring-2 focus:ring-orange-500/50'
              )}
              aria-label="Pause download"
            >
              <Pause className="w-4 h-4" />
              <span className="hidden sm:inline">Pause</span>
            </motion.button>
          )}

          {isPaused && onResume && (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onResume}
              className={cn(
                'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium',
                'bg-emerald-500/10 text-emerald-600 hover:bg-emerald-500/20',
                'dark:text-emerald-400 dark:hover:bg-emerald-500/20',
                'transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500/50'
              )}
              aria-label="Resume download"
            >
              <Play className="w-4 h-4" />
              <span className="hidden sm:inline">Resume</span>
            </motion.button>
          )}

          {isActive && onCancel && (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onCancel}
              className={cn(
                'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium',
                'bg-red-500/10 text-red-600 hover:bg-red-500/20',
                'dark:text-red-400 dark:hover:bg-red-500/20',
                'transition-colors focus:outline-none focus:ring-2 focus:ring-red-500/50'
              )}
              aria-label="Cancel download"
            >
              <X className="w-4 h-4" />
              <span className="hidden sm:inline">Cancel</span>
            </motion.button>
          )}

          {(isFailed || isCancelled) && onRetry && (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onRetry}
              className={cn(
                'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium',
                'bg-primary/10 text-primary hover:bg-primary/20',
                'transition-colors focus:outline-none focus:ring-2 focus:ring-primary/50'
              )}
              aria-label="Retry download"
            >
              <RefreshCw className="w-4 h-4" />
              <span className="hidden sm:inline">Retry</span>
            </motion.button>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default DownloadCard;
