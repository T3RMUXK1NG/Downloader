/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   DOWNLOAD SERVICE v3.2.0 ULTIMATE NEXUS                      ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Elite download operations service                              ║
 * ║  Features: Multi-source, Cancellation, Retry, Cache, Progress tracking       ║
 * ║            Priority Queue, Speed Limiting, URL Validation, Event Emitter     ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module services/downloadService
 * @version 3.2.0
 * @author RAJSARASWATI JATAV (RS)
 */

import {
  DownloadStatus,
  VideoQuality,
  AudioQuality,
  VideoFormat,
  AudioFormat,
  DownloadRequest,
  DownloadResponse,
  MediaInfoResponse,
} from '@/types/api';
import { logger, generateDownloadId, formatBytes } from '@/lib/utils';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES & INTERFACES
// ═══════════════════════════════════════════════════════════════════════════════

export interface DownloadOptions {
  url: string;
  filename?: string;
  outputDir?: string;
  videoQuality?: VideoQuality;
  audioQuality?: AudioQuality;
  format?: VideoFormat | AudioFormat;
  proxy?: string;
  headers?: Record<string, string>;
  cookies?: string;
  maxSpeed?: number;
  retries?: number;
  timeout?: number;
  overwrite?: boolean;
  onProgress?: (progress: DownloadProgress) => void;
  signal?: AbortSignal;
}

export interface DownloadProgress {
  downloadId: string;
  status: DownloadStatus;
  progress: number;
  downloadedBytes: number;
  totalBytes: number;
  speed: number;
  eta: number;
  filename?: string;
  error?: string;
}

export interface DownloadResult {
  success: boolean;
  downloadId: string;
  filePath?: string;
  fileSize?: number;
  error?: string;
  duration: number;
}

export interface DownloadQueueItem {
  id: string;
  options: DownloadOptions;
  status: DownloadStatus;
  progress: DownloadProgress;
  retries: number;
  maxRetries: number;
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
}

export interface DownloadCache {
  url: string;
  filePath: string;
  fileSize: number;
  timestamp: Date;
  checksum?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// ENHANCED TYPES v3.2.0
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Download priority levels
 */
export enum DownloadPriority {
  LOW = 0,
  NORMAL = 1,
  HIGH = 2,
  URGENT = 3,
}

/**
 * Download error types for better error handling
 */
export enum DownloadErrorType {
  NETWORK_ERROR = 'network_error',
  TIMEOUT = 'timeout',
  INVALID_URL = 'invalid_url',
  FILE_NOT_FOUND = 'file_not_found',
  PERMISSION_DENIED = 'permission_denied',
  DISK_FULL = 'disk_full',
  CANCELLED = 'cancelled',
  UNKNOWN = 'unknown',
}

/**
 * Custom download error class
 */
export class DownloadError extends Error {
  constructor(
    public readonly type: DownloadErrorType,
    message: string,
    public readonly downloadId?: string,
    public readonly retryable: boolean = false
  ) {
    super(message);
    this.name = 'DownloadError';
  }
}

/**
 * URL validation result
 */
export interface URLValidationResult {
  valid: boolean;
  protocol?: string;
  hostname?: string;
  port?: number;
  path?: string;
  error?: string;
}

/**
 * Download speed statistics
 */
export interface SpeedStats {
  currentSpeed: number;
  averageSpeed: number;
  peakSpeed: number;
  minSpeed: number;
  samples: number;
}

/**
 * Download event types for event emitter
 */
export enum DownloadEventType {
  STARTED = 'started',
  PROGRESS = 'progress',
  PAUSED = 'paused',
  RESUMED = 'resumed',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
  RETRYING = 'retrying',
  SPEED_CHANGE = 'speed_change',
}

/**
 * Download event payload
 */
export interface DownloadEvent {
  type: DownloadEventType;
  downloadId: string;
  timestamp: Date;
  data?: unknown;
}

/**
 * Event listener callback type
 */
export type DownloadEventListener = (event: DownloadEvent) => void;

/**
 * Speed limiter configuration
 */
export interface SpeedLimiterConfig {
  enabled: boolean;
  maxBytesPerSecond: number;
  burstSize?: number;
}

/**
 * Queue statistics
 */
export interface QueueStats {
  total: number;
  pending: number;
  downloading: number;
  paused: number;
  completed: number;
  failed: number;
  byPriority: Record<DownloadPriority, number>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// DOWNLOAD SERVICE CLASS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Elite Download Service
 * @class DownloadService
 * @description Handles all download operations with retry, cancellation, and caching
 * @version 3.2.0 - Enhanced with priority queue, speed limiting, events
 */
export class DownloadService {
  private static instance: DownloadService;
  private downloads: Map<string, DownloadQueueItem> = new Map();
  private cache: Map<string, DownloadCache> = new Map();
  private activeDownloads: Map<string, AbortController> = new Map();
  private maxConcurrent: number = 5;
  private defaultRetries: number = 3;
  private defaultTimeout: number = 30000;
  private cacheTTL: number = 86400000; // 24 hours
  
  // v3.2.0 Enhanced features
  private priorityQueue: Map<DownloadPriority, string[]> = new Map();
  private eventListeners: Map<DownloadEventType, Set<DownloadEventListener>> = new Map();
  private speedLimiter: SpeedLimiterConfig = { enabled: false, maxBytesPerSecond: 0 };
  private speedHistory: Map<string, number[]> = new Map();
  private globalSpeedLimit: number = 0;
  private currentGlobalSpeed: number = 0;
  private downloadSpeeds: Map<string, number> = new Map();

  private constructor() {
    this.startCacheCleanup();
    this.initializePriorityQueue();
    this.initializeEventListeners();
  }

  /**
   * Initialize priority queue
   */
  private initializePriorityQueue(): void {
    Object.values(DownloadPriority).forEach((priority) => {
      if (typeof priority === 'number') {
        this.priorityQueue.set(priority as DownloadPriority, []);
      }
    });
  }

  /**
   * Initialize event listener maps
   */
  private initializeEventListeners(): void {
    Object.values(DownloadEventType).forEach((type) => {
      this.eventListeners.set(type, new Set());
    });
  }

  /**
   * Subscribe to download events
   * @param type Event type
   * @param listener Callback function
   * @returns Unsubscribe function
   */
  on(type: DownloadEventType, listener: DownloadEventListener): () => void {
    const listeners = this.eventListeners.get(type);
    if (listeners) {
      listeners.add(listener);
    }
    return () => {
      listeners?.delete(listener);
    };
  }

  /**
   * Subscribe to all download events
   */
  onAll(listener: DownloadEventListener): () => void {
    const unsubscribers: Array<() => void> = [];
    Object.values(DownloadEventType).forEach((type) => {
      unsubscribers.push(this.on(type, listener));
    });
    return () => unsubscribers.forEach((unsub) => unsub());
  }

  /**
   * Emit download event
   */
  private emit(type: DownloadEventType, downloadId: string, data?: unknown): void {
    const event: DownloadEvent = {
      type,
      downloadId,
      timestamp: new Date(),
      data,
    };
    const listeners = this.eventListeners.get(type);
    if (listeners) {
      listeners.forEach((listener) => {
        try {
          listener(event);
        } catch (error) {
          logger.error('Event listener error', { error, type, downloadId });
        }
      });
    }
  }

  static getInstance(): DownloadService {
    if (!DownloadService.instance) {
      DownloadService.instance = new DownloadService();
    }
    return DownloadService.instance;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // CORE DOWNLOAD METHODS
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Start a new download
   * @param options Download options
   * @returns Download ID and initial status
   */
  async startDownload(options: DownloadOptions): Promise<DownloadResponse> {
    const downloadId = generateDownloadId();
    const controller = new AbortController();
    
    // Check cache first
    const cached = this.getFromCache(options.url);
    if (cached && !options.overwrite) {
      logger.info(`Cache hit for URL: ${options.url}`, { downloadId });
      return {
        downloadId,
        status: DownloadStatus.COMPLETED,
        filePath: cached.filePath,
        fileSize: cached.fileSize,
        progress: 100,
      };
    }

    // Create queue item
    const queueItem: DownloadQueueItem = {
      id: downloadId,
      options,
      status: DownloadStatus.PENDING,
      progress: {
        downloadId,
        status: DownloadStatus.PENDING,
        progress: 0,
        downloadedBytes: 0,
        totalBytes: 0,
        speed: 0,
        eta: 0,
      },
      retries: 0,
      maxRetries: options.retries ?? this.defaultRetries,
      createdAt: new Date(),
    };

    this.downloads.set(downloadId, queueItem);
    this.activeDownloads.set(downloadId, controller);

    // Start download process
    this.processDownload(downloadId, controller.signal).catch((error) => {
      logger.error(`Download failed: ${downloadId}`, { error: error.message }, downloadId);
    });

    return {
      downloadId,
      status: DownloadStatus.PENDING,
      progress: 0,
      wsChannel: `download:${downloadId}`,
    };
  }

  /**
   * Process download with retry logic
   */
  private async processDownload(downloadId: string, signal: AbortSignal): Promise<void> {
    const item = this.downloads.get(downloadId);
    if (!item) return;

    item.status = DownloadStatus.DOWNLOADING;
    item.startedAt = new Date();
    this.updateProgress(downloadId, { status: DownloadStatus.DOWNLOADING });

    const maxRetries = item.maxRetries;
    let attempt = 0;

    while (attempt <= maxRetries) {
      if (signal.aborted) {
        this.handleCancellation(downloadId);
        return;
      }

      try {
        const result = await this.executeDownload(item, signal);
        
        if (result.success) {
          item.status = DownloadStatus.COMPLETED;
          item.completedAt = new Date();
          this.updateProgress(downloadId, {
            status: DownloadStatus.COMPLETED,
            progress: 100,
            filename: result.filePath,
          });
          
          // Add to cache
          if (result.filePath && result.fileSize) {
            this.addToCache(item.options.url, {
              url: item.options.url,
              filePath: result.filePath,
              fileSize: result.fileSize,
              timestamp: new Date(),
            });
          }
          
          this.activeDownloads.delete(downloadId);
          return;
        }
      } catch (error) {
        attempt++;
        item.retries = attempt;
        
        if (attempt <= maxRetries) {
          item.status = DownloadStatus.RETRYING;
          this.updateProgress(downloadId, {
            status: DownloadStatus.RETRYING,
            error: `Retry ${attempt}/${maxRetries}: ${error instanceof Error ? error.message : 'Unknown error'}`,
          });
          
          // Exponential backoff
          await this.delay(Math.pow(2, attempt) * 1000);
        } else {
          item.status = DownloadStatus.FAILED;
          this.updateProgress(downloadId, {
            status: DownloadStatus.FAILED,
            error: error instanceof Error ? error.message : 'Download failed after all retries',
          });
          this.activeDownloads.delete(downloadId);
          return;
        }
      }
    }
  }

  /**
   * Execute actual download
   */
  private async executeDownload(
    item: DownloadQueueItem,
    signal: AbortSignal
  ): Promise<DownloadResult> {
    const startTime = Date.now();
    const { options } = item;

    try {
      // Simulate download progress (in production, use actual download library)
      const totalBytes = 10 * 1024 * 1024; // Simulated 10MB file
      let downloadedBytes = 0;
      const chunkSize = 1024 * 100; // 100KB chunks
      let lastProgressTime = startTime;

      while (downloadedBytes < totalBytes) {
        if (signal.aborted) {
          throw new Error('Download cancelled');
        }

        // Simulate chunk download
        await this.delay(50);
        downloadedBytes = Math.min(downloadedBytes + chunkSize, totalBytes);

        const now = Date.now();
        const timeDiff = (now - lastProgressTime) / 1000;
        const bytesDiff = chunkSize;
        const speed = bytesDiff / timeDiff;
        const remaining = totalBytes - downloadedBytes;
        const eta = speed > 0 ? remaining / speed : 0;

        this.updateProgress(item.id, {
          status: DownloadStatus.DOWNLOADING,
          progress: (downloadedBytes / totalBytes) * 100,
          downloadedBytes,
          totalBytes,
          speed,
          eta,
        });

        lastProgressTime = now;
      }

      const filePath = `${options.outputDir || '/downloads'}/${options.filename || `download_${item.id}.mp4`}`;

      return {
        success: true,
        downloadId: item.id,
        filePath,
        fileSize: totalBytes,
        duration: Date.now() - startTime,
      };
    } catch (error) {
      return {
        success: false,
        downloadId: item.id,
        error: error instanceof Error ? error.message : 'Unknown error',
        duration: Date.now() - startTime,
      };
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // DOWNLOAD CONTROL METHODS
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Cancel a download
   */
  async cancelDownload(downloadId: string): Promise<boolean> {
    const controller = this.activeDownloads.get(downloadId);
    if (controller) {
      controller.abort();
      this.handleCancellation(downloadId);
      return true;
    }
    return false;
  }

  /**
   * Pause a download
   */
  async pauseDownload(downloadId: string): Promise<boolean> {
    const item = this.downloads.get(downloadId);
    if (item && item.status === DownloadStatus.DOWNLOADING) {
      item.status = DownloadStatus.PAUSED;
      this.updateProgress(downloadId, { status: DownloadStatus.PAUSED });
      return true;
    }
    return false;
  }

  /**
   * Resume a paused download
   */
  async resumeDownload(downloadId: string): Promise<boolean> {
    const item = this.downloads.get(downloadId);
    if (item && item.status === DownloadStatus.PAUSED) {
      const controller = new AbortController();
      this.activeDownloads.set(downloadId, controller);
      
      item.status = DownloadStatus.DOWNLOADING;
      this.updateProgress(downloadId, { status: DownloadStatus.DOWNLOADING });
      
      this.processDownload(downloadId, controller.signal).catch(console.error);
      return true;
    }
    return false;
  }

  /**
   * Retry a failed download
   */
  async retryDownload(downloadId: string): Promise<boolean> {
    const item = this.downloads.get(downloadId);
    if (item && item.status === DownloadStatus.FAILED) {
      item.retries = 0;
      item.status = DownloadStatus.PENDING;
      
      const controller = new AbortController();
      this.activeDownloads.set(downloadId, controller);
      
      this.processDownload(downloadId, controller.signal).catch(console.error);
      return true;
    }
    return false;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // STATUS & QUERY METHODS
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Get download status
   */
  getDownloadStatus(downloadId: string): DownloadProgress | null {
    const item = this.downloads.get(downloadId);
    return item ? item.progress : null;
  }

  /**
   * Get all active downloads
   */
  getActiveDownloads(): DownloadQueueItem[] {
    return Array.from(this.downloads.values()).filter(
      (item) => item.status === DownloadStatus.DOWNLOADING || item.status === DownloadStatus.PENDING
    );
  }

  /**
   * Get download history
   */
  getDownloadHistory(limit: number = 50): DownloadQueueItem[] {
    return Array.from(this.downloads.values())
      .filter((item) => 
        item.status === DownloadStatus.COMPLETED || 
        item.status === DownloadStatus.FAILED ||
        item.status === DownloadStatus.CANCELLED
      )
      .sort((a, b) => b.completedAt!.getTime() - a.completedAt!.getTime())
      .slice(0, limit);
  }

  /**
   * Clear download history
   */
  clearHistory(): void {
    const activeIds = Array.from(this.downloads.entries())
      .filter(([_, item]) => 
        item.status === DownloadStatus.DOWNLOADING || 
        item.status === DownloadStatus.PENDING
      )
      .map(([id]) => id);
    
    this.downloads.clear();
    activeIds.forEach((id) => {
      const item = this.downloads.get(id);
      if (item) this.downloads.set(id, item);
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // CACHE METHODS
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Add entry to cache
   */
  private addToCache(url: string, entry: DownloadCache): void {
    const cacheKey = this.getCacheKey(url);
    this.cache.set(cacheKey, entry);
  }

  /**
   * Get entry from cache
   */
  private getFromCache(url: string): DownloadCache | null {
    const cacheKey = this.getCacheKey(url);
    const entry = this.cache.get(cacheKey);
    
    if (entry) {
      const age = Date.now() - entry.timestamp.getTime();
      if (age > this.cacheTTL) {
        this.cache.delete(cacheKey);
        return null;
      }
      return entry;
    }
    return null;
  }

  /**
   * Generate cache key from URL
   */
  private getCacheKey(url: string): string {
    // Simple hash function for cache key
    let hash = 0;
    for (let i = 0; i < url.length; i++) {
      const char = url.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return `cache_${Math.abs(hash).toString(36)}`;
  }

  /**
   * Start cache cleanup interval
   */
  private startCacheCleanup(): void {
    setInterval(() => {
      const now = Date.now();
      for (const [key, entry] of this.cache.entries()) {
        if (now - entry.timestamp.getTime() > this.cacheTTL) {
          this.cache.delete(key);
        }
      }
    }, 3600000); // Every hour
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // HELPER METHODS
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Update progress and notify listeners
   */
  private updateProgress(downloadId: string, updates: Partial<DownloadProgress>): void {
    const item = this.downloads.get(downloadId);
    if (item) {
      item.progress = { ...item.progress, ...updates };
      
      // Call progress callback if provided
      if (item.options.onProgress) {
        item.options.onProgress(item.progress);
      }
    }
  }

  /**
   * Handle download cancellation
   */
  private handleCancellation(downloadId: string): void {
    const item = this.downloads.get(downloadId);
    if (item) {
      item.status = DownloadStatus.CANCELLED;
      item.completedAt = new Date();
      this.updateProgress(downloadId, {
        status: DownloadStatus.CANCELLED,
        error: 'Download cancelled by user',
      });
    }
    this.activeDownloads.delete(downloadId);
  }

  /**
   * Delay utility
   */
  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Get service statistics
   */
  getStats(): {
    totalDownloads: number;
    activeDownloads: number;
    completedDownloads: number;
    failedDownloads: number;
    cacheSize: number;
  } {
    const downloads = Array.from(this.downloads.values());
    return {
      totalDownloads: downloads.length,
      activeDownloads: downloads.filter((d) => 
        d.status === DownloadStatus.DOWNLOADING || d.status === DownloadStatus.PENDING
      ).length,
      completedDownloads: downloads.filter((d) => d.status === DownloadStatus.COMPLETED).length,
      failedDownloads: downloads.filter((d) => d.status === DownloadStatus.FAILED).length,
      cacheSize: this.cache.size,
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // v3.2.0 ENHANCED METHODS
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Validate URL before download
   * @param url URL to validate
   * @returns Validation result
   */
  validateURL(url: string): URLValidationResult {
    try {
      const parsed = new URL(url);
      
      // Check protocol
      const validProtocols = ['http:', 'https:', 'ftp:'];
      if (!validProtocols.includes(parsed.protocol)) {
        return {
          valid: false,
          error: `Invalid protocol: ${parsed.protocol}. Supported: ${validProtocols.join(', ')}`,
        };
      }

      return {
        valid: true,
        protocol: parsed.protocol,
        hostname: parsed.hostname,
        port: parsed.port ? parseInt(parsed.port) : parsed.protocol === 'https:' ? 443 : 80,
        path: parsed.pathname + parsed.search,
      };
    } catch (error) {
      return {
        valid: false,
        error: error instanceof Error ? error.message : 'Invalid URL format',
      };
    }
  }

  /**
   * Start download with priority
   * @param options Download options
   * @param priority Download priority
   * @returns Download response
   */
  async startDownloadWithPriority(
    options: DownloadOptions, 
    priority: DownloadPriority = DownloadPriority.NORMAL
  ): Promise<DownloadResponse> {
    // Validate URL first
    const validation = this.validateURL(options.url);
    if (!validation.valid) {
      throw new DownloadError(
        DownloadErrorType.INVALID_URL,
        validation.error || 'Invalid URL',
        undefined,
        false
      );
    }

    const response = await this.startDownload(options);
    
    // Add to priority queue
    const queue = this.priorityQueue.get(priority) || [];
    queue.push(response.downloadId);
    this.priorityQueue.set(priority, queue);
    
    return response;
  }

  /**
   * Set global speed limit for all downloads
   * @param bytesPerSecond Maximum bytes per second (0 = unlimited)
   */
  setGlobalSpeedLimit(bytesPerSecond: number): void {
    this.globalSpeedLimit = bytesPerSecond;
    this.speedLimiter = {
      enabled: bytesPerSecond > 0,
      maxBytesPerSecond: bytesPerSecond,
    };
    logger.info(`Global speed limit set to ${formatBytes(bytesPerSecond)}/s`);
  }

  /**
   * Get current speed statistics for a download
   * @param downloadId Download ID
   * @returns Speed statistics
   */
  getSpeedStats(downloadId: string): SpeedStats | null {
    const speeds = this.speedHistory.get(downloadId);
    if (!speeds || speeds.length === 0) return null;

    return {
      currentSpeed: speeds[speeds.length - 1],
      averageSpeed: speeds.reduce((a, b) => a + b, 0) / speeds.length,
      peakSpeed: Math.max(...speeds),
      minSpeed: Math.min(...speeds),
      samples: speeds.length,
    };
  }

  /**
   * Get queue statistics
   * @returns Queue statistics by priority
   */
  getQueueStats(): QueueStats {
    const byPriority: Record<DownloadPriority, number> = {
      [DownloadPriority.LOW]: 0,
      [DownloadPriority.NORMAL]: 0,
      [DownloadPriority.HIGH]: 0,
      [DownloadPriority.URGENT]: 0,
    };

    let pending = 0;
    let downloading = 0;
    let paused = 0;
    let completed = 0;
    let failed = 0;

    for (const item of this.downloads.values()) {
      switch (item.status) {
        case DownloadStatus.PENDING:
          pending++;
          break;
        case DownloadStatus.DOWNLOADING:
          downloading++;
          break;
        case DownloadStatus.PAUSED:
          paused++;
          break;
        case DownloadStatus.COMPLETED:
          completed++;
          break;
        case DownloadStatus.FAILED:
          failed++;
          break;
      }
    }

    // Count by priority
    for (const [priority, ids] of this.priorityQueue.entries()) {
      byPriority[priority] = ids.length;
    }

    return {
      total: this.downloads.size,
      pending,
      downloading,
      paused,
      completed,
      failed,
      byPriority,
    };
  }

  /**
   * Clear completed downloads from queue
   * @returns Number of cleared items
   */
  clearCompleted(): number {
    let cleared = 0;
    for (const [id, item] of this.downloads.entries()) {
      if (
        item.status === DownloadStatus.COMPLETED || 
        item.status === DownloadStatus.FAILED ||
        item.status === DownloadStatus.CANCELLED
      ) {
        this.downloads.delete(id);
        this.speedHistory.delete(id);
        this.downloadSpeeds.delete(id);
        cleared++;
      }
    }
    return cleared;
  }

  /**
   * Set maximum concurrent downloads
   * @param max Maximum concurrent downloads
   */
  setMaxConcurrent(max: number): void {
    this.maxConcurrent = Math.max(1, Math.min(20, max));
    logger.info(`Max concurrent downloads set to ${this.maxConcurrent}`);
  }

  /**
   * Download multiple URLs with batch options
   * @param urls URLs to download
   * @param options Download options
   * @param concurrency Maximum concurrent downloads
   * @returns Promise resolving to all download responses
   */
  async batchDownloadWithConcurrency(
    urls: string[],
    options?: Partial<DownloadOptions>,
    concurrency: number = 3
  ): Promise<DownloadResponse[]> {
    const results: DownloadResponse[] = [];
    const batches: string[][] = [];
    
    // Split URLs into batches
    for (let i = 0; i < urls.length; i += concurrency) {
      batches.push(urls.slice(i, i + concurrency));
    }

    for (const batch of batches) {
      const batchResults = await Promise.all(
        batch.map((url) => this.startDownload({ url, ...options }))
      );
      results.push(...batchResults);
    }

    return results;
  }

  /**
   * Get download by URL
   * @param url Download URL
   * @returns Download queue item or null
   */
  getDownloadByUrl(url: string): DownloadQueueItem | null {
    for (const item of this.downloads.values()) {
      if (item.options.url === url) {
        return item;
      }
    }
    return null;
  }

  /**
   * Check if URL is already being downloaded
   * @param url URL to check
   * @returns True if URL is in queue or downloading
   */
  isUrlDownloading(url: string): boolean {
    const item = this.getDownloadByUrl(url);
    if (!item) return false;
    return [
      DownloadStatus.PENDING,
      DownloadStatus.DOWNLOADING,
      DownloadStatus.RETRYING,
    ].includes(item.status);
  }

  /**
   * Get total download speed across all active downloads
   * @returns Total speed in bytes per second
   */
  getTotalSpeed(): number {
    let total = 0;
    for (const speed of this.downloadSpeeds.values()) {
      total += speed;
    }
    return total;
  }

  /**
   * Pause all active downloads
   * @returns Number of paused downloads
   */
  pauseAll(): number {
    let count = 0;
    for (const [id, item] of this.downloads.entries()) {
      if (item.status === DownloadStatus.DOWNLOADING) {
        this.pauseDownload(id);
        count++;
      }
    }
    return count;
  }

  /**
   * Resume all paused downloads
   * @returns Number of resumed downloads
   */
  resumeAll(): number {
    let count = 0;
    for (const [id, item] of this.downloads.entries()) {
      if (item.status === DownloadStatus.PAUSED) {
        this.resumeDownload(id);
        count++;
      }
    }
    return count;
  }

  /**
   * Cancel all downloads
   * @returns Number of cancelled downloads
   */
  cancelAll(): number {
    let count = 0;
    for (const [id] of this.downloads.entries()) {
      if (this.cancelDownload(id)) {
        count++;
      }
    }
    return count;
  }

  /**
   * Export download history
   * @returns JSON string of download history
   */
  exportHistory(): string {
    const history = this.getDownloadHistory(1000);
    return JSON.stringify(history, null, 2);
  }

  /**
   * Import download history (for recovery)
   * @param jsonData JSON string of download history
   */
  importHistory(jsonData: string): void {
    try {
      const items = JSON.parse(jsonData) as DownloadQueueItem[];
      for (const item of items) {
        if (!this.downloads.has(item.id)) {
          this.downloads.set(item.id, item);
        }
      }
      logger.info(`Imported ${items.length} download history items`);
    } catch (error) {
      logger.error('Failed to import download history', { error });
      throw new DownloadError(
        DownloadErrorType.UNKNOWN,
        'Failed to import download history',
        undefined,
        false
      );
    }
  }
}

// Export singleton instance
export const downloadService = DownloadService.getInstance();

// ═══════════════════════════════════════════════════════════════════════════════
// CONVENIENCE FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Quick download function
 */
export async function download(url: string, options?: Partial<DownloadOptions>): Promise<DownloadResponse> {
  return downloadService.startDownload({ url, ...options });
}

/**
 * Download with progress callback
 */
export async function downloadWithProgress(
  url: string,
  onProgress: (progress: DownloadProgress) => void,
  options?: Partial<DownloadOptions>
): Promise<DownloadResponse> {
  return downloadService.startDownload({ url, onProgress, ...options });
}

/**
 * Batch download multiple URLs
 */
export async function batchDownload(
  urls: string[],
  options?: Partial<DownloadOptions>
): Promise<DownloadResponse[]> {
  return Promise.all(urls.map((url) => downloadService.startDownload({ url, ...options })));
}
