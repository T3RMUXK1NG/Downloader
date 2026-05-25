/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   DOWNLOAD SERVICE v3.0.1 ULTIMATE NEXUS                      ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Elite download operations service                              ║
 * ║  Features: Multi-source, Cancellation, Retry, Cache, Progress tracking       ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module services/downloadService
 * @version 3.0.1
 * @author RAJSARASWATI JATEV (RS)
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
// DOWNLOAD SERVICE CLASS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Elite Download Service
 * @class DownloadService
 * @description Handles all download operations with retry, cancellation, and caching
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

  private constructor() {
    this.startCacheCleanup();
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
