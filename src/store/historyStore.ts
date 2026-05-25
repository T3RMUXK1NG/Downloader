/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    HISTORY STORE v3.0.1 ULTIMATE NEXUS                        ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: History state management with Zustand                          ║
 * ║  Features: CRUD, filtering, sorting, statistics, cleanup                    ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module store/historyStore
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
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

export interface HistoryStore {
  // State
  items: HistoryItem[];
  maxItems: number;

  // Actions
  setItems: (items: HistoryItem[]) => void;
  addItem: (item: HistoryItem) => void;
  updateItem: (id: string, updates: Partial<HistoryItem>) => void;
  removeItem: (id: string) => void;
  clearItems: () => void;

  // Bulk Actions
  removeMultiple: (ids: string[]) => void;
  clearByStatus: (status: DownloadStatus) => void;
  clearOlderThan: (days: number) => void;

  // Tag Actions
  addTag: (id: string, tag: string) => void;
  removeTag: (id: string, tag: string) => void;

  // Computed
  getById: (id: string) => HistoryItem | undefined;
  getByUrl: (url: string) => HistoryItem[];
  getByStatus: (status: DownloadStatus) => HistoryItem[];
  getByFileType: (fileType: FileType) => HistoryItem[];
  search: (query: string) => HistoryItem[];
  getStats: () => HistoryStats;
}

export interface HistoryStats {
  totalItems: number;
  totalSize: number;
  successCount: number;
  failedCount: number;
  averageSize: number;
  byFileType: Record<FileType, number>;
  byStatus: Record<DownloadStatus, number>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// STORE IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

export const useHistoryStore = create<HistoryStore>()(
  immer((set, get) => ({
    // ═════════════════════════════════════════════════════════════════════════
    // INITIAL STATE
    // ═════════════════════════════════════════════════════════════════════════
    items: [],
    maxItems: 1000,

    // ═════════════════════════════════════════════════════════════════════════
    // ACTIONS
    // ═════════════════════════════════════════════════════════════════════════

    setItems: (items) => {
      set((state) => {
        state.items = items;
      });
    },

    addItem: (item) => {
      set((state) => {
        // Add to beginning
        state.items.unshift(item);

        // Enforce max items
        if (state.items.length > state.maxItems) {
          state.items = state.items.slice(0, state.maxItems);
        }
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
        state.items = state.items.filter((item) => item.id !== id);
      });
    },

    clearItems: () => {
      set((state) => {
        state.items = [];
      });
    },

    // ═════════════════════════════════════════════════════════════════════════
    // BULK ACTIONS
    // ═════════════════════════════════════════════════════════════════════════

    removeMultiple: (ids) => {
      set((state) => {
        state.items = state.items.filter((item) => !ids.includes(item.id));
      });
    },

    clearByStatus: (status) => {
      set((state) => {
        state.items = state.items.filter((item) => item.status !== status);
      });
    },

    clearOlderThan: (days) => {
      const cutoff = new Date();
      cutoff.setDate(cutoff.getDate() - days);

      set((state) => {
        state.items = state.items.filter(
          (item) => new Date(item.downloadedAt) >= cutoff
        );
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

    // ═════════════════════════════════════════════════════════════════════════
    // COMPUTED
    // ═════════════════════════════════════════════════════════════════════════

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

    getStats: () => {
      const items = get().items;
      const byFileType = {} as Record<FileType, number>;
      const byStatus = {} as Record<DownloadStatus, number>;
      let totalSize = 0;
      let successCount = 0;
      let failedCount = 0;

      items.forEach((item) => {
        byFileType[item.fileType] = (byFileType[item.fileType] || 0) + 1;
        byStatus[item.status] = (byStatus[item.status] || 0) + 1;
        totalSize += item.fileSize;

        if (item.status === DownloadStatus.COMPLETED) {
          successCount++;
        } else if (item.status === DownloadStatus.FAILED) {
          failedCount++;
        }
      });

      return {
        totalItems: items.length,
        totalSize,
        successCount,
        failedCount,
        averageSize: items.length > 0 ? totalSize / items.length : 0,
        byFileType,
        byStatus,
      };
    },
  }))
);

export default useHistoryStore;
