/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    DOWNLOAD STORE v3.2.0 ULTIMATE NEXUS                       ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Enhanced download state management with Zustand                 ║
 * ║  Features: Downloads, progress, queue, categories, rules, persistence        ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module store/downloadStore
 * @version 3.2.0
 * @author RAJSARASWATI JATAV (RS)
 */

import { create, StoreApi, UseBoundStore } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { persist, createJSONStorage } from 'zustand/middleware';
import {
  DownloadResponse,
  DownloadStatus,
  WSDownloadProgress,
  VideoQuality,
  AudioQuality,
  VideoFormat,
  AudioFormat,
} from '@/types/api';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Download category for organization
 */
export interface DownloadCategory {
  id: string;
  name: string;
  color: string;
  icon?: string;
  description?: string;
  createdAt: Date;
  downloadCount: number;
}

/**
 * Tag for download organization
 */
export interface DownloadTag {
  id: string;
  name: string;
  color: string;
  usageCount: number;
}

/**
 * Custom download rule
 */
export interface DownloadRule {
  id: string;
  name: string;
  description?: string;
  enabled: boolean;
  priority: number;
  conditions: DownloadRuleCondition[];
  actions: DownloadRuleAction[];
  createdAt: Date;
  lastTriggered?: Date;
  triggerCount: number;
}

/**
 * Rule condition
 */
export interface DownloadRuleCondition {
  field: 'url' | 'title' | 'duration' | 'fileSize' | 'quality' | 'platform';
  operator: 'equals' | 'contains' | 'startsWith' | 'endsWith' | 'regex' | 'gt' | 'lt' | 'gte' | 'lte';
  value: string | number;
}

/**
 * Rule action
 */
export interface DownloadRuleAction {
  type: 'setCategory' | 'setOutputDir' | 'setQuality' | 'addTag' | 'setPriority' | 'autoStart' | 'skipDownload';
  value: string | number | boolean;
}

/**
 * Queue item with extended properties
 */
export interface DownloadQueueItem {
  id: string;
  url: string;
  priority: number;
  addedAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  category?: string;
  tags: string[];
  ruleId?: string;
  autoStart: boolean;
  retryCount: number;
  maxRetries: number;
  error?: string;
}

/**
 * Download schedule
 */
export interface DownloadSchedule {
  id: string;
  queueItemId: string;
  scheduledFor: Date;
  recurrence?: 'once' | 'daily' | 'weekly' | 'monthly';
  enabled: boolean;
}

/**
 * Speed limit rule
 */
export interface SpeedLimitRule {
  id: string;
  name: string;
  maxSpeed: number; // bytes per second
  timeRange?: {
    start: string; // HH:MM format
    end: string;
  };
  days?: number[]; // 0-6, Sunday = 0
  enabled: boolean;
}

/**
 * Undo/redo state
 */
interface UndoState {
  downloads: Array<[string, DownloadResponse | undefined]>;
  queue: DownloadQueueItem[];
  timestamp: number;
  action: string;
}

/**
 * Store state interface
 */
export interface DownloadStoreState {
  // Core state
  downloads: Record<string, DownloadResponse>;
  progress: Record<string, WSDownloadProgress>;
  queue: DownloadQueueItem[];
  maxConcurrent: number;
  activeCount: number;
  
  // Categories and tags
  categories: DownloadCategory[];
  tags: DownloadTag[];
  
  // Rules
  rules: DownloadRule[];
  speedLimitRules: SpeedLimitRule[];
  
  // Schedules
  schedules: DownloadSchedule[];
  
  // Statistics
  totalDownloaded: number;
  totalBytes: number;
  sessionStats: {
    started: number;
    completed: number;
    failed: number;
    bytesDownloaded: number;
  };
  
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
export interface DownloadStoreActions {
  // Download actions
  addDownload: (download: DownloadResponse) => void;
  updateDownload: (id: string, updates: Partial<DownloadResponse>) => void;
  removeDownload: (id: string) => void;
  updateProgress: (id: string, progress: WSDownloadProgress) => void;
  clearProgress: (id: string) => void;
  clearDownloads: () => void;
  clearCompletedDownloads: () => void;
  clearFailedDownloads: () => void;
  
  // Queue actions
  addToQueue: (item: Omit<DownloadQueueItem, 'addedAt' | 'id'>) => string;
  removeFromQueue: (id: string) => void;
  reorderQueue: (id: string, newIndex: number) => void;
  clearQueue: () => void;
  getNextInQueue: () => DownloadQueueItem | undefined;
  startNextInQueue: () => DownloadQueueItem | undefined;
  pauseQueueItem: (id: string) => void;
  resumeQueueItem: (id: string) => void;
  retryQueueItem: (id: string) => void;
  moveQueueItemToTop: (id: string) => void;
  moveQueueItemToBottom: (id: string) => void;
  
  // Category actions
  addCategory: (category: Omit<DownloadCategory, 'id' | 'createdAt' | 'downloadCount'>) => string;
  updateCategory: (id: string, updates: Partial<DownloadCategory>) => void;
  removeCategory: (id: string) => void;
  setDownloadCategory: (downloadId: string, categoryId: string) => void;
  
  // Tag actions
  addTag: (tag: Omit<DownloadTag, 'id' | 'usageCount'>) => string;
  removeTag: (id: string) => void;
  tagDownload: (downloadId: string, tagId: string) => void;
  untagDownload: (downloadId: string, tagId: string) => void;
  
  // Rule actions
  addRule: (rule: Omit<DownloadRule, 'id' | 'createdAt' | 'lastTriggered' | 'triggerCount'>) => string;
  updateRule: (id: string, updates: Partial<DownloadRule>) => void;
  removeRule: (id: string) => void;
  toggleRule: (id: string) => void;
  applyRulesToUrl: (url: string) => Partial<DownloadQueueItem>;
  
  // Speed limit actions
  addSpeedLimitRule: (rule: Omit<SpeedLimitRule, 'id'>) => string;
  updateSpeedLimitRule: (id: string, updates: Partial<SpeedLimitRule>) => void;
  removeSpeedLimitRule: (id: string) => void;
  getCurrentSpeedLimit: () => number;
  
  // Schedule actions
  addSchedule: (schedule: Omit<DownloadSchedule, 'id'>) => string;
  removeSchedule: (id: string) => void;
  toggleSchedule: (id: string) => void;
  getPendingSchedules: () => DownloadSchedule[];
  
  // Settings
  setMaxConcurrent: (max: number) => void;
  
  // Statistics
  updateStats: (completed: boolean, success: boolean, bytes: number) => void;
  resetSessionStats: () => void;
  
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
  
  // Computed selectors (as functions for Zustand)
  getActiveDownloads: () => DownloadResponse[];
  getCompletedDownloads: () => DownloadResponse[];
  getFailedDownloads: () => DownloadResponse[];
  getByStatus: (status: DownloadStatus) => DownloadResponse[];
  getByCategory: (categoryId: string) => DownloadResponse[];
  getByTag: (tagId: string) => DownloadResponse[];
  searchDownloads: (query: string) => DownloadResponse[];
  getDownloadStats: () => DownloadStats;
  getQueueStats: () => QueueStats;
}

/**
 * Combined store type
 */
export type DownloadStore = DownloadStoreState & DownloadStoreActions;

/**
 * Download statistics
 */
export interface DownloadStats {
  total: number;
  active: number;
  completed: number;
  failed: number;
  pending: number;
  totalBytes: number;
  averageSpeed: number;
  averageDuration: number;
}

/**
 * Queue statistics
 */
export interface QueueStats {
  total: number;
  pending: number;
  downloading: number;
  paused: number;
  failed: number;
  averageWaitTime: number;
  estimatedTimeRemaining: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// DEFAULT VALUES
// ═══════════════════════════════════════════════════════════════════════════════

const DEFAULT_CATEGORIES: DownloadCategory[] = [
  { id: 'cat_videos', name: 'Videos', color: '#ef4444', icon: 'video', createdAt: new Date(), downloadCount: 0 },
  { id: 'cat_audio', name: 'Audio', color: '#3b82f6', icon: 'music', createdAt: new Date(), downloadCount: 0 },
  { id: 'cat_playlists', name: 'Playlists', color: '#8b5cf6', icon: 'list', createdAt: new Date(), downloadCount: 0 },
  { id: 'cat_other', name: 'Other', color: '#6b7280', icon: 'file', createdAt: new Date(), downloadCount: 0 },
];

// ═══════════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Generate unique ID
 */
const generateId = (): string => `dl_${Date.now()}_${Math.random().toString(36).substring(2, 10)}`;

/**
 * Create undo snapshot
 */
const createUndoSnapshot = (state: DownloadStoreState, action: string): UndoState => ({
  downloads: Object.entries(state.downloads).slice(0, 100), // Limit size
  queue: state.queue.slice(0, 100),
  timestamp: Date.now(),
  action,
});

// ═══════════════════════════════════════════════════════════════════════════════
// STORE IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

export const useDownloadStore = create<DownloadStore>()(
  persist(
    immer((set, get) => ({
      // ═════════════════════════════════════════════════════════════════════════
      // INITIAL STATE
      // ═════════════════════════════════════════════════════════════════════════
      downloads: {},
      progress: {},
      queue: [],
      maxConcurrent: 3,
      activeCount: 0,
      
      categories: DEFAULT_CATEGORIES,
      tags: [],
      rules: [],
      speedLimitRules: [],
      schedules: [],
      
      totalDownloaded: 0,
      totalBytes: 0,
      sessionStats: {
        started: 0,
        completed: 0,
        failed: 0,
        bytesDownloaded: 0,
      },
      
      undoStack: [],
      redoStack: [],
      maxUndoSteps: 50,
      lastSaved: null,
      isHydrated: false,

      // ═════════════════════════════════════════════════════════════════════════
      // DOWNLOAD ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      addDownload: (download) => {
        set((state) => {
          // Save for undo
          state.undoStack.push(createUndoSnapshot(state, 'addDownload'));
          if (state.undoStack.length > state.maxUndoSteps) {
            state.undoStack.shift();
          }
          state.redoStack = [];
          
          state.downloads[download.downloadId] = download;
          
          if (
            download.status === DownloadStatus.DOWNLOADING ||
            download.status === DownloadStatus.PENDING
          ) {
            state.activeCount++;
            state.sessionStats.started++;
          }
        });
      },

      updateDownload: (id, updates) => {
        set((state) => {
          const download = state.downloads[id];
          if (download) {
            const previousStatus = download.status;
            state.downloads[id] = { ...download, ...updates };

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
                
                // Update session stats
                if (newStatus === DownloadStatus.COMPLETED) {
                  state.sessionStats.completed++;
                  state.totalDownloaded++;
                  if (download.fileSize) {
                    state.totalBytes += download.fileSize;
                    state.sessionStats.bytesDownloaded += download.fileSize;
                  }
                } else if (newStatus === DownloadStatus.FAILED) {
                  state.sessionStats.failed++;
                }
              } else if (!wasActive && isActive) {
                state.activeCount++;
              }
            }
          }
        });
      },

      removeDownload: (id) => {
        set((state) => {
          // Save for undo
          state.undoStack.push(createUndoSnapshot(state, 'removeDownload'));
          if (state.undoStack.length > state.maxUndoSteps) {
            state.undoStack.shift();
          }
          state.redoStack = [];
          
          const download = state.downloads[id];
          if (download) {
            if (
              download.status === DownloadStatus.DOWNLOADING ||
              download.status === DownloadStatus.PENDING
            ) {
              state.activeCount = Math.max(0, state.activeCount - 1);
            }
          }
          delete state.downloads[id];
          delete state.progress[id];
        });
      },

      updateProgress: (id, progress) => {
        set((state) => {
          state.progress[id] = progress;
        });
      },

      clearProgress: (id) => {
        set((state) => {
          delete state.progress[id];
        });
      },

      clearDownloads: () => {
        set((state) => {
          state.undoStack.push(createUndoSnapshot(state, 'clearDownloads'));
          state.redoStack = [];
          
          state.downloads = {};
          state.progress = {};
          state.activeCount = 0;
        });
      },

      clearCompletedDownloads: () => {
        set((state) => {
          state.undoStack.push(createUndoSnapshot(state, 'clearCompletedDownloads'));
          state.redoStack = [];
          
          Object.keys(state.downloads).forEach((id) => {
            if (state.downloads[id].status === DownloadStatus.COMPLETED) {
              delete state.downloads[id];
              delete state.progress[id];
            }
          });
        });
      },

      clearFailedDownloads: () => {
        set((state) => {
          state.undoStack.push(createUndoSnapshot(state, 'clearFailedDownloads'));
          state.redoStack = [];
          
          Object.keys(state.downloads).forEach((id) => {
            if (state.downloads[id].status === DownloadStatus.FAILED) {
              delete state.downloads[id];
              delete state.progress[id];
            }
          });
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // QUEUE ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      addToQueue: (item) => {
        const id = generateId();
        set((state) => {
          state.undoStack.push(createUndoSnapshot(state, 'addToQueue'));
          state.redoStack = [];
          
          const queueItem: DownloadQueueItem = {
            ...item,
            id,
            addedAt: new Date(),
            tags: item.tags || [],
            autoStart: item.autoStart ?? true,
            retryCount: 0,
            maxRetries: item.maxRetries ?? 3,
          };
          
          state.queue.push(queueItem);
          state.queue.sort((a, b) => b.priority - a.priority);
        });
        return id;
      },

      removeFromQueue: (id) => {
        set((state) => {
          state.undoStack.push(createUndoSnapshot(state, 'removeFromQueue'));
          state.redoStack = [];
          
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
          state.undoStack.push(createUndoSnapshot(state, 'clearQueue'));
          state.redoStack = [];
          
          state.queue = [];
        });
      },

      getNextInQueue: () => {
        const state = get();
        const pending = state.queue.filter(
          (item) => !item.startedAt && item.autoStart
        );
        return pending[0];
      },

      startNextInQueue: () => {
        const state = get();
        if (state.activeCount >= state.maxConcurrent) return undefined;
        
        const nextItem = state.queue.find(
          (item) => !item.startedAt && item.autoStart
        );
        
        if (!nextItem) return undefined;
        
        set((s) => {
          const item = s.queue.find((i) => i.id === nextItem.id);
          if (item) {
            item.startedAt = new Date();
          }
        });
        
        return nextItem;
      },

      pauseQueueItem: (id) => {
        set((state) => {
          const item = state.queue.find((i) => i.id === id);
          if (item) {
            item.autoStart = false;
          }
        });
      },

      resumeQueueItem: (id) => {
        set((state) => {
          const item = state.queue.find((i) => i.id === id);
          if (item) {
            item.autoStart = true;
            item.error = undefined;
          }
        });
      },

      retryQueueItem: (id) => {
        set((state) => {
          const item = state.queue.find((i) => i.id === id);
          if (item && item.retryCount < item.maxRetries) {
            item.retryCount++;
            item.startedAt = undefined;
            item.error = undefined;
            item.autoStart = true;
          }
        });
      },

      moveQueueItemToTop: (id) => {
        set((state) => {
          const index = state.queue.findIndex((i) => i.id === id);
          if (index > 0) {
            const [item] = state.queue.splice(index, 1);
            state.queue.unshift(item);
          }
        });
      },

      moveQueueItemToBottom: (id) => {
        set((state) => {
          const index = state.queue.findIndex((i) => i.id === id);
          if (index !== -1 && index < state.queue.length - 1) {
            const [item] = state.queue.splice(index, 1);
            state.queue.push(item);
          }
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // CATEGORY ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      addCategory: (category) => {
        const id = `cat_${Date.now()}`;
        set((state) => {
          state.categories.push({
            ...category,
            id,
            createdAt: new Date(),
            downloadCount: 0,
          });
        });
        return id;
      },

      updateCategory: (id, updates) => {
        set((state) => {
          const index = state.categories.findIndex((c) => c.id === id);
          if (index !== -1) {
            state.categories[index] = { ...state.categories[index], ...updates };
          }
        });
      },

      removeCategory: (id) => {
        set((state) => {
          state.categories = state.categories.filter((c) => c.id !== id);
        });
      },

      setDownloadCategory: (downloadId, categoryId) => {
        set((state) => {
          const queueItem = state.queue.find((i) => i.id === downloadId);
          if (queueItem) {
            queueItem.category = categoryId;
          }
          
          // Update category count
          const category = state.categories.find((c) => c.id === categoryId);
          if (category) {
            category.downloadCount++;
          }
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // TAG ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      addTag: (tag) => {
        const id = `tag_${Date.now()}`;
        set((state) => {
          state.tags.push({
            ...tag,
            id,
            usageCount: 0,
          });
        });
        return id;
      },

      removeTag: (id) => {
        set((state) => {
          state.tags = state.tags.filter((t) => t.id !== id);
          // Remove from all queue items
          state.queue.forEach((item) => {
            item.tags = item.tags.filter((t) => t !== id);
          });
        });
      },

      tagDownload: (downloadId, tagId) => {
        set((state) => {
          const item = state.queue.find((i) => i.id === downloadId);
          if (item && !item.tags.includes(tagId)) {
            item.tags.push(tagId);
          }
          
          const tag = state.tags.find((t) => t.id === tagId);
          if (tag) {
            tag.usageCount++;
          }
        });
      },

      untagDownload: (downloadId, tagId) => {
        set((state) => {
          const item = state.queue.find((i) => i.id === downloadId);
          if (item) {
            item.tags = item.tags.filter((t) => t !== tagId);
          }
          
          const tag = state.tags.find((t) => t.id === tagId);
          if (tag && tag.usageCount > 0) {
            tag.usageCount--;
          }
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // RULE ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      addRule: (rule) => {
        const id = `rule_${Date.now()}`;
        set((state) => {
          state.rules.push({
            ...rule,
            id,
            createdAt: new Date(),
            lastTriggered: undefined,
            triggerCount: 0,
          });
          state.rules.sort((a, b) => b.priority - a.priority);
        });
        return id;
      },

      updateRule: (id, updates) => {
        set((state) => {
          const index = state.rules.findIndex((r) => r.id === id);
          if (index !== -1) {
            state.rules[index] = { ...state.rules[index], ...updates };
          }
        });
      },

      removeRule: (id) => {
        set((state) => {
          state.rules = state.rules.filter((r) => r.id !== id);
        });
      },

      toggleRule: (id) => {
        set((state) => {
          const rule = state.rules.find((r) => r.id === id);
          if (rule) {
            rule.enabled = !rule.enabled;
          }
        });
      },

      applyRulesToUrl: (url) => {
        const state = get();
        const result: Partial<DownloadQueueItem> = {
          tags: [],
          autoStart: true,
        };

        for (const rule of state.rules) {
          if (!rule.enabled) continue;

          let matches = true;
          for (const condition of rule.conditions) {
            const fieldValue = condition.field === 'url' ? url : '';
            
            switch (condition.operator) {
              case 'equals':
                matches = fieldValue === condition.value;
                break;
              case 'contains':
                matches = fieldValue.includes(String(condition.value));
                break;
              case 'startsWith':
                matches = fieldValue.startsWith(String(condition.value));
                break;
              case 'endsWith':
                matches = fieldValue.endsWith(String(condition.value));
                break;
              case 'regex':
                try {
                  matches = new RegExp(String(condition.value)).test(fieldValue);
                } catch {
                  matches = false;
                }
                break;
              default:
                matches = false;
            }
            
            if (!matches) break;
          }

          if (matches) {
            for (const action of rule.actions) {
              switch (action.type) {
                case 'setCategory':
                  result.category = String(action.value);
                  break;
                case 'addTag':
                  if (typeof action.value === 'string') {
                    result.tags?.push(action.value);
                  }
                  break;
                case 'setPriority':
                  result.priority = Number(action.value);
                  break;
                case 'autoStart':
                  result.autoStart = Boolean(action.value);
                  break;
                case 'skipDownload':
                  return { skip: true };
              }
            }
            
            // Update rule stats
            set((s) => {
              const r = s.rules.find((r) => r.id === rule.id);
              if (r) {
                r.lastTriggered = new Date();
                r.triggerCount++;
              }
            });
            
            break; // First matching rule wins
          }
        }

        return result;
      },

      // ═════════════════════════════════════════════════════════════════════════
      // SPEED LIMIT ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      addSpeedLimitRule: (rule) => {
        const id = `speed_${Date.now()}`;
        set((state) => {
          state.speedLimitRules.push({ ...rule, id });
        });
        return id;
      },

      updateSpeedLimitRule: (id, updates) => {
        set((state) => {
          const index = state.speedLimitRules.findIndex((r) => r.id === id);
          if (index !== -1) {
            state.speedLimitRules[index] = { ...state.speedLimitRules[index], ...updates };
          }
        });
      },

      removeSpeedLimitRule: (id) => {
        set((state) => {
          state.speedLimitRules = state.speedLimitRules.filter((r) => r.id !== id);
        });
      },

      getCurrentSpeedLimit: () => {
        const state = get();
        const now = new Date();
        const currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
        const currentDay = now.getDay();

        for (const rule of state.speedLimitRules) {
          if (!rule.enabled) continue;
          
          // Check day
          if (rule.days && !rule.days.includes(currentDay)) continue;
          
          // Check time range
          if (rule.timeRange) {
            if (currentTime >= rule.timeRange.start && currentTime <= rule.timeRange.end) {
              return rule.maxSpeed;
            }
          } else {
            // No time range means always active
            return rule.maxSpeed;
          }
        }

        return 0; // No limit
      },

      // ═════════════════════════════════════════════════════════════════════════
      // SCHEDULE ACTIONS
      // ═════════════════════════════════════════════════════════════════════════

      addSchedule: (schedule) => {
        const id = `sched_${Date.now()}`;
        set((state) => {
          state.schedules.push({ ...schedule, id });
        });
        return id;
      },

      removeSchedule: (id) => {
        set((state) => {
          state.schedules = state.schedules.filter((s) => s.id !== id);
        });
      },

      toggleSchedule: (id) => {
        set((state) => {
          const schedule = state.schedules.find((s) => s.id === id);
          if (schedule) {
            schedule.enabled = !schedule.enabled;
          }
        });
      },

      getPendingSchedules: () => {
        const state = get();
        const now = new Date();
        return state.schedules.filter(
          (s) => s.enabled && new Date(s.scheduledFor) <= now
        );
      },

      // ═════════════════════════════════════════════════════════════════════════
      // SETTINGS
      // ═════════════════════════════════════════════════════════════════════════

      setMaxConcurrent: (max) => {
        set((state) => {
          state.maxConcurrent = Math.max(1, Math.min(10, max));
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // STATISTICS
      // ═════════════════════════════════════════════════════════════════════════

      updateStats: (completed, success, bytes) => {
        set((state) => {
          state.sessionStats.completed += completed ? 1 : 0;
          state.sessionStats.failed += !success ? 1 : 0;
          state.sessionStats.bytesDownloaded += bytes;
          state.totalBytes += bytes;
        });
      },

      resetSessionStats: () => {
        set((state) => {
          state.sessionStats = {
            started: 0,
            completed: 0,
            failed: 0,
            bytesDownloaded: 0,
          };
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // UNDO/REDO
      // ═════════════════════════════════════════════════════════════════════════

      undo: () => {
        const state = get();
        if (state.undoStack.length === 0) return false;

        const previousState = state.undoStack[state.undoStack.length - 1];
        
        set((s) => {
          // Save current state to redo stack
          s.redoStack.push(createUndoSnapshot(s, 'redo'));
          if (s.redoStack.length > s.maxUndoSteps) {
            s.redoStack.shift();
          }
          
          // Restore previous state
          s.downloads = Object.fromEntries(previousState.downloads);
          s.queue = previousState.queue;
          s.undoStack.pop();
        });

        return true;
      },

      redo: () => {
        const state = get();
        if (state.redoStack.length === 0) return false;

        const nextState = state.redoStack[state.redoStack.length - 1];
        
        set((s) => {
          // Save current state to undo stack
          s.undoStack.push(createUndoSnapshot(s, 'undo'));
          if (s.undoStack.length > s.maxUndoSteps) {
            s.undoStack.shift();
          }
          
          // Restore next state
          s.downloads = Object.fromEntries(nextState.downloads);
          s.queue = nextState.queue;
          s.redoStack.pop();
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
        // Persistence is handled by Zustand persist middleware
        set((state) => {
          state.isHydrated = true;
        });
      },

      setHydrated: (hydrated) => {
        set((state) => {
          state.isHydrated = hydrated;
        });
      },

      // ═════════════════════════════════════════════════════════════════════════
      // COMPUTED SELECTORS
      // ═════════════════════════════════════════════════════════════════════════

      getActiveDownloads: () => {
        const state = get();
        return Object.values(state.downloads).filter(
          (d) =>
            d.status === DownloadStatus.DOWNLOADING ||
            d.status === DownloadStatus.PENDING ||
            d.status === DownloadStatus.PAUSED
        );
      },

      getCompletedDownloads: () => {
        const state = get();
        return Object.values(state.downloads).filter(
          (d) => d.status === DownloadStatus.COMPLETED
        );
      },

      getFailedDownloads: () => {
        const state = get();
        return Object.values(state.downloads).filter(
          (d) => d.status === DownloadStatus.FAILED
        );
      },

      getByStatus: (status) => {
        const state = get();
        return Object.values(state.downloads).filter((d) => d.status === status);
      },

      getByCategory: (categoryId) => {
        const state = get();
        return state.queue
          .filter((item) => item.category === categoryId)
          .map((item) => state.downloads[item.id])
          .filter(Boolean);
      },

      getByTag: (tagId) => {
        const state = get();
        return state.queue
          .filter((item) => item.tags.includes(tagId))
          .map((item) => state.downloads[item.id])
          .filter(Boolean);
      },

      searchDownloads: (query) => {
        const state = get();
        const queryLower = query.toLowerCase();
        return Object.values(state.downloads).filter((d) => {
          const queueItem = state.queue.find((i) => i.id === d.downloadId);
          return (
            d.downloadId.toLowerCase().includes(queryLower) ||
            d.filePath?.toLowerCase().includes(queryLower) ||
            queueItem?.url.toLowerCase().includes(queryLower) ||
            queueItem?.tags.some((t) => t.toLowerCase().includes(queryLower))
          );
        });
      },

      getDownloadStats: () => {
        const state = get();
        const downloads = Object.values(state.downloads);
        const speeds = Object.values(state.progress)
          .map((p) => p.speed)
          .filter(Boolean);

        return {
          total: downloads.length,
          active: state.activeCount,
          completed: downloads.filter((d) => d.status === DownloadStatus.COMPLETED).length,
          failed: downloads.filter((d) => d.status === DownloadStatus.FAILED).length,
          pending: downloads.filter((d) => d.status === DownloadStatus.PENDING).length,
          totalBytes: state.totalBytes,
          averageSpeed: speeds.length > 0 ? speeds.reduce((a, b) => a + b, 0) / speeds.length : 0,
          averageDuration: 0, // Would need to track this separately
        };
      },

      getQueueStats: () => {
        const state = get();
        const now = Date.now();
        
        const pending = state.queue.filter((i) => !i.startedAt);
        const downloading = state.queue.filter((i) => i.startedAt && !i.completedAt);
        const failed = state.queue.filter((i) => i.error);
        
        // Calculate average wait time
        const waitTimes = pending
          .map((i) => now - new Date(i.addedAt).getTime())
          .filter((t) => t > 0);
        const avgWaitTime = waitTimes.length > 0
          ? waitTimes.reduce((a, b) => a + b, 0) / waitTimes.length
          : 0;

        return {
          total: state.queue.length,
          pending: pending.length,
          downloading: downloading.length,
          paused: state.queue.filter((i) => !i.autoStart).length,
          failed: failed.length,
          averageWaitTime: avgWaitTime,
          estimatedTimeRemaining: 0, // Would need more data to calculate
        };
      },
    })),
    {
      name: 'rs-toolkit-downloads',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        downloads: state.downloads,
        queue: state.queue.slice(0, 100), // Limit persisted queue size
        categories: state.categories,
        tags: state.tags,
        rules: state.rules,
        speedLimitRules: state.speedLimitRules,
        maxConcurrent: state.maxConcurrent,
        totalDownloaded: state.totalDownloaded,
        totalBytes: state.totalBytes,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.isHydrated = true;
          state.lastSaved = new Date();
        }
      },
    }
  )
);

// ═══════════════════════════════════════════════════════════════════════════════
// SELECTORS (for use with React hooks)
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Selector for active downloads count
 */
export const selectActiveCount = (state: DownloadStore) => state.activeCount;

/**
 * Selector for queue length
 */
export const selectQueueLength = (state: DownloadStore) => state.queue.length;

/**
 * Selector for downloads by status
 */
export const createSelectByStatus = (status: DownloadStatus) => 
  (state: DownloadStore) => Object.values(state.downloads).filter((d) => d.status === status);

/**
 * Selector for download progress
 */
export const selectProgress = (downloadId: string) => 
  (state: DownloadStore) => state.progress[downloadId];

/**
 * Selector for queue item
 */
export const selectQueueItem = (id: string) => 
  (state: DownloadStore) => state.queue.find((i) => i.id === id);

/**
 * Selector for categories
 */
export const selectCategories = (state: DownloadStore) => state.categories;

/**
 * Selector for tags
 */
export const selectTags = (state: DownloadStore) => state.tags;

/**
 * Selector for rules
 */
export const selectRules = (state: DownloadStore) => state.rules;

/**
 * Selector for session statistics
 */
export const selectSessionStats = (state: DownloadStore) => state.sessionStats;

export default useDownloadStore;
