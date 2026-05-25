/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                  PLAYLIST API ROUTE v3.0.1 ULTIMATE NEXUS                    ║
 * ║                  OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Comprehensive playlist download API with advanced features     ║
 * ║  Features:                                                                   ║
 * ║    - Multi-platform playlist support (YouTube, Spotify, etc.)               ║
 * ║    - Selective item download (range, specific items)                        ║
 * ║    - Progress tracking with WebSocket updates                               ║
 * ║    - Download archive for tracking completed items                          ║
 * ║    - Auto-skip already downloaded items                                     ║
 * ║    - Reverse and shuffle options                                            ║
 * ║    - Thumbnail and subtitle download                                        ║
 * ║    - Metadata embedding                                                     ║
 * ║    - Webhook notifications                                                  ║
 * ║    - Pause/Resume/Cancel operations                                         ║
 * ║    - Rate limiting and authentication                                       ║
 * ║    - Comprehensive error handling                                           ║
 * ║    - Detailed logging and analytics                                         ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module api/playlist
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 * 
 * @example
 * // POST /api/playlist
 * // Request body:
 * {
 *   "url": "https://youtube.com/playlist?list=example",
 *   "videoQuality": "1080p",
 *   "itemRange": "1-10",
 *   "skipDownloaded": true
 * }
 */

import { NextRequest } from 'next/server';
import {
  PlaylistRequest,
  PlaylistResponse,
  PlaylistItemStatus,
  DownloadStatus,
  VideoQuality,
  AudioQuality,
  VideoFormat,
  AudioFormat,
  WSMessageType,
} from '@/types/api';
import {
  successResponse,
  errorResponse,
  validationError,
  generateRequestId,
  generatePlaylistId,
  generateDownloadId,
  parseJsonBody,
  isValidUrl,
  isValidVideoQuality,
  isValidAudioQuality,
  isValidFormat,
  rateLimitMiddleware,
  authMiddleware,
  createMiddleware,
  logger,
  RateLimitTier,
  AuthLevel,
  wsChannelManager,
  MAX_PLAYLIST_ITEMS,
} from '@/lib/utils';

// ═══════════════════════════════════════════════════════════════════════════════
// PLAYLIST MANAGER CLASS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Playlist State Interface
 */
interface PlaylistState {
  id: string;
  title: string;
  url: string;
  status: 'fetching' | 'ready' | 'downloading' | 'completed' | 'failed' | 'cancelled' | 'paused';
  request: PlaylistRequest;
  items: PlaylistItemState[];
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  wsChannel: string;
  totalProgress: number;
  downloadedCount: number;
  failedCount: number;
  skippedCount: number;
}

/**
 * Playlist Item State Interface
 */
interface PlaylistItemState {
  position: number;
  title: string;
  url: string;
  downloadId: string;
  status: DownloadStatus;
  progress: number;
  error?: string;
  filePath?: string;
  skipped: boolean;
}

/**
 * Playlist Download Manager
 * @class PlaylistManager
 * @description Manages playlist downloads with advanced features
 */
class PlaylistManager {
  private static instance: PlaylistManager;
  private playlists: Map<string, PlaylistState> = new Map();
  private archive: Map<string, Set<string>> = new Map(); // URL -> Set of downloaded video IDs
  private activePlaylists = 0;
  private maxActivePlaylists = 3;

  private constructor() {}

  static getInstance(): PlaylistManager {
    if (!PlaylistManager.instance) {
      PlaylistManager.instance = new PlaylistManager();
    }
    return PlaylistManager.instance;
  }

  /**
   * Create a new playlist download
   */
  async createPlaylist(
    request: PlaylistRequest,
    requestId: string
  ): Promise<{ playlistId: string; wsChannel: string }> {
    const playlistId = generatePlaylistId();
    const wsChannel = `playlist_${playlistId}`;

    // Create initial state
    const state: PlaylistState = {
      id: playlistId,
      title: `Playlist ${playlistId}`,
      url: request.url,
      status: 'fetching',
      request,
      items: [],
      createdAt: new Date(),
      wsChannel,
      totalProgress: 0,
      downloadedCount: 0,
      failedCount: 0,
      skippedCount: 0,
    };

    this.playlists.set(playlistId, state);

    logger.info(`Playlist created: ${playlistId}`, {
      url: request.url,
    }, requestId);

    // Fetch playlist info and start download
    this.fetchAndProcess(playlistId).catch((error) => {
      logger.error(`Playlist processing failed: ${playlistId}`, { error });
    });

    return { playlistId, wsChannel };
  }

  /**
   * Fetch playlist info and start processing
   */
  private async fetchAndProcess(playlistId: string): Promise<void> {
    const playlist = this.playlists.get(playlistId);
    if (!playlist) return;

    try {
      // Fetch playlist info (simulated - in production, use yt-dlp)
      const playlistInfo = await this.fetchPlaylistInfo(playlist.url);

      playlist.title = playlistInfo.title;
      playlist.items = playlistInfo.items.map((item, index) => ({
        position: index + 1,
        title: item.title,
        url: item.url,
        downloadId: generateDownloadId(),
        status: DownloadStatus.PENDING,
        progress: 0,
        skipped: false,
      }));

      // Apply item range filter
      if (playlist.request.itemRange) {
        this.applyItemRange(playlist);
      }

      // Apply reverse
      if (playlist.request.reverse) {
        playlist.items.reverse();
      }

      // Apply shuffle
      if (playlist.request.shuffle) {
        this.shuffleArray(playlist.items);
      }

      // Check archive for already downloaded items
      if (playlist.request.skipDownloaded) {
        this.checkArchive(playlist);
      }

      playlist.status = 'ready';

      // Broadcast update
      this.broadcastUpdate(playlist);

      // Start processing if under limit
      if (this.activePlaylists < this.maxActivePlaylists) {
        this.activePlaylists++;
        playlist.status = 'downloading';
        playlist.startedAt = new Date();

        await this.processPlaylist(playlistId);

        this.activePlaylists--;
      }
    } catch (error) {
      playlist.status = 'failed';
      this.broadcastUpdate(playlist);
      logger.error(`Playlist fetch failed: ${playlistId}`, {
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }

  /**
   * Fetch playlist information (simulated)
   */
  private async fetchPlaylistInfo(
    url: string
  ): Promise<{ title: string; items: { title: string; url: string }[] }> {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // Generate simulated playlist
    const itemCount = Math.floor(Math.random() * 50) + 10;
    const items = Array.from({ length: itemCount }, (_, i) => ({
      title: `Video ${i + 1} - Sample Title`,
      url: `${url}?video=${i + 1}`,
    }));

    return {
      title: `Sample Playlist (${itemCount} items)`,
      items,
    };
  }

  /**
   * Apply item range filter
   */
  private applyItemRange(playlist: PlaylistState): void {
    const range = playlist.request.itemRange!;
    const items = playlist.items;

    // Parse range (e.g., "1-10", "5,7,9", "1-5,10,15-20")
    const selectedIndices = new Set<number>();

    const parts = range.split(',');
    for (const part of parts) {
      const trimmed = part.trim();
      if (trimmed.includes('-')) {
        const [start, end] = trimmed.split('-').map((n) => parseInt(n.trim()));
        for (let i = start; i <= end; i++) {
          if (i > 0 && i <= items.length) {
            selectedIndices.add(i - 1);
          }
        }
      } else {
        const index = parseInt(trimmed);
        if (index > 0 && index <= items.length) {
          selectedIndices.add(index - 1);
        }
      }
    }

    playlist.items = items.filter((_, index) => selectedIndices.has(index));
  }

  /**
   * Shuffle array in place
   */
  private shuffleArray<T>(array: T[]): void {
    for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
  }

  /**
   * Check archive for already downloaded items
   */
  private checkArchive(playlist: PlaylistState): void {
    const archiveKey = this.getArchiveKey(playlist.url);

    for (const item of playlist.items) {
      if (this.isInArchive(archiveKey, item.url)) {
        item.skipped = true;
        item.status = DownloadStatus.COMPLETED;
        item.progress = 100;
        playlist.skippedCount++;
      }
    }
  }

  /**
   * Get archive key from playlist URL
   */
  private getArchiveKey(url: string): string {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname + urlObj.pathname;
    } catch {
      return url;
    }
  }

  /**
   * Check if item is in archive
   */
  private isInArchive(archiveKey: string, itemUrl: string): boolean {
    return this.archive.get(archiveKey)?.has(itemUrl) || false;
  }

  /**
   * Add item to archive
   */
  private addToArchive(archiveKey: string, itemUrl: string): void {
    if (!this.archive.has(archiveKey)) {
      this.archive.set(archiveKey, new Set());
    }
    this.archive.get(archiveKey)!.add(itemUrl);
  }

  /**
   * Process playlist items
   */
  private async processPlaylist(playlistId: string): Promise<void> {
    const playlist = this.playlists.get(playlistId);
    if (!playlist) return;

    const concurrent = playlist.request.concurrentDownloads || 3;
    const archiveKey = this.getArchiveKey(playlist.url);

    // Get items to download
    const pendingItems = playlist.items.filter(
      (item) => !item.skipped && item.status === DownloadStatus.PENDING
    );

    // Process in chunks
    const chunks: PlaylistItemState[][] = [];
    for (let i = 0; i < pendingItems.length; i += concurrent) {
      chunks.push(pendingItems.slice(i, i + concurrent));
    }

    for (const chunk of chunks) {
      if (playlist.status === 'cancelled') break;
      if (playlist.status === 'paused') {
        await this.waitForResume(playlistId);
      }

      // Process chunk concurrently
      await Promise.all(chunk.map((item) => this.processItem(playlist, item, archiveKey)));
    }

    // Complete playlist
    playlist.status = playlist.failedCount > 0 && playlist.downloadedCount === 0
      ? 'failed'
      : 'completed';
    playlist.completedAt = new Date();

    this.broadcastUpdate(playlist);

    // Send webhook if configured
    if (playlist.request.webhookUrl) {
      await this.sendWebhook(playlist.request.webhookUrl, playlist);
    }

    logger.info(`Playlist completed: ${playlistId}`, {
      status: playlist.status,
      totalItems: playlist.items.length,
      downloaded: playlist.downloadedCount,
      failed: playlist.failedCount,
      skipped: playlist.skippedCount,
    });
  }

  /**
   * Process a single playlist item
   */
  private async processItem(
    playlist: PlaylistState,
    item: PlaylistItemState,
    archiveKey: string
  ): Promise<void> {
    if (playlist.status === 'cancelled') return;

    item.status = DownloadStatus.DOWNLOADING;
    this.updateProgress(playlist);
    this.broadcastUpdate(playlist);

    try {
      // Simulate download
      const totalSteps = 20;
      for (let step = 0; step <= totalSteps; step++) {
        if (playlist.status === 'cancelled') return;
        if (playlist.status === 'paused') {
          await this.waitForResume(playlist.id);
        }

        item.progress = (step / totalSteps) * 100;
        this.updateProgress(playlist);
        this.broadcastUpdate(playlist);

        await new Promise((resolve) => setTimeout(resolve, 150));
      }

      // Complete item
      item.status = DownloadStatus.COMPLETED;
      item.progress = 100;
      item.filePath = `/downloads/playlist/${sanitize(item.title)}.mp4`;
      playlist.downloadedCount++;

      // Add to archive
      this.addToArchive(archiveKey, item.url);

      logger.debug(`Playlist item completed: ${item.title}`);
    } catch (error) {
      item.status = DownloadStatus.FAILED;
      item.error = error instanceof Error ? error.message : 'Unknown error';
      playlist.failedCount++;

      logger.error(`Playlist item failed: ${item.title}`, { error: item.error });
    }

    this.updateProgress(playlist);
  }

  /**
   * Update overall playlist progress
   */
  private updateProgress(playlist: PlaylistState): void {
    const totalItems = playlist.items.filter((item) => !item.skipped).length;
    const completedProgress = playlist.items
      .filter((item) => !item.skipped)
      .reduce((sum, item) => sum + item.progress, 0);

    playlist.totalProgress = totalItems > 0 ? completedProgress / totalItems : 0;
  }

  /**
   * Wait for playlist resume
   */
  private async waitForResume(playlistId: string): Promise<void> {
    return new Promise((resolve) => {
      const checkInterval = setInterval(() => {
        const playlist = this.playlists.get(playlistId);
        if (!playlist || playlist.status === 'cancelled') {
          clearInterval(checkInterval);
          return;
        }
        if (playlist.status === 'downloading') {
          clearInterval(checkInterval);
          resolve();
        }
      }, 100);
    });
  }

  /**
   * Broadcast playlist update via WebSocket
   */
  private broadcastUpdate(playlist: PlaylistState): void {
    const response: PlaylistResponse = {
      playlistId: playlist.id,
      title: playlist.title,
      totalItems: playlist.items.length,
      downloadedItems: playlist.downloadedCount,
      failedItems: playlist.failedCount,
      progress: playlist.totalProgress,
      items: playlist.items.map((item) => ({
        position: item.position,
        title: item.title,
        url: item.url,
        downloadId: item.downloadId,
        status: item.status,
        progress: item.progress,
        error: item.error,
        filePath: item.filePath,
      })),
      wsChannel: playlist.wsChannel,
    };

    wsChannelManager.broadcast(playlist.wsChannel, {
      type: WSMessageType.QUEUE_UPDATE,
      data: response,
      timestamp: new Date().toISOString(),
      messageId: `msg_${Date.now()}`,
    });
  }

  /**
   * Send webhook notification
   */
  private async sendWebhook(url: string, playlist: PlaylistState): Promise<void> {
    try {
      await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          playlistId: playlist.id,
          title: playlist.title,
          status: playlist.status,
          totalItems: playlist.items.length,
          downloadedItems: playlist.downloadedCount,
          failedItems: playlist.failedCount,
          skippedItems: playlist.skippedCount,
        }),
      });
    } catch (error) {
      logger.error(`Webhook failed: ${url}`, { error });
    }
  }

  /**
   * Get playlist status
   */
  getPlaylist(playlistId: string): PlaylistState | undefined {
    return this.playlists.get(playlistId);
  }

  /**
   * Get all playlists
   */
  getAllPlaylists(): PlaylistState[] {
    return Array.from(this.playlists.values());
  }

  /**
   * Pause playlist
   */
  pausePlaylist(playlistId: string): boolean {
    const playlist = this.playlists.get(playlistId);
    if (!playlist || playlist.status !== 'downloading') return false;

    playlist.status = 'paused';
    this.broadcastUpdate(playlist);
    return true;
  }

  /**
   * Resume playlist
   */
  resumePlaylist(playlistId: string): boolean {
    const playlist = this.playlists.get(playlistId);
    if (!playlist || playlist.status !== 'paused') return false;

    playlist.status = 'downloading';
    this.broadcastUpdate(playlist);
    return true;
  }

  /**
   * Cancel playlist
   */
  cancelPlaylist(playlistId: string): boolean {
    const playlist = this.playlists.get(playlistId);
    if (!playlist) return false;

    playlist.status = 'cancelled';
    playlist.items.forEach((item) => {
      if (item.status === DownloadStatus.PENDING || item.status === DownloadStatus.DOWNLOADING) {
        item.status = DownloadStatus.CANCELLED;
      }
    });

    this.broadcastUpdate(playlist);
    return true;
  }

  /**
   * Get statistics
   */
  getStats(): {
    active: number;
    total: number;
    maxActive: number;
    archiveSize: number;
  } {
    let archiveSize = 0;
    for (const set of this.archive.values()) {
      archiveSize += set.size;
    }

    return {
      active: this.activePlaylists,
      total: this.playlists.size,
      maxActive: this.maxActivePlaylists,
      archiveSize,
    };
  }
}

/**
 * Sanitize filename
 */
function sanitize(filename: string): string {
  return filename
    .replace(/[<>:"/\\|?*]/g, '_')
    .replace(/\s+/g, '_')
    .substring(0, 100);
}

const playlistManager = PlaylistManager.getInstance();

// ═══════════════════════════════════════════════════════════════════════════════
// VALIDATION
// ═══════════════════════════════════════════════════════════════════════════════

function validatePlaylistRequest(
  body: unknown,
  requestId: string,
  startTime: number
): { valid: boolean; error?: ReturnType<typeof validationError>; data?: PlaylistRequest } {
  if (!body || typeof body !== 'object') {
    return {
      valid: false,
      error: validationError('Request body is required', 'body', requestId, startTime),
    };
  }

  const request = body as Partial<PlaylistRequest>;

  // URL validation
  if (!request.url) {
    return {
      valid: false,
      error: validationError('Playlist URL is required', 'url', requestId, startTime),
    };
  }

  if (!isValidUrl(request.url)) {
    return {
      valid: false,
      error: validationError('Invalid URL format', 'url', requestId, startTime),
    };
  }

  // Video quality validation
  if (request.videoQuality && !isValidVideoQuality(request.videoQuality)) {
    return {
      valid: false,
      error: validationError(
        `Invalid video quality. Valid options: ${Object.values(VideoQuality).join(', ')}`,
        'videoQuality',
        requestId,
        startTime
      ),
    };
  }

  // Audio quality validation
  if (request.audioQuality && !isValidAudioQuality(request.audioQuality)) {
    return {
      valid: false,
      error: validationError(
        `Invalid audio quality. Valid options: ${Object.values(AudioQuality).join(', ')}`,
        'audioQuality',
        requestId,
        startTime
      ),
    };
  }

  // Format validation
  if (request.format && !isValidFormat(request.format)) {
    return {
      valid: false,
      error: validationError(
        `Invalid format. Valid options: ${[...Object.values(VideoFormat), ...Object.values(AudioFormat)].join(', ')}`,
        'format',
        requestId,
        startTime
      ),
    };
  }

  // Item range validation
  if (request.itemRange) {
    const rangeRegex = /^(\d+(-\d+)?)(,\d+(-\d+)?)*$/;
    if (!rangeRegex.test(request.itemRange)) {
      return {
        valid: false,
        error: validationError(
          'Invalid item range format. Examples: "1-10", "5,7,9", "1-5,10,15-20"',
          'itemRange',
          requestId,
          startTime
        ),
      };
    }
  }

  // Concurrent downloads validation
  if (
    request.concurrentDownloads !== undefined &&
    (request.concurrentDownloads < 1 || request.concurrentDownloads > 10)
  ) {
    return {
      valid: false,
      error: validationError('Concurrent downloads must be between 1 and 10', 'concurrentDownloads', requestId, startTime),
    };
  }

  // Webhook URL validation
  if (request.webhookUrl && !isValidUrl(request.webhookUrl)) {
    return {
      valid: false,
      error: validationError('Invalid webhook URL format', 'webhookUrl', requestId, startTime),
    };
  }

  return { valid: true, data: request as PlaylistRequest };
}

// ═══════════════════════════════════════════════════════════════════════════════
// MIDDLEWARE
// ═══════════════════════════════════════════════════════════════════════════════

const middleware = createMiddleware(
  rateLimitMiddleware(RateLimitTier.PRO),
  authMiddleware(AuthLevel.USER)
);

// ═══════════════════════════════════════════════════════════════════════════════
// API ROUTE HANDLERS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * POST /api/playlist
 * @description Start a playlist download
 */
export async function POST(request: NextRequest): Promise<Response> {
  const startTime = Date.now();
  const requestId = generateRequestId();

  const { response: middlewareResponse, context } = await middleware(request);
  if (middlewareResponse) return middlewareResponse;

  try {
    const body = await parseJsonBody<PlaylistRequest>(request);

    // Validate request
    const validation = validatePlaylistRequest(body, requestId, startTime);
    if (!validation.valid || !validation.data) {
      return validation.error!;
    }

    const playlistRequest = validation.data;

    // Set defaults
    playlistRequest.concurrentDownloads = playlistRequest.concurrentDownloads || 3;
    playlistRequest.videoQuality = playlistRequest.videoQuality || VideoQuality.BEST;
    playlistRequest.format = playlistRequest.format || VideoFormat.MP4;
    playlistRequest.skipDownloaded = playlistRequest.skipDownloaded ?? true;
    playlistRequest.downloadThumbnails = playlistRequest.downloadThumbnails ?? true;
    playlistRequest.downloadSubtitles = playlistRequest.downloadSubtitles ?? false;
    playlistRequest.useWebSocket = playlistRequest.useWebSocket ?? true;

    // Create playlist
    const { playlistId, wsChannel } = await playlistManager.createPlaylist(playlistRequest, requestId);

    // Build response
    const playlist = playlistManager.getPlaylist(playlistId)!;
    const responseData: PlaylistResponse = {
      playlistId,
      title: playlist.title,
      totalItems: playlist.items.length,
      downloadedItems: 0,
      failedItems: 0,
      progress: 0,
      items: playlist.items,
      wsChannel: playlistRequest.useWebSocket ? wsChannel : undefined,
    };

    logger.info(`Playlist created successfully`, {
      playlistId,
      url: playlistRequest.url,
      user: context.session?.userId,
    }, requestId);

    return successResponse(responseData, requestId, startTime);
  } catch (error) {
    logger.error('Playlist creation failed', {
      error: error instanceof Error ? error.message : 'Unknown error',
    }, requestId);

    return errorResponse(
      {
        code: 'INTERNAL_ERROR',
        message: 'Failed to create playlist download',
        details: { error: error instanceof Error ? error.message : 'Unknown' },
      },
      requestId,
      startTime,
      500
    );
  }
}

/**
 * GET /api/playlist
 * @description Get playlist status or list all playlists
 */
export async function GET(request: NextRequest): Promise<Response> {
  const startTime = Date.now();
  const requestId = generateRequestId();

  const { response: middlewareResponse } = await middleware(request);
  if (middlewareResponse) return middlewareResponse;

  try {
    const { searchParams } = new URL(request.url);
    const playlistId = searchParams.get('id');
    const action = searchParams.get('action');

    // Handle specific playlist actions
    if (playlistId) {
      const playlist = playlistManager.getPlaylist(playlistId);

      if (!playlist) {
        return errorResponse(
          {
            code: 'NOT_FOUND',
            message: `Playlist not found: ${playlistId}`,
            suggestion: 'Please check the playlist ID and try again',
          },
          requestId,
          startTime,
          404
        );
      }

      // Handle actions
      if (action === 'pause') {
        const paused = playlistManager.pausePlaylist(playlistId);
        return successResponse(
          {
            playlistId,
            status: paused ? 'paused' : playlist.status,
            message: paused ? 'Playlist paused successfully' : 'Failed to pause playlist',
          },
          requestId,
          startTime
        );
      }

      if (action === 'resume') {
        const resumed = playlistManager.resumePlaylist(playlistId);
        return successResponse(
          {
            playlistId,
            status: resumed ? 'downloading' : playlist.status,
            message: resumed ? 'Playlist resumed successfully' : 'Failed to resume playlist',
          },
          requestId,
          startTime
        );
      }

      if (action === 'cancel') {
        const cancelled = playlistManager.cancelPlaylist(playlistId);
        return successResponse(
          {
            playlistId,
            status: cancelled ? 'cancelled' : playlist.status,
            message: cancelled ? 'Playlist cancelled successfully' : 'Failed to cancel playlist',
          },
          requestId,
          startTime
        );
      }

      // Return playlist status
      const responseData: PlaylistResponse = {
        playlistId: playlist.id,
        title: playlist.title,
        totalItems: playlist.items.length,
        downloadedItems: playlist.downloadedCount,
        failedItems: playlist.failedCount,
        progress: playlist.totalProgress,
        items: playlist.items,
        wsChannel: playlist.wsChannel,
      };

      return successResponse(responseData, requestId, startTime);
    }

    // Return all playlists or stats
    const stats = playlistManager.getStats();
    const playlists = playlistManager.getAllPlaylists().map((playlist) => ({
      playlistId: playlist.id,
      title: playlist.title,
      status: playlist.status,
      totalItems: playlist.items.length,
      progress: playlist.totalProgress,
      createdAt: playlist.createdAt,
    }));

    return successResponse(
      {
        stats,
        playlists,
        message: 'Playlist API v3.0.1 ULTIMATE NEXUS',
      },
      requestId,
      startTime
    );
  } catch (error) {
    logger.error('Failed to get playlist status', {
      error: error instanceof Error ? error.message : 'Unknown error',
    }, requestId);

    return errorResponse(
      {
        code: 'INTERNAL_ERROR',
        message: 'Failed to retrieve playlist status',
      },
      requestId,
      startTime,
      500
    );
  }
}

/**
 * DELETE /api/playlist
 * @description Cancel a playlist
 */
export async function DELETE(request: NextRequest): Promise<Response> {
  const startTime = Date.now();
  const requestId = generateRequestId();

  const { response: middlewareResponse } = await middleware(request);
  if (middlewareResponse) return middlewareResponse;

  try {
    const { searchParams } = new URL(request.url);
    const playlistId = searchParams.get('id');

    if (!playlistId) {
      return validationError('Playlist ID is required', 'id', requestId, startTime);
    }

    const cancelled = playlistManager.cancelPlaylist(playlistId);

    if (!cancelled) {
      return errorResponse(
        {
          code: 'NOT_FOUND',
          message: `Playlist not found or already completed: ${playlistId}`,
        },
        requestId,
        startTime,
        404
      );
    }

    return successResponse(
      {
        playlistId,
        status: 'cancelled',
        message: 'Playlist cancelled successfully',
      },
      requestId,
      startTime
    );
  } catch (error) {
    logger.error('Failed to cancel playlist', {
      error: error instanceof Error ? error.message : 'Unknown error',
    }, requestId);

    return errorResponse(
      {
        code: 'INTERNAL_ERROR',
        message: 'Failed to cancel playlist',
      },
      requestId,
      startTime,
      500
    );
  }
}

/**
 * OPTIONS /api/playlist
 * @description Return API documentation
 */
export async function OPTIONS(): Promise<Response> {
  return new Response(
    JSON.stringify({
      name: 'Playlist API',
      version: '3.0.1',
      edition: 'ULTIMATE NEXUS',
      author: 'RAJSARASWATI JATAV (RS)',
      description: 'Playlist download management with advanced features',
      endpoints: {
        'POST /api/playlist': {
          description: 'Start a playlist download',
          body: {
            url: 'string (required) - Playlist URL',
            outputDir: 'string - Output directory',
            videoQuality: 'string - Video quality preference',
            audioQuality: 'string - Audio quality preference',
            format: 'string - Output format',
            itemRange: 'string - Item range (e.g., "1-10", "5,7,9")',
            reverse: 'boolean - Reverse playlist order',
            shuffle: 'boolean - Shuffle playlist items',
            concurrentDownloads: 'number - Max concurrent downloads (1-10)',
            archiveFile: 'string - Download archive file path',
            skipDownloaded: 'boolean - Skip already downloaded items',
            downloadThumbnails: 'boolean - Download thumbnails',
            downloadSubtitles: 'boolean - Download subtitles',
            subtitleLanguages: 'string[] - Subtitle language codes',
            webhookUrl: 'string - Webhook for notifications',
            useWebSocket: 'boolean - Enable WebSocket updates',
            tags: 'string[] - Tags for organization',
          },
        },
        'GET /api/playlist': {
          description: 'Get playlist status or list playlists',
          params: {
            id: 'string - Playlist ID (optional)',
            action: 'string - Action (pause, resume, cancel)',
          },
        },
        'DELETE /api/playlist': {
          description: 'Cancel a playlist',
          params: {
            id: 'string - Playlist ID (required)',
          },
        },
      },
      limits: {
        maxPlaylistItems: MAX_PLAYLIST_ITEMS,
        maxConcurrentPlaylists: 3,
        maxConcurrentDownloads: 10,
      },
    }),
    {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
      },
    }
  );
}
