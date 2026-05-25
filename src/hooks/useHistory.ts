/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    USE HISTORY HOOK v3.0.1 ULTIMATE NEXUS                     ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Download history management hook                               ║
 * ║  Features: History CRUD, search, filter, export, statistics                 ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module hooks/useHistory
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

'use client';

import { useCallback, useEffect, useState, useMemo } from 'react';
import { useHistoryStore } from '@/store/historyStore';
import { DownloadStatus, FileType } from '@/types/api';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface HistoryItem {
  id: string;
  url: string;
  title?: string;
  filename: string;
  filePath: string;
  fileSize: number;
  fileType: FileType;
  status: DownloadStatus;
  downloadedAt: Date;
  duration?: number;
  thumbnail?: string;
  tags: string[];
  error?: string;
}

export interface HistoryFilter {
  search?: string;
  status?: DownloadStatus[];
  fileTypes?: FileType[];
  dateFrom?: Date;
  dateTo?: Date;
  tags?: string[];
  minSize?: number;
  maxSize?: number;
}

export interface HistorySort {
  field: 'downloadedAt' | 'fileSize' | 'title' | 'status';
  order: 'asc' | 'desc';
}

export interface HistoryStats {
  totalDownloads: number;
  totalSize: number;
  byStatus: Record<DownloadStatus, number>;
  byFileType: Record<FileType, number>;
  averageSize: number;
  successRate: number;
}

export interface UseHistoryOptions {
  /** Persist history to localStorage */
  persist?: boolean;
  /** Storage key for persistence */
  storageKey?: string;
  /** Maximum items to keep */
  maxItems?: number;
}

export interface UseHistoryReturn {
  /** History items */
  items: HistoryItem[];
  /** Filtered items */
  filteredItems: HistoryItem[];
  /** Current filter */
  filter: HistoryFilter;
  /** Current sort */
  sort: HistorySort;
  /** Statistics */
  stats: HistoryStats;
  /** Add item to history */
  add: (item: Omit<HistoryItem, 'id' | 'downloadedAt'>) => void;
  /** Update item */
  update: (id: string, updates: Partial<HistoryItem>) => void;
  /** Remove item */
  remove: (id: string) => void;
  /** Clear all history */
  clear: () => void;
  /** Set filter */
  setFilter: (filter: HistoryFilter) => void;
  /** Set sort */
  setSort: (sort: HistorySort) => void;
  /** Get item by ID */
  getById: (id: string) => HistoryItem | undefined;
  /** Search history */
  search: (query: string) => HistoryItem[];
  /** Export history */
  export: (format: 'json' | 'csv') => string;
  /** Import history */
  import: (data: string, format: 'json' | 'csv') => boolean;
  /** Get all tags */
  tags: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// HOOK IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * useHistory Hook
 * @description Download history management with filtering, sorting, and statistics
 * @param options Hook options
 * @returns History controls and state
 */
export function useHistory(options: UseHistoryOptions = {}): UseHistoryReturn {
  const {
    persist = true,
    storageKey = 'rs-toolkit-history',
    maxItems = 1000,
  } = options;

  // Store
  const { items, addItem, updateItem, removeItem, clearItems, setItems } = useHistoryStore();

  // Local state
  const [filter, setFilterState] = useState<HistoryFilter>({});
  const [sort, setSortState] = useState<HistorySort>({
    field: 'downloadedAt',
    order: 'desc',
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // PERSISTENCE
  // ═══════════════════════════════════════════════════════════════════════════

  // Load from storage
  useEffect(() => {
    if (!persist || typeof window === 'undefined') return;

    try {
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        const parsed = JSON.parse(stored) as HistoryItem[];
        setItems(parsed.map((item) => ({
          ...item,
          downloadedAt: new Date(item.downloadedAt),
        })));
      }
    } catch (error) {
      console.error('Failed to load history from storage:', error);
    }
  }, [persist, storageKey, setItems]);

  // Save to storage
  useEffect(() => {
    if (!persist || typeof window === 'undefined') return;

    try {
      localStorage.setItem(storageKey, JSON.stringify(items));
    } catch (error) {
      console.error('Failed to save history to storage:', error);
    }
  }, [items, persist, storageKey]);

  // ═══════════════════════════════════════════════════════════════════════════
  // FILTERING & SORTING
  // ═══════════════════════════════════════════════════════════════════════════

  const filteredItems = useMemo(() => {
    let result = [...items];

    // Search filter
    if (filter.search) {
      const searchLower = filter.search.toLowerCase();
      result = result.filter(
        (item) =>
          item.title?.toLowerCase().includes(searchLower) ||
          item.filename.toLowerCase().includes(searchLower) ||
          item.url.toLowerCase().includes(searchLower)
      );
    }

    // Status filter
    if (filter.status?.length) {
      result = result.filter((item) => filter.status!.includes(item.status));
    }

    // File type filter
    if (filter.fileTypes?.length) {
      result = result.filter((item) => filter.fileTypes!.includes(item.fileType));
    }

    // Date range filter
    if (filter.dateFrom) {
      result = result.filter((item) => new Date(item.downloadedAt) >= filter.dateFrom!);
    }
    if (filter.dateTo) {
      result = result.filter((item) => new Date(item.downloadedAt) <= filter.dateTo!);
    }

    // Tags filter
    if (filter.tags?.length) {
      result = result.filter((item) =>
        filter.tags!.some((tag) => item.tags.includes(tag))
      );
    }

    // Size range filter
    if (filter.minSize !== undefined) {
      result = result.filter((item) => item.fileSize >= filter.minSize!);
    }
    if (filter.maxSize !== undefined) {
      result = result.filter((item) => item.fileSize <= filter.maxSize!);
    }

    // Sorting
    result.sort((a, b) => {
      let comparison = 0;

      switch (sort.field) {
        case 'downloadedAt':
          comparison = new Date(a.downloadedAt).getTime() - new Date(b.downloadedAt).getTime();
          break;
        case 'fileSize':
          comparison = a.fileSize - b.fileSize;
          break;
        case 'title':
          comparison = (a.title || a.filename).localeCompare(b.title || b.filename);
          break;
        case 'status':
          comparison = a.status.localeCompare(b.status);
          break;
      }

      return sort.order === 'desc' ? -comparison : comparison;
    });

    return result;
  }, [items, filter, sort]);

  // ═══════════════════════════════════════════════════════════════════════════
  // STATISTICS
  // ═══════════════════════════════════════════════════════════════════════════

  const stats = useMemo((): HistoryStats => {
    const byStatus = {} as Record<DownloadStatus, number>;
    const byFileType = {} as Record<FileType, number>;
    let totalSize = 0;
    let successCount = 0;

    items.forEach((item) => {
      byStatus[item.status] = (byStatus[item.status] || 0) + 1;
      byFileType[item.fileType] = (byFileType[item.fileType] || 0) + 1;
      totalSize += item.fileSize;

      if (item.status === DownloadStatus.COMPLETED) {
        successCount++;
      }
    });

    return {
      totalDownloads: items.length,
      totalSize,
      byStatus,
      byFileType,
      averageSize: items.length > 0 ? totalSize / items.length : 0,
      successRate: items.length > 0 ? (successCount / items.length) * 100 : 0,
    };
  }, [items]);

  // ═══════════════════════════════════════════════════════════════════════════
  // CRUD OPERATIONS
  // ═══════════════════════════════════════════════════════════════════════════

  const add = useCallback((item: Omit<HistoryItem, 'id' | 'downloadedAt'>) => {
    const newItem: HistoryItem = {
      ...item,
      id: `history_${Date.now()}_${Math.random().toString(36).substring(2, 10)}`,
      downloadedAt: new Date(),
    };

    addItem(newItem);

    // Enforce max items limit
    if (items.length >= maxItems) {
      const sortedItems = [...items, newItem].sort(
        (a, b) => new Date(b.downloadedAt).getTime() - new Date(a.downloadedAt).getTime()
      );
      setItems(sortedItems.slice(0, maxItems));
    }
  }, [addItem, setItems, items.length, maxItems]);

  const update = useCallback((id: string, updates: Partial<HistoryItem>) => {
    updateItem(id, updates);
  }, [updateItem]);

  const remove = useCallback((id: string) => {
    removeItem(id);
  }, [removeItem]);

  const clear = useCallback(() => {
    clearItems();
  }, [clearItems]);

  const setFilter = useCallback((newFilter: HistoryFilter) => {
    setFilterState(newFilter);
  }, []);

  const setSort = useCallback((newSort: HistorySort) => {
    setSortState(newSort);
  }, []);

  const getById = useCallback((id: string): HistoryItem | undefined => {
    return items.find((item) => item.id === id);
  }, [items]);

  const search = useCallback((query: string): HistoryItem[] => {
    const queryLower = query.toLowerCase();
    return items.filter(
      (item) =>
        item.title?.toLowerCase().includes(queryLower) ||
        item.filename.toLowerCase().includes(queryLower) ||
        item.url.toLowerCase().includes(queryLower) ||
        item.tags.some((tag) => tag.toLowerCase().includes(queryLower))
    );
  }, [items]);

  // ═══════════════════════════════════════════════════════════════════════════
  // IMPORT/EXPORT
  // ═══════════════════════════════════════════════════════════════════════════

  const exportHistory = useCallback((format: 'json' | 'csv'): string => {
    if (format === 'json') {
      return JSON.stringify(items, null, 2);
    }

    // CSV format
    const headers = ['ID', 'URL', 'Title', 'Filename', 'File Path', 'File Size', 'File Type', 'Status', 'Downloaded At', 'Tags'];
    const rows = items.map((item) => [
      item.id,
      item.url,
      item.title || '',
      item.filename,
      item.filePath,
      item.fileSize.toString(),
      item.fileType,
      item.status,
      new Date(item.downloadedAt).toISOString(),
      item.tags.join(';'),
    ]);

    return [headers.join(','), ...rows.map((row) => row.map((cell) => `"${cell}"`).join(','))].join('\n');
  }, [items]);

  const importHistory = useCallback((data: string, format: 'json' | 'csv'): boolean => {
    try {
      if (format === 'json') {
        const parsed = JSON.parse(data) as HistoryItem[];
        setItems(parsed.map((item) => ({
          ...item,
          downloadedAt: new Date(item.downloadedAt),
        })));
        return true;
      }

      // CSV format
      const lines = data.split('\n').slice(1); // Skip header
      const newItems: HistoryItem[] = lines
        .filter((line) => line.trim())
        .map((line) => {
          const values = line.match(/(".*?"|[^",]+)(?=\s*,|\s*$)/g) || [];
          const cleanValues = values.map((v) => v.replace(/^"|"$/g, ''));

          return {
            id: cleanValues[0],
            url: cleanValues[1],
            title: cleanValues[2] || undefined,
            filename: cleanValues[3],
            filePath: cleanValues[4],
            fileSize: parseInt(cleanValues[5], 10),
            fileType: cleanValues[6] as FileType,
            status: cleanValues[7] as DownloadStatus,
            downloadedAt: new Date(cleanValues[8]),
            tags: cleanValues[9] ? cleanValues[9].split(';') : [],
          };
        });

      setItems(newItems);
      return true;
    } catch (error) {
      console.error('Failed to import history:', error);
      return false;
    }
  }, [setItems]);

  // ═══════════════════════════════════════════════════════════════════════════
  // TAGS
  // ═══════════════════════════════════════════════════════════════════════════

  const tags = useMemo(() => {
    const tagSet = new Set<string>();
    items.forEach((item) => item.tags.forEach((tag) => tagSet.add(tag)));
    return Array.from(tagSet).sort();
  }, [items]);

  // ═══════════════════════════════════════════════════════════════════════════
  // RETURN
  // ═══════════════════════════════════════════════════════════════════════════

  return {
    items,
    filteredItems,
    filter,
    sort,
    stats,
    add,
    update,
    remove,
    clear,
    setFilter,
    setSort,
    getById,
    search,
    export: exportHistory,
    import: importHistory,
    tags,
  };
}

export default useHistory;
