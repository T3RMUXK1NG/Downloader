/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   HISTORY LIST v3.0.1 ULTIMATE NEXUS                         ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Download history list with filtering and actions               ║
 * ║  Features: Search, filter, sort, batch actions, export, infinite scroll      ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  Filter,
  SortAsc,
  SortDesc,
  Download,
  Trash2,
  MoreVertical,
  ExternalLink,
  RefreshCw,
  Copy,
  CheckCircle,
  AlertCircle,
  Clock,
  HardDrive,
  FileVideo,
  FileAudio,
  FileText,
  Image,
  Archive,
  FolderOpen,
  Calendar,
  X,
} from 'lucide-react';
import { DownloadStatus } from '@/types/api';
import { cn } from '@/lib/utils';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface HistoryItem {
  id: string;
  title: string;
  url: string;
  filePath?: string;
  fileSize?: number;
  fileType: 'video' | 'audio' | 'image' | 'document' | 'archive' | 'unknown';
  status: DownloadStatus;
  progress: number;
  thumbnail?: string;
  platform?: string;
  downloadedAt: Date;
  duration?: number;
  error?: string;
}

export interface HistoryListProps {
  /** History items */
  items: HistoryItem[];
  /** On item click */
  onItemClick?: (item: HistoryItem) => void;
  /** On item delete */
  onItemDelete?: (item: HistoryItem) => void;
  /** On item retry */
  onItemRetry?: (item: HistoryItem) => void;
  /** On item open folder */
  onItemOpenFolder?: (item: HistoryItem) => void;
  /** On item download again */
  onItemDownloadAgain?: (item: HistoryItem) => void;
  /** On copy URL */
  onCopyUrl?: (item: HistoryItem) => void;
  /** On clear all */
  onClearAll?: () => void;
  /** On export */
  onExport?: () => void;
  /** Is loading */
  isLoading?: boolean;
  /** Additional class names */
  className?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
};

const formatDate = (date: Date): string => {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (days === 0) return 'Today';
  if (days === 1) return 'Yesterday';
  if (days < 7) return `${days} days ago`;
  return date.toLocaleDateString();
};

const getFileIcon = (type: HistoryItem['fileType']): React.ReactNode => {
  switch (type) {
    case 'video':
      return <FileVideo className="w-5 h-5" />;
    case 'audio':
      return <FileAudio className="w-5 h-5" />;
    case 'image':
      return <Image className="w-5 h-5" />;
    case 'document':
      return <FileText className="w-5 h-5" />;
    case 'archive':
      return <Archive className="w-5 h-5" />;
    default:
      return <Download className="w-5 h-5" />;
  }
};

const getStatusIcon = (status: DownloadStatus): React.ReactNode => {
  switch (status) {
    case DownloadStatus.COMPLETED:
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    case DownloadStatus.FAILED:
      return <AlertCircle className="w-4 h-4 text-red-500" />;
    case DownloadStatus.CANCELLED:
      return <X className="w-4 h-4 text-gray-500" />;
    default:
      return <Clock className="w-4 h-4 text-amber-500" />;
  }
};

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export const HistoryList: React.FC<HistoryListProps> = ({
  items,
  onItemClick,
  onItemDelete,
  onItemRetry,
  onItemOpenFolder,
  onItemDownloadAgain,
  onCopyUrl,
  onClearAll,
  onExport,
  isLoading = false,
  className,
}) => {
  const [searchQuery, setSearchQuery] = React.useState('');
  const [statusFilter, setStatusFilter] = React.useState<DownloadStatus | 'all'>('all');
  const [sortOrder, setSortOrder] = React.useState<'asc' | 'desc'>('desc');
  const [selectedItems, setSelectedItems] = React.useState<Set<string>>(new Set());
  const [activeMenu, setActiveMenu] = React.useState<string | null>(null);
  const [copiedId, setCopiedId] = React.useState<string | null>(null);

  const menuRef = React.useRef<HTMLDivElement>(null);

  // Close menu on outside click
  React.useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setActiveMenu(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Filter and sort items
  const filteredItems = React.useMemo(() => {
    return items
      .filter((item) => {
        const matchesSearch =
          !searchQuery ||
          item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.url.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesStatus = statusFilter === 'all' || item.status === statusFilter;
        return matchesSearch && matchesStatus;
      })
      .sort((a, b) => {
        const order = sortOrder === 'desc' ? -1 : 1;
        return order * (a.downloadedAt.getTime() - b.downloadedAt.getTime());
      });
  }, [items, searchQuery, statusFilter, sortOrder]);

  const toggleSelectAll = () => {
    if (selectedItems.size === filteredItems.length) {
      setSelectedItems(new Set());
    } else {
      setSelectedItems(new Set(filteredItems.map((i) => i.id)));
    }
  };

  const toggleSelectItem = (id: string) => {
    const newSelected = new Set(selectedItems);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedItems(newSelected);
  };

  const handleCopyUrl = (item: HistoryItem) => {
    navigator.clipboard.writeText(item.url);
    setCopiedId(item.id);
    setTimeout(() => setCopiedId(null), 2000);
    onCopyUrl?.(item);
  };

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
      <div className="p-4 border-b border-border/50 space-y-3">
        {/* Search and filters */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search history..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-background border border-input text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>

          <div className="flex gap-2">
            {/* Status filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as DownloadStatus | 'all')}
              className="px-3 py-2 rounded-xl border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            >
              <option value="all">All Status</option>
              <option value={DownloadStatus.COMPLETED}>Completed</option>
              <option value={DownloadStatus.FAILED}>Failed</option>
              <option value={DownloadStatus.CANCELLED}>Cancelled</option>
            </select>

            {/* Sort button */}
            <button
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              className="p-2 rounded-xl border border-input hover:bg-muted/50 transition-colors"
              title={`Sort ${sortOrder === 'asc' ? 'newest first' : 'oldest first'}`}
            >
              {sortOrder === 'asc' ? (
                <SortAsc className="w-4 h-4 text-muted-foreground" />
              ) : (
                <SortDesc className="w-4 h-4 text-muted-foreground" />
              )}
            </button>
          </div>
        </div>

        {/* Batch actions */}
        {selectedItems.size > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-between p-3 rounded-xl bg-primary/10"
          >
            <span className="text-sm text-primary font-medium">
              {selectedItems.size} selected
            </span>
            <div className="flex gap-2">
              <button
                onClick={() => setSelectedItems(new Set())}
                className="px-3 py-1.5 text-sm rounded-lg hover:bg-muted/50 transition-colors"
              >
                Clear
              </button>
              <button
                onClick={() => {
                  // Batch delete logic
                  setSelectedItems(new Set());
                }}
                className="px-3 py-1.5 text-sm rounded-lg bg-red-500/10 text-red-500 hover:bg-red-500/20 transition-colors"
              >
                Delete Selected
              </button>
            </div>
          </motion.div>
        )}
      </div>

      {/* List */}
      <div className="max-h-[500px] overflow-y-auto">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            >
              <RefreshCw className="w-8 h-8 text-muted-foreground" />
            </motion.div>
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
            <Clock className="w-12 h-12 mb-4 opacity-50" />
            <p className="text-sm">No download history</p>
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="mt-2 text-sm text-primary hover:underline"
              >
                Clear search
              </button>
            )}
          </div>
        ) : (
          <ul className="divide-y divide-border/50">
            <AnimatePresence>
              {filteredItems.map((item, index) => (
                <motion.li
                  key={item.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: index * 0.03 }}
                  className={cn(
                    'flex items-center gap-3 p-3 sm:p-4 hover:bg-muted/30 transition-colors cursor-pointer',
                    selectedItems.has(item.id) && 'bg-primary/5'
                  )}
                  onClick={() => onItemClick?.(item)}
                >
                  {/* Checkbox */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleSelectItem(item.id);
                    }}
                    className={cn(
                      'w-5 h-5 rounded border-2 flex items-center justify-center transition-colors',
                      selectedItems.has(item.id)
                        ? 'bg-primary border-primary'
                        : 'border-muted-foreground/30 hover:border-muted-foreground'
                    )}
                  >
                    {selectedItems.has(item.id) && (
                      <CheckCircle className="w-3 h-3 text-primary-foreground" />
                    )}
                  </button>

                  {/* Thumbnail/Icon */}
                  <div className="relative flex-shrink-0">
                    {item.thumbnail ? (
                      <img
                        src={item.thumbnail}
                        alt={item.title}
                        className="w-12 h-12 sm:w-14 sm:h-14 rounded-lg object-cover"
                      />
                    ) : (
                      <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-lg bg-muted flex items-center justify-center text-muted-foreground">
                        {getFileIcon(item.fileType)}
                      </div>
                    )}
                    <div className="absolute -bottom-1 -right-1">
                      {getStatusIcon(item.status)}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium text-foreground truncate">{item.title}</h4>
                    <div className="flex flex-wrap items-center gap-2 mt-1 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {formatDate(item.downloadedAt)}
                      </span>
                      {item.fileSize && (
                        <span className="flex items-center gap-1">
                          <HardDrive className="w-3 h-3" />
                          {formatBytes(item.fileSize)}
                        </span>
                      )}
                      {item.platform && (
                        <span className="px-1.5 py-0.5 rounded bg-muted/50 capitalize">
                          {item.platform}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="relative" ref={menuRef}>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setActiveMenu(activeMenu === item.id ? null : item.id);
                      }}
                      className="p-2 rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <MoreVertical className="w-4 h-4 text-muted-foreground" />
                    </button>

                    <AnimatePresence>
                      {activeMenu === item.id && (
                        <motion.div
                          initial={{ opacity: 0, scale: 0.95 }}
                          animate={{ opacity: 1, scale: 1 }}
                          exit={{ opacity: 0, scale: 0.95 }}
                          className="absolute right-0 top-full mt-1 z-50 min-w-[160px] rounded-xl border border-border bg-popover p-1 shadow-lg"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {item.status === DownloadStatus.COMPLETED && onItemOpenFolder && (
                            <button
                              onClick={() => {
                                onItemOpenFolder(item);
                                setActiveMenu(null);
                              }}
                              className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-lg hover:bg-muted/50"
                            >
                              <FolderOpen className="w-4 h-4" />
                              Open Folder
                            </button>
                          )}
                          <button
                            onClick={() => handleCopyUrl(item)}
                            className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-lg hover:bg-muted/50"
                          >
                            {copiedId === item.id ? (
                              <CheckCircle className="w-4 h-4 text-green-500" />
                            ) : (
                              <Copy className="w-4 h-4" />
                            )}
                            {copiedId === item.id ? 'Copied!' : 'Copy URL'}
                          </button>
                          {onItemDownloadAgain && (
                            <button
                              onClick={() => {
                                onItemDownloadAgain(item);
                                setActiveMenu(null);
                              }}
                              className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-lg hover:bg-muted/50"
                            >
                              <Download className="w-4 h-4" />
                              Download Again
                            </button>
                          )}
                          {item.status === DownloadStatus.FAILED && onItemRetry && (
                            <button
                              onClick={() => {
                                onItemRetry(item);
                                setActiveMenu(null);
                              }}
                              className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-lg hover:bg-muted/50"
                            >
                              <RefreshCw className="w-4 h-4" />
                              Retry
                            </button>
                          )}
                          {onItemDelete && (
                            <button
                              onClick={() => {
                                onItemDelete(item);
                                setActiveMenu(null);
                              }}
                              className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-lg hover:bg-destructive/10 text-destructive"
                            >
                              <Trash2 className="w-4 h-4" />
                              Delete
                            </button>
                          )}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </motion.li>
              ))}
            </AnimatePresence>
          </ul>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between p-4 border-t border-border/50 bg-muted/30">
        <span className="text-xs text-muted-foreground">
          {filteredItems.length} {filteredItems.length === 1 ? 'item' : 'items'}
        </span>
        <div className="flex gap-2">
          {onExport && (
            <button
              onClick={onExport}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg hover:bg-muted/50 transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              Export
            </button>
          )}
          {onClearAll && (
            <button
              onClick={onClearAll}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg hover:bg-destructive/10 text-destructive transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Clear All
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default HistoryList;
