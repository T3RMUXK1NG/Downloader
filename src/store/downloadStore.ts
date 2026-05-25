/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    DOWNLOAD STORE v3.0.1 ULTIMATE NEXUS                       ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Download state management with Zustand                         ║
 * ║  Features: Downloads, progress, queue, concurrency control                  ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module store/downloadStore
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import {
  DownloadResponse,
  DownloadStatus,
  WSDownloadProgress,
} from '@/types/api';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface DownloadQueueItem {
  id: string;
  url: string;
  priority: number;
  addedAt: Date;
  startedAt?: Date;
}

export interface DownloadStore {
  // State
  downloads: Map<string, DownloadResponse>;
  progress: Map<string, WSDownloadProgress>;
  queue: DownloadQueueItem[];
  maxConcurrent: number;
  activeCount: number;

  // Actions
  addDownload: (download: DownloadResponse) => void;
  updateDownload: (id: string, updates: Partial<DownloadResponse>) => void;
  removeDownload: (id: string) => void;
  updateProgress: (id: string, progress: WSDownloadProgress) => void;
  clearProgress: (id: string) => void;
  clearDownloads: () => void;

  // Queue Actions
  addToQueue: (item: Omit<DownloadQueueItem, 'addedAt'>) => void;
  removeFromQueue: (id: string) => void;
  reorderQueue: (id: string, newIndex: number) => void;
  clearQueue: () => void;
  getNextInQueue: () => DownloadQueueItem | undefined;
  startNextInQueue: () => void;

  // Settings
  setMaxConcurrent: (max: number) => void;

  // Computed
  getActiveDownloads: () => DownloadResponse[];
  getCompletedDownloads: () => DownloadResponse[];
  getFailedDownloads: () => DownloadResponse[];
  getByStatus: (status: DownloadStatus) => DownloadResponse[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// STORE IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

export const useDownloadStore = create<DownloadStore>()(
  immer((set, get) => ({
    // ═════════════════════════════════════════════════════════════════════════
    // INITIAL STATE
    // ═════════════════════════════════════════════════════════════════════════
    downloads: new Map(),
    progress: new Map(),
    queue: [],
    maxConcurrent: 3,
    activeCount: 0,

    // ═════════════════════════════════════════════════════════════════════════
    // DOWNLOAD ACTIONS
    // ═════════════════════════════════════════════════════════════════════════

    addDownload: (download) => {
      set((state) => {
        state.downloads.set(download.downloadId, download);
        
        // Update active count
        if (
          download.status === DownloadStatus.DOWNLOADING ||
          download.status === DownloadStatus.PENDING
        ) {
          state.activeCount++;
        }
      });
    },

    updateDownload: (id, updates) => {
      set((state) => {
        const download = state.downloads.get(id);
        if (download) {
          const previousStatus = download.status;
          state.downloads.set(id, { ...download, ...updates });

          // Update active count if status changed
          const newStatus = updates.status;
          if (newStatus) {
            const wasActive =
              previousStatus === DownloadStatus.DOWNLOADING ||
              previousStatus === DownloadStatus.PENDING;
            const isActive =
              newStatus === DownloadStatus.DOWNLOADING ||
              newStatus === DownloadStatus.PENDING;

            if (wasActive && !isActive) {
              state.activeCount = Math.max(0, state.activeCount - 1);
            } else if (!wasActive && isActive) {
              state.activeCount++;
            }
          }
        }
      });
    },

    removeDownload: (id) => {
      set((state) => {
        const download = state.downloads.get(id);
        if (download) {
          // Update active count if necessary
          if (
            download.status === DownloadStatus.DOWNLOADING ||
            download.status === DownloadStatus.PENDING
          ) {
            state.activeCount = Math.max(0, state.activeCount - 1);
          }
        }
        state.downloads.delete(id);
        state.progress.delete(id);
      });
    },

    updateProgress: (id, progress) => {
      set((state) => {
        state.progress.set(id, progress);
      });
    },

    clearProgress: (id) => {
      set((state) => {
        state.progress.delete(id);
      });
    },

    clearDownloads: () => {
      set((state) => {
        state.downloads.clear();
        state.progress.clear();
        state.activeCount = 0;
      });
    },

    // ═════════════════════════════════════════════════════════════════════════
    // QUEUE ACTIONS
    // ═════════════════════════════════════════════════════════════════════════

    addToQueue: (item) => {
      set((state) => {
        state.queue.push({
          ...item,
          addedAt: new Date(),
        });
        // Sort by priority (higher first)
        state.queue.sort((a, b) => b.priority - a.priority);
      });
    },

    removeFromQueue: (id) => {
      set((state) => {
        state.queue = state.queue.filter((item) => item.id !== id);
      });
    },

    reorderQueue: (id, newIndex) => {
      set((state) => {
        const currentIndex = state.queue.findIndex((item) => item.id === id);
        if (currentIndex !== -1) {
          const [item] = state.queue.splice(currentIndex, 1);
          state.queue.splice(newIndex, 0, item);
        }
      });
    },

    clearQueue: () => {
      set((state) => {
        state.queue = [];
      });
    },

    getNextInQueue: () => {
      const state = get();
      if (state.queue.length === 0) return undefined;
      return state.queue[0];
    },

    startNextInQueue: () => {
      const state = get();
      if (state.activeCount >= state.maxConcurrent) return;
      if (state.queue.length === 0) return;

      const nextItem = state.queue[0];
      set((s) => {
        s.queue.shift();
      });

      return nextItem;
    },

    // ═════════════════════════════════════════════════════════════════════════
    // SETTINGS
    // ═════════════════════════════════════════════════════════════════════════

    setMaxConcurrent: (max) => {
      set((state) => {
        state.maxConcurrent = max;
      });
    },

    // ═════════════════════════════════════════════════════════════════════════
    // COMPUTED
    // ═════════════════════════════════════════════════════════════════════════

    getActiveDownloads: () => {
      const state = get();
      return Array.from(state.downloads.values()).filter(
        (d) =>
          d.status === DownloadStatus.DOWNLOADING ||
          d.status === DownloadStatus.PENDING
      );
    },

    getCompletedDownloads: () => {
      const state = get();
      return Array.from(state.downloads.values()).filter(
        (d) => d.status === DownloadStatus.COMPLETED
      );
    },

    getFailedDownloads: () => {
      const state = get();
      return Array.from(state.downloads.values()).filter(
        (d) => d.status === DownloadStatus.FAILED
      );
    },

    getByStatus: (status) => {
      const state = get();
      return Array.from(state.downloads.values()).filter(
        (d) => d.status === status
      );
    },
  }))
);

export default useDownloadStore;
