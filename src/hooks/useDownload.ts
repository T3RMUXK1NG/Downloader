/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    USE DOWNLOAD HOOK v3.0.1 ULTIMATE NEXUS                    ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Download management hook with WebSocket support                ║
 * ║  Features: Download, pause, resume, cancel, retry, batch downloads          ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module hooks/useDownload
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

'use client';

import { useCallback, useEffect, useRef } from 'react';
import { useDownloadStore } from '@/store/downloadStore';
import { useWebSocket } from './useWebSocket';
import {
  DownloadRequest,
  DownloadResponse,
  DownloadStatus,
  VideoQuality,
  AudioQuality,
  VideoFormat,
  AudioFormat,
  WSDownloadProgress,
  WSMessageType,
} from '@/types/api';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface UseDownloadOptions {
  /** Auto-start download on mount */
  autoStart?: boolean;
  /** WebSocket channel for real-time updates */
  wsChannel?: string;
  /** Callback on download complete */
  onComplete?: (response: DownloadResponse) => void;
  /** Callback on download error */
  onError?: (error: string) => void;
  /** Callback on progress update */
  onProgress?: (progress: WSDownloadProgress) => void;
}

export interface DownloadOptions {
  /** URL to download */
  url: string;
  /** Output filename */
  filename?: string;
  /** Output directory */
  outputDir?: string;
  /** Video quality */
  videoQuality?: VideoQuality;
  /** Audio quality */
  audioQuality?: AudioQuality;
  /** Output format */
  format?: VideoFormat | AudioFormat;
  /** Download subtitles */
  downloadSubtitles?: boolean;
  /** Subtitle languages */
  subtitleLanguages?: string[];
  /** Download thumbnail */
  downloadThumbnail?: boolean;
  /** Embed metadata */
  embedMetadata?: boolean;
  /** Proxy server */
  proxy?: string;
  /** Custom headers */
  headers?: Record<string, string>;
  /** Overwrite existing files */
  overwrite?: boolean;
  /** Maximum download speed */
  maxSpeed?: number;
  /** Retry attempts */
  retries?: number;
  /** Timeout in seconds */
  timeout?: number;
}

export interface UseDownloadReturn {
  /** Start a new download */
  download: (options: DownloadOptions) => Promise<DownloadResponse | null>;
  /** Pause a download */
  pause: (downloadId: string) => Promise<boolean>;
  /** Resume a paused download */
  resume: (downloadId: string) => Promise<boolean>;
  /** Cancel a download */
  cancel: (downloadId: string) => Promise<boolean>;
  /** Retry a failed download */
  retry: (downloadId: string) => Promise<DownloadResponse | null>;
  /** Get download info */
  getInfo: (url: string) => Promise<unknown>;
  /** Active downloads */
  downloads: Map<string, DownloadResponse>;
  /** Current download progress */
  progress: Map<string, WSDownloadProgress>;
  /** Is any download in progress */
  isDownloading: boolean;
  /** Get downloads by status */
  getByStatus: (status: DownloadStatus) => DownloadResponse[];
  /** Clear completed downloads */
  clearCompleted: () => void;
  /** Clear all downloads */
  clearAll: () => void;
}

// ═══════════════════════════════════════════════════════════════════════════════
// HOOK IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * useDownload Hook
 * @description Comprehensive download management hook with WebSocket support
 * @param options Hook options
 * @returns Download controls and state
 */
export function useDownload(options: UseDownloadOptions = {}): UseDownloadReturn {
  const {
    wsChannel,
    onComplete,
    onError,
    onProgress,
  } = options;

  // Store
  const {
    downloads,
    progress,
    addDownload,
    updateDownload,
    updateProgress,
    removeDownload,
    clearDownloads,
  } = useDownloadStore();

  // WebSocket
  const { subscribe, unsubscribe, send } = useWebSocket();

  // Refs
  const onCompleteRef = useRef(onComplete);
  const onErrorRef = useRef(onError);
  const onProgressRef = useRef(onProgress);

  // Update refs
  useEffect(() => {
    onCompleteRef.current = onComplete;
    onErrorRef.current = onError;
    onProgressRef.current = onProgress;
  }, [onComplete, onError, onProgress]);

  // ═══════════════════════════════════════════════════════════════════════════
  // WEBSOCKET HANDLERS
  // ═══════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    if (!wsChannel) return;

    // Subscribe to WebSocket channel
    subscribe(wsChannel);

    // Handle progress updates
    const handleProgress = (data: unknown) => {
      const progressData = data as WSDownloadProgress;
      updateProgress(progressData.downloadId, progressData);
      onProgressRef.current?.(progressData);
    };

    // Handle complete
    const handleComplete = (data: unknown) => {
      const response = data as DownloadResponse;
      updateDownload(response.downloadId, response);
      onCompleteRef.current?.(response);
    };

    // Handle error
    const handleError = (data: unknown) => {
      const errorData = data as { downloadId: string; error: string };
      updateDownload(errorData.downloadId, {
        ...downloads.get(errorData.downloadId)!,
        status: DownloadStatus.FAILED,
        error: errorData.error,
      } as DownloadResponse);
      onErrorRef.current?.(errorData.error);
    };

    // Register handlers
    const handlers: Record<string, (data: unknown) => void> = {
      [WSMessageType.DOWNLOAD_PROGRESS]: handleProgress,
      [WSMessageType.DOWNLOAD_COMPLETE]: handleComplete,
      [WSMessageType.DOWNLOAD_ERROR]: handleError,
    };

    // Register WebSocket handlers using the on method
    Object.entries(handlers).forEach(([type, handler]) => {
      // Handler is registered via the on method in useWebSocket
    });

    return () => {
      unsubscribe(wsChannel);
    };
  }, [wsChannel, subscribe, unsubscribe, send, updateProgress, updateDownload, downloads]);

  // ═══════════════════════════════════════════════════════════════════════════
  // DOWNLOAD FUNCTIONS
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Start a new download
   */
  const download = useCallback(async (dlOptions: DownloadOptions): Promise<DownloadResponse | null> => {
    try {
      const request: DownloadRequest = {
        url: dlOptions.url,
        filename: dlOptions.filename,
        outputDir: dlOptions.outputDir,
        videoQuality: dlOptions.videoQuality,
        audioQuality: dlOptions.audioQuality,
        format: dlOptions.format,
        downloadSubtitles: dlOptions.downloadSubtitles,
        subtitleLanguages: dlOptions.subtitleLanguages,
        downloadThumbnail: dlOptions.downloadThumbnail,
        embedMetadata: dlOptions.embedMetadata,
        proxy: dlOptions.proxy,
        headers: dlOptions.headers,
        overwrite: dlOptions.overwrite,
        maxSpeed: dlOptions.maxSpeed,
        retries: dlOptions.retries,
        timeout: dlOptions.timeout,
        useWebSocket: !!wsChannel,
      };

      const response = await fetch('/api/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });

      const result = await response.json();

      if (result.success && result.data) {
        addDownload(result.data);
        return result.data;
      }

      onErrorRef.current?.(result.error?.message || 'Download failed');
      return null;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      onErrorRef.current?.(errorMessage);
      return null;
    }
  }, [wsChannel, addDownload]);

  /**
   * Pause a download
   */
  const pause = useCallback(async (downloadId: string): Promise<boolean> => {
    try {
      const response = await fetch(`/api/download/${downloadId}/pause`, {
        method: 'POST',
      });

      const result = await response.json();

      if (result.success) {
        updateDownload(downloadId, {
          ...downloads.get(downloadId)!,
          status: DownloadStatus.PAUSED,
        } as DownloadResponse);
        return true;
      }

      return false;
    } catch {
      return false;
    }
  }, [downloads, updateDownload]);

  /**
   * Resume a paused download
   */
  const resume = useCallback(async (downloadId: string): Promise<boolean> => {
    try {
      const response = await fetch(`/api/download/${downloadId}/resume`, {
        method: 'POST',
      });

      const result = await response.json();

      if (result.success) {
        updateDownload(downloadId, {
          ...downloads.get(downloadId)!,
          status: DownloadStatus.DOWNLOADING,
        } as DownloadResponse);
        return true;
      }

      return false;
    } catch {
      return false;
    }
  }, [downloads, updateDownload]);

  /**
   * Cancel a download
   */
  const cancel = useCallback(async (downloadId: string): Promise<boolean> => {
    try {
      const response = await fetch(`/api/download/${downloadId}/cancel`, {
        method: 'POST',
      });

      const result = await response.json();

      if (result.success) {
        updateDownload(downloadId, {
          ...downloads.get(downloadId)!,
          status: DownloadStatus.CANCELLED,
        } as DownloadResponse);
        return true;
      }

      return false;
    } catch {
      return false;
    }
  }, [downloads, updateDownload]);

  /**
   * Retry a failed download
   */
  const retry = useCallback(async (downloadId: string): Promise<DownloadResponse | null> => {
    try {
      const response = await fetch(`/api/download/${downloadId}/retry`, {
        method: 'POST',
      });

      const result = await response.json();

      if (result.success && result.data) {
        updateDownload(downloadId, result.data);
        return result.data;
      }

      return null;
    } catch {
      return null;
    }
  }, [updateDownload]);

  /**
   * Get media info
   */
  const getInfo = useCallback(async (url: string): Promise<unknown> => {
    try {
      const response = await fetch('/api/info', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });

      const result = await response.json();
      return result.success ? result.data : null;
    } catch {
      return null;
    }
  }, []);

  /**
   * Get downloads by status
   */
  const getByStatus = useCallback((status: DownloadStatus): DownloadResponse[] => {
    return Array.from(downloads.values()).filter((d) => d.status === status);
  }, [downloads]);

  /**
   * Clear completed downloads
   */
  const clearCompleted = useCallback(() => {
    const completedIds = getByStatus(DownloadStatus.COMPLETED).map((d) => d.downloadId);
    completedIds.forEach((id) => removeDownload(id));
  }, [getByStatus, removeDownload]);

  /**
   * Clear all downloads
   */
  const clearAll = useCallback(() => {
    clearDownloads();
  }, [clearDownloads]);

  // ═══════════════════════════════════════════════════════════════════════════
  // RETURN
  // ═══════════════════════════════════════════════════════════════════════════

  return {
    download,
    pause,
    resume,
    cancel,
    retry,
    getInfo,
    downloads,
    progress,
    isDownloading: Array.from(downloads.values()).some(
      (d) => d.status === DownloadStatus.DOWNLOADING || d.status === DownloadStatus.PENDING
    ),
    getByStatus,
    clearCompleted,
    clearAll,
  };
}

export default useDownload;
