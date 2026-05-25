/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    HISTORY STORE v3.2.0 ULTIMATE NEXUS                        ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Enhanced history state management with Zustand                  ║
 * ║  Features: CRUD, filtering, sorting, statistics, cleanup, persistence        ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module store/historyStore
 * @version 3.2.0
 * @author RAJSARASWATI JATAV (RS)
 */

import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { persist, createJSONStorage } from 'zustand/middleware';
import { DownloadStatus, FileType } from '@/types/api';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * History item interface
 */
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
  completedAt?: Date;
  duration?: number;
  thumbnail?: string;
  tags: string[];
  category?: string;
  error?: string;
  metadata?: HistoryMetadata;
  notes?: string;
  rating?: 1 | 2 | 3 | 4 | 5;
  favorite: boolean;
  archived: boolean;
  downloadSpeed?: number;
  source?: string;
}

/**
 * History metadata
 */
export interface HistoryMetadata {
  uploader?: string;
  uploadDate?: string;
  viewCount?: number;
  likeCount?: number;
  description?: string;
  format?: string;
  resolution?: string;
  bitrate?: number;
  fps?: number;
  codec?: string;
}

/**
 * History filter options
 */
export interface HistoryFilter {
  search?: string;
  status?: DownloadStatus[];
  fileTypes?: FileType[];
  tags?: string[];
  category?: string;
  dateRange?: {
    start: Date;
    end: Date;
  };
  sizeRange?: {
    min: number;
    max: number;
  };
  favorites?: boolean;
  archived?: boolean;
  rating?: number[];
}

/**
 * History sort options
 */
export interface HistorySort {
  field: 'downloadedAt' | 'fileSize' | 'title' | 'duration' | 'rating';
  direction: 'asc' | 'desc';
}

/**
 * History pagination
 */
export interface HistoryPagination {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

/**
 * History statistics
 */
export interface HistoryStats {
  totalItems: number;
  totalSize: number;
  successCount: number;
  failedCount: number;
  averageSize: number;
  averageSpeed: number;
  byFileType: Record<FileType, number>;
  byStatus: Record<DownloadStatus, number>;
  byDay: { date: string; count: number; size: number }[];
  topDomains: { domain: string; count: number }[];
  recentActivity: {
    today: number;
    thisWeek: number;
    thisMonth: number;
  };
}

/**
 * History export options
 */
export interface HistoryExportOptions {
  format: 'json' | 'csv' | 'txt';
  includeMetadata: boolean;
  includeThumbnails: boolean;
  dateRange?: { start: Date; end: Date };
  filter?: HistoryFilter;
}

/**
 * Undo/redo state
 */
interface UndoState {
  items: HistoryItem[];
  timestamp: number;
  action: string;
}

/**
 * Store state interface
 */
export interface HistoryStoreState {
  // Core state
  items: HistoryItem[];
  maxItems: number;
  
  // View state
  filter: HistoryFilter;
  sort: HistorySort;
  pagination: HistoryPagination;
  selectedIds: string[];
  
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
export interface HistoryStoreActions {
  // CRUD actions
  setItems: (items: HistoryItem[]) => void;
  addItem: (item: HistoryItem) => void;
  updateItem: (id: string, updates: Partial<HistoryItem>) => void;
  removeItem: (id: string) => void;
  clearItems: () => void;
  
  // Bulk actions
  removeMultiple: (ids: string[]) => void;
  updateMultiple: (ids: string[], updates: Partial<HistoryItem>) => void;
  clearByStatus: (status: DownloadStatus) => void;
  clearByFileType: (fileType: FileType) => void;
  clearOlderThan: (days: number) => void;
  clearByDateRange: (start: Date, end: Date) => void;
  
  // Tag actions
  addTag: (id: string, tag: string) => void;
  removeTag: (id: string, tag: string) => void;
  addTagToMultiple: (ids: string[], tag: string) => void;
  removeTagFromMultiple: (ids: string[], tag: string) => void;
  getAvailableTags: () => { tag: string; count: number }[];
  
  // Category actions
  setCategory: (id: string, category: string) => void;
  setCategoryToMultiple: (ids: string[], category: string) => void;
  
  // Favorite/Archive actions
  toggleFavorite: (id: string) => void;
  toggleArchive: (id: string) => void;
  setRating: (id: string, rating: 1 | 2 | 3 | 4 | 5 | undefined) => void;
  setNotes: (id: string, notes: string) => void;
  
  // Selection actions
  selectItem: (id: string) => void;
  deselectItem: (id: string) => void;
  toggleSelectItem: (id: string) => void;
  selectAll: () => void;
  deselectAll: () => void;
  selectByFilter: (filter: HistoryFilter) => void;
  
  // Filter/Sort actions
  setFilter: (filter: Partial<HistoryFilter>) => void;
  clearFilter: () => void;
  setSort: (sort: HistorySort) => void;
  setPagination: (pagination: Partial<HistoryPagination>) => void;
  
  // Computed selectors
  getFilteredItems: () => HistoryItem[];
  getPaginatedItems: () => HistoryItem[];
  getById: (id: string) => HistoryItem | undefined;
  getByUrl: (url: string) => HistoryItem[];
  getByStatus: (status: DownloadStatus) => HistoryItem[];
  getByFileType: (fileType: FileType) => HistoryItem[];
  getByTag: (tag: string) => HistoryItem[];
  getByCategory: (category: string) => HistoryItem[];
  search: (query: string) => HistoryItem[];
  getFavorites: () => HistoryItem[];
  getArchived: () => HistoryItem[];
  getStats: () => HistoryStats;
  getRecentItems: (limit?: number) => HistoryItem[];
  getDuplicateUrls: () => { url: string; items: HistoryItem[] }[];
  
  // Export/Import
  exportHistory: (options: HistoryExportOptions) => string;
  importHistory: (data: string, format: 'json' | 'csv') => number;
  
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
}

/**
 * Combined store type
 */
export type HistoryStore = HistoryStoreState & HistoryStoreActions;

// ═══════════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

const generateId = (): string => `hist_${Date.now()}_${Math.random().toString(36).substring(2, 10)}`;

const createUndoSnapshot = (items: HistoryItem[], action: string): UndoState => ({
  items: items.slice(0, 100),
  timestamp: Date.now(),
  action,
});

/**
 * Extract domain from URL
 */
const extractDomain = (url: string): string => {
  try {
    return new URL(url).hostname;
  } catch {
    return 'unknown';
  }
};

/**
 * Check if item matches filter
 */
const matchesFilter = (item: HistoryItem, filter: HistoryFilter): boolean => {
  // Search
  if (filter.search) {
    const searchLower = filter.search.toLowerCase();
    const matches =
      item.title?.toLowerCase().includes(searchLower) ||
      item.filename.toLowerCase().includes(searchLower) ||
      item.url.toLowerCase().includes(searchLower) ||
      item.tags.some((t) => t.toLowerCase().includes(searchLower));
    if (!matches) return false;
  }

  // Status
  if (filter.status && filter.status.length > 0) {
    if (!filter.status.includes(item.status)) return false;
  }

  // File types
  if (filter.fileTypes && filter.fileTypes.length > 0) {
    if (!filter.fileTypes.includes(item.fileType)) return false;
  }

  // Tags
  if (filter.tags && filter.tags.length > 0) {
    if (!filter.tags.some((t) => item.tags.includes(t))) return false;
  }

  // Category
  if (filter.category && item.category !== filter.category) return false;

  // Date range
  if (filter.dateRange) {
    const date = new Date(item.downloadedAt);
    if (date < filter.dateRange.start || date > filter.dateRange.end) return false;
  }

  // Size range
  if (filter.sizeRange) {
    if (item.fileSize < filter.sizeRange.min || item.fileSize > filter.sizeRange.max) return false;
  }

  // Favorites
  if (filter.favorites === true && !item.favorite) return false;

  // Archived
  if (filter.archived !== undefined && item.archived !== filter.archived) return false;

  // Rating
  if (filter.rating && filter.rating.length > 0) {
    if (!item.rating || !filter.rating.includes(item.rating)) return false;
  }

  return true;
};

// ═══════════════════════════════════════════════════════════════════════════════
// STORE IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

export const useHistoryStore = create<HistoryStore>()(
  persist(
    immer((set, get) => ({
      // ═════════════════════════════════════════════════════════════════════════
      // INITIAL STATE
      // ═════════════════════════════════════════════════════════════════════════
      items: [],
      maxItems: 1000,
      
      filter: {},
      sort: { field: 'downloadedAt', direction: 'desc' },
      pagination: { page: 1, limit: 50, total: 0, totalPages: 0 },
      selectedIds: [],
      
      undoStack: [],
      redoStack: [],
      maxUndoSteps: 50,
      
      lastSaved: null,
      isHydrated: false,

      // ═════════════════════════════════════════════════════════════════════════
      // CRUD ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      setItems: (items) => {
        set((state) => {
          state.items = items;
          state.pagination.total = items.length;
          state.pagination.totalPages = Math.ceil(items.length / state.pagination.limit);
        });
      },

      addItem: (item) => {
        set((state) => {
          state.undoStack.push(createUndoSnapshot(state.items, 'addItem'));
          if (state.undoStack.length > state.maxUndoSteps) {
            state.undoStack.shift();
          }
          state.redoStack = [];
          
          state.items.unshift(item);
          
          if (state.items.length > state.maxItems) {
            state.items = state.items.slice(0, state.maxItems);
          }
          
          state.pagination.total = state.items.length;
          state.pagination.totalPages = Math.ceil(state.items.length / state.pagination.limit);
        });
      },

      updateItem: (id, updates) => {
        set((state) => {
          const index = state.items.findIndex((item) => item.id === id);
          if (index !== -1) {
            state.items[index] = {
              ...state.items[index],
              ...updates,
            };
          }
        });
      },

      removeItem: (id) => {
        set((state) => {
          state.undoStack.push(createUndoSnapshot(state.items, 'removeItem'));
          if (state.undoStack.length > state.maxUndoSteps) {
            state.undoStack.shift();
          }
          state.redoStack = [];
          
          state.items = state.items.filter((item) => item.id !== id);
          state.selectedIds = state.selectedIds.filter((sid) => sid !== id);
          
          state.pagination.total = state.items.length;
          state.pagination.totalPages = Math.ceil(state.items.length / state.pagination.limit);
        });
      },

      clearItems: () => {
        set((state) => {
          state.undoStack.push(createUndoSnapshot(state.items, 'clearItems'));
          state.redoStack = [];
          
          state.items = [];
          state.selectedIds = [];
          state.pagination.total = 0;
          state.pagination.totalPages = 0;
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // BULK ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      removeMultiple: (ids) => {
        set((state) => {
          state.undoStack.push(createUndoSnapshot(state.items, 'removeMultiple'));
          state.redoStack = [];
          
          state.items = state.items.filter((item) => !ids.includes(item.id));
          state.selectedIds = state.selectedIds.filter((id) => !ids.includes(id));
          
          state.pagination.total = state.items.length;
          state.pagination.totalPages = Math.ceil(state.items.length / state.pagination.limit);
        });
      },

      updateMultiple: (ids, updates) => {
        set((state) => {
          ids.forEach((id) => {
            const index = state.items.findIndex((item) => item.id === id);
            if (index !== -1) {
              state.items[index] = {
                ...state.items[index],
                ...updates,
              };
            }
          });
        });
      },

      clearByStatus: (status) => {
        set((state) => {
          state.undoStack.push(createUndoSnapshot(state.items, 'clearByStatus'));
          state.redoStack = [];
          
          state.items = state.items.filter((item) => item.status !== status);
          state.pagination.total = state.items.length;
        });
      },

      clearByFileType: (fileType) => {
        set((state) => {
          state.undoStack.push(createUndoSnapshot(state.items, 'clearByFileType'));
          state.redoStack = [];
          
          state.items = state.items.filter((item) => item.fileType !== fileType);
          state.pagination.total = state.items.length;
        });
      },

      clearOlderThan: (days) => {
        const cutoff = new Date();
        cutoff.setDate(cutoff.getDate() - days);

        set((state) => {
          state.undoStack.push(createUndoSnapshot(state.items, 'clearOlderThan'));
          state.redoStack = [];
          
          state.items = state.items.filter(
            (item) => new Date(item.downloadedAt) >= cutoff
          );
          state.pagination.total = state.items.length;
        });
      },

      clearByDateRange: (start, end) => {
        set((state) => {
          state.undoStack.push(createUndoSnapshot(state.items, 'clearByDateRange'));
          state.redoStack = [];
          
          state.items = state.items.filter((item) => {
            const date = new Date(item.downloadedAt);
            return date < start || date > end;
          });
          state.pagination.total = state.items.length;
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // TAG ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      addTag: (id, tag) => {
        set((state) => {
          const item = state.items.find((i) => i.id === id);
          if (item && !item.tags.includes(tag)) {
            item.tags.push(tag);
          }
        });
      },

      removeTag: (id, tag) => {
        set((state) => {
          const item = state.items.find((i) => i.id === id);
          if (item) {
            item.tags = item.tags.filter((t) => t !== tag);
          }
        });
      },

      addTagToMultiple: (ids, tag) => {
        set((state) => {
          ids.forEach((id) => {
            const item = state.items.find((i) => i.id === id);
            if (item && !item.tags.includes(tag)) {
              item.tags.push(tag);
            }
          });
        });
      },

      removeTagFromMultiple: (ids, tag) => {
        set((state) => {
          ids.forEach((id) => {
            const item = state.items.find((i) => i.id === id);
            if (item) {
              item.tags = item.tags.filter((t) => t !== tag);
            }
          });
        });
      },

      getAvailableTags: () => {
        const state = get();
        const tagCounts: Record<string, number> = {};
        
        state.items.forEach((item) => {
          item.tags.forEach((tag) => {
            tagCounts[tag] = (tagCounts[tag] || 0) + 1;
          });
        });
        
        return Object.entries(tagCounts)
          .map(([tag, count]) => ({ tag, count }))
          .sort((a, b) => b.count - a.count);
      },

      // ═════════════════════════════════════════════════════════════════════════
      // CATEGORY ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      setCategory: (id, category) => {
        set((state) => {
          const item = state.items.find((i) => i.id === id);
          if (item) {
            item.category = category;
          }
        });
      },

      setCategoryToMultiple: (ids, category) => {
        set((state) => {
          ids.forEach((id) => {
            const item = state.items.find((i) => i.id === id);
            if (item) {
              item.category = category;
            }
          });
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // FAVORITE/ARCHIVE ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      toggleFavorite: (id) => {
        set((state) => {
          const item = state.items.find((i) => i.id === id);
          if (item) {
            item.favorite = !item.favorite;
          }
        });
      },

      toggleArchive: (id) => {
        set((state) => {
          const item = state.items.find((i) => i.id === id);
          if (item) {
            item.archived = !item.archived;
          }
        });
      },

      setRating: (id, rating) => {
        set((state) => {
          const item = state.items.find((i) => i.id === id);
          if (item) {
            item.rating = rating;
          }
        });
      },

      setNotes: (id, notes) => {
        set((state) => {
          const item = state.items.find((i) => i.id === id);
          if (item) {
            item.notes = notes;
          }
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // SELECTION ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      selectItem: (id) => {
        set((state) => {
          if (!state.selectedIds.includes(id)) {
            state.selectedIds.push(id);
          }
        });
      },

      deselectItem: (id) => {
        set((state) => {
          state.selectedIds = state.selectedIds.filter((sid) => sid !== id);
        });
      },

      toggleSelectItem: (id) => {
        set((state) => {
          if (state.selectedIds.includes(id)) {
            state.selectedIds = state.selectedIds.filter((sid) => sid !== id);
          } else {
            state.selectedIds.push(id);
          }
        });
      },

      selectAll: () => {
        set((state) => {
          state.selectedIds = state.items.map((item) => item.id);
        });
      },

      deselectAll: () => {
        set((state) => {
          state.selectedIds = [];
        });
      },

      selectByFilter: (filter) => {
        set((state) => {
          state.selectedIds = state.items
            .filter((item) => matchesFilter(item, filter))
            .map((item) => item.id);
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // FILTER/SORT ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      setFilter: (filter) => {
        set((state) => {
          state.filter = { ...state.filter, ...filter };
          state.pagination.page = 1;
        });
      },

      clearFilter: () => {
        set((state) => {
          state.filter = {};
          state.pagination.page = 1;
        });
      },

      setSort: (sort) => {
        set((state) => {
          state.sort = sort;
        });
      },

      setPagination: (pagination) => {
        set((state) => {
          state.pagination = { ...state.pagination, ...pagination };
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // COMPUTED SELECTORS
      // ═════════════════════════════════════════════════════════════════════════

      getFilteredItems: () => {
        const state = get();
        let items = state.items.filter((item) => matchesFilter(item, state.filter));
        
        // Sort
        items.sort((a, b) => {
          let aVal: number | string = 0;
          let bVal: number | string = 0;
          
          switch (state.sort.field) {
            case 'downloadedAt':
              aVal = new Date(a.downloadedAt).getTime();
              bVal = new Date(b.downloadedAt).getTime();
              break;
            case 'fileSize':
              aVal = a.fileSize;
              bVal = b.fileSize;
              break;
            case 'title':
              aVal = a.title || a.filename;
              bVal = b.title || b.filename;
              break;
            case 'duration':
              aVal = a.duration || 0;
              bVal = b.duration || 0;
              break;
            case 'rating':
              aVal = a.rating || 0;
              bVal = b.rating || 0;
              break;
          }
          
          if (typeof aVal === 'string') {
            return state.sort.direction === 'asc' 
              ? aVal.localeCompare(bVal as string)
              : (bVal as string).localeCompare(aVal);
          }
          
          return state.sort.direction === 'asc' ? aVal - (bVal as number) : (bVal as number) - aVal;
        });
        
        return items;
      },

      getPaginatedItems: () => {
        const state = get();
        const filtered = get().getFilteredItems();
        const start = (state.pagination.page - 1) * state.pagination.limit;
        return filtered.slice(start, start + state.pagination.limit);
      },

      getById: (id) => {
        return get().items.find((item) => item.id === id);
      },

      getByUrl: (url) => {
        return get().items.filter((item) => item.url === url);
      },

      getByStatus: (status) => {
        return get().items.filter((item) => item.status === status);
      },

      getByFileType: (fileType) => {
        return get().items.filter((item) => item.fileType === fileType);
      },

      getByTag: (tag) => {
        return get().items.filter((item) => item.tags.includes(tag));
      },

      getByCategory: (category) => {
        return get().items.filter((item) => item.category === category);
      },

      search: (query) => {
        const queryLower = query.toLowerCase();
        return get().items.filter(
          (item) =>
            item.title?.toLowerCase().includes(queryLower) ||
            item.filename.toLowerCase().includes(queryLower) ||
            item.url.toLowerCase().includes(queryLower) ||
            item.tags.some((tag) => tag.toLowerCase().includes(queryLower))
        );
      },

      getFavorites: () => {
        return get().items.filter((item) => item.favorite);
      },

      getArchived: () => {
        return get().items.filter((item) => item.archived);
      },

      getStats: () => {
        const items = get().items;
        const byFileType = {} as Record<FileType, number>;
        const byStatus = {} as Record<DownloadStatus, number>;
        let totalSize = 0;
        let successCount = 0;
        let failedCount = 0;
        let totalSpeed = 0;
        let speedCount = 0;
        const domainCounts: Record<string, number> = {};
        const dayStats: Record<string, { count: number; size: number }> = {};
        
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
        const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
        
        let todayCount = 0;
        let weekCount = 0;
        let monthCount = 0;

        items.forEach((item) => {
          byFileType[item.fileType] = (byFileType[item.fileType] || 0) + 1;
          byStatus[item.status] = (byStatus[item.status] || 0) + 1;
          totalSize += item.fileSize;

          if (item.status === DownloadStatus.COMPLETED) {
            successCount++;
          } else if (item.status === DownloadStatus.FAILED) {
            failedCount++;
          }
          
          if (item.downloadSpeed) {
            totalSpeed += item.downloadSpeed;
            speedCount++;
          }
          
          // Domain stats
          const domain = extractDomain(item.url);
          domainCounts[domain] = (domainCounts[domain] || 0) + 1;
          
          // Day stats
          const dateKey = new Date(item.downloadedAt).toISOString().split('T')[0];
          if (!dayStats[dateKey]) {
            dayStats[dateKey] = { count: 0, size: 0 };
          }
          dayStats[dateKey].count++;
          dayStats[dateKey].size += item.fileSize;
          
          // Recent activity
          const itemDate = new Date(item.downloadedAt);
          if (itemDate >= today) todayCount++;
          if (itemDate >= weekAgo) weekCount++;
          if (itemDate >= monthAgo) monthCount++;
        });

        const topDomains = Object.entries(domainCounts)
          .map(([domain, count]) => ({ domain, count }))
          .sort((a, b) => b.count - a.count)
          .slice(0, 10);

        const byDay = Object.entries(dayStats)
          .map(([date, stats]) => ({ date, count: stats.count, size: stats.size }))
          .sort((a, b) => a.date.localeCompare(b.date))
          .slice(-30);

        return {
          totalItems: items.length,
          totalSize,
          successCount,
          failedCount,
          averageSize: items.length > 0 ? totalSize / items.length : 0,
          averageSpeed: speedCount > 0 ? totalSpeed / speedCount : 0,
          byFileType,
          byStatus,
          byDay,
          topDomains,
          recentActivity: {
            today: todayCount,
            thisWeek: weekCount,
            thisMonth: monthCount,
          },
        };
      },

      getRecentItems: (limit = 10) => {
        return get().items.slice(0, limit);
      },

      getDuplicateUrls: () => {
        const items = get().items;
        const urlMap: Record<string, HistoryItem[]> = {};
        
        items.forEach((item) => {
          if (!urlMap[item.url]) {
            urlMap[item.url] = [];
          }
          urlMap[item.url].push(item);
        });
        
        return Object.entries(urlMap)
          .filter(([, items]) => items.length > 1)
          .map(([url, items]) => ({ url, items }));
      },

      // ═════════════════════════════════════════════════════════════════════════
      // EXPORT/IMPORT
      // ═════════════════════════════════════════════════════════════════════════

      exportHistory: (options) => {
        const state = get();
        let items = state.items;
        
        // Apply filter if provided
        if (options.filter) {
          items = items.filter((item) => matchesFilter(item, options.filter));
        }
        
        // Apply date range if provided
        if (options.dateRange) {
          items = items.filter((item) => {
            const date = new Date(item.downloadedAt);
            return date >= options.dateRange!.start && date <= options.dateRange!.end;
          });
        }
        
        switch (options.format) {
          case 'json':
            return JSON.stringify({
              version: '3.2.0',
              exportedAt: new Date().toISOString(),
              items: options.includeMetadata ? items : items.map(({ metadata, ...rest }) => rest),
            }, null, 2);
          
          case 'csv':
            const headers = ['ID', 'URL', 'Title', 'Filename', 'FileSize', 'Status', 'DownloadedAt', 'Tags'];
            const rows = items.map((item) => [
              item.id,
              item.url,
              item.title || '',
              item.filename,
              item.fileSize.toString(),
              item.status,
              new Date(item.downloadedAt).toISOString(),
              item.tags.join(';'),
            ]);
            return [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
          
          case 'txt':
            return items.map((item) => 
              `[${new Date(item.downloadedAt).toISOString()}] ${item.title || item.filename} - ${item.url}`
            ).join('\n');
          
          default:
            return '';
        }
      },

      importHistory: (data, format) => {
        try {
          let importedItems: HistoryItem[] = [];
          
          if (format === 'json') {
            const parsed = JSON.parse(data);
            importedItems = (parsed.items || []).map((item: HistoryItem) => ({
              ...item,
              id: item.id || generateId(),
              downloadedAt: new Date(item.downloadedAt),
            }));
          } else if (format === 'csv') {
            const lines = data.split('\n').slice(1);
            importedItems = lines
              .filter((line) => line.trim())
              .map((line) => {
                const [id, url, title, filename, fileSize, status, downloadedAt, tags] = line.split(',');
                return {
                  id: id || generateId(),
                  url,
                  title,
                  filename,
                  filePath: '',
                  fileSize: parseInt(fileSize, 10) || 0,
                  fileType: FileType.UNKNOWN,
                  status: status as DownloadStatus,
                  downloadedAt: new Date(downloadedAt),
                  tags: tags ? tags.split(';') : [],
                  favorite: false,
                  archived: false,
                } as HistoryItem;
              });
          }
          
          set((state) => {
            state.undoStack.push(createUndoSnapshot(state.items, 'importHistory'));
            state.redoStack = [];
            
            // Merge with existing items
            const existingIds = new Set(state.items.map((i) => i.id));
            const newItems = importedItems.filter((i) => !existingIds.has(i.id));
            
            state.items = [...newItems, ...state.items].slice(0, state.maxItems);
            state.pagination.total = state.items.length;
          });
          
          return importedItems.length;
        } catch {
          return 0;
        }
      },

      // ═════════════════════════════════════════════════════════════════════════
      // UNDO/REDO
      // ═════════════════════════════════════════════════════════════════════════

      undo: () => {
        const state = get();
        if (state.undoStack.length === 0) return false;

        const previousState = state.undoStack[state.undoStack.length - 1];
        
        set((s) => {
          s.redoStack.push(createUndoSnapshot(s.items, 'redo'));
          s.items = previousState.items;
          s.undoStack.pop();
          s.pagination.total = s.items.length;
        });

        return true;
      },

      redo: () => {
        const state = get();
        if (state.redoStack.length === 0) return false;

        const nextState = state.redoStack[state.redoStack.length - 1];
        
        set((s) => {
          s.undoStack.push(createUndoSnapshot(s.items, 'undo'));
          s.items = nextState.items;
          s.redoStack.pop();
          s.pagination.total = s.items.length;
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
    })),
    {
      name: 'rs-toolkit-history',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        items: state.items.slice(0, 500), // Limit persisted items
        maxItems: state.maxItems,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.isHydrated = true;
          state.lastSaved = new Date();
          state.pagination.total = state.items.length;
          state.pagination.totalPages = Math.ceil(state.items.length / state.pagination.limit);
        }
      },
    }
  )
);

// ═══════════════════════════════════════════════════════════════════════════════
// SELECTORS
// ═══════════════════════════════════════════════════════════════════════════════

export const selectHistoryItems = (state: HistoryStore) => state.items;
export const selectHistoryFilter = (state: HistoryStore) => state.filter;
export const selectHistorySort = (state: HistoryStore) => state.sort;
export const selectHistoryPagination = (state: HistoryStore) => state.pagination;
export const selectSelectedIds = (state: HistoryStore) => state.selectedIds;
export const selectHistoryStats = (state: HistoryStore) => state.getStats();

export default useHistoryStore;
