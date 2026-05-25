/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   API UTILITIES v3.0.1 ULTIMATE NEXUS                         ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Comprehensive utilities for API routes                         ║
 * ║  Features: Logging, Rate Limiting, Auth, Validation, Error Handling          ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module lib/utils
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

import { NextRequest, NextResponse } from 'next/server';
import { v4 as uuidv4 } from 'uuid';
import {
  ApiResponse,
  ApiError,
  RateLimitInfo,
  RateLimitConfig,
  UserSession,
  AuthLevel,
  RateLimitTier,
  LogEntry,
} from '@/types/api';

// ═══════════════════════════════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════════════════════════════

export const API_VERSION = '3.0.1';
export const API_NAME = 'ULTIMATE NEXUS API';
export const DEFAULT_TIMEOUT = 30000;
export const MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024; // 10GB
export const MAX_BATCH_SIZE = 100;
export const MAX_PLAYLIST_ITEMS = 1000;

// Rate limit configurations per tier
export const RATE_LIMIT_TIERS: Record<RateLimitTier, RateLimitConfig> = {
  [RateLimitTier.FREE]: { windowMs: 60000, maxRequests: 10 },
  [RateLimitTier.BASIC]: { windowMs: 60000, maxRequests: 30 },
  [RateLimitTier.PRO]: { windowMs: 60000, maxRequests: 100 },
  [RateLimitTier.ENTERPRISE]: { windowMs: 60000, maxRequests: 1000 },
};

// ═══════════════════════════════════════════════════════════════════════════════
// LOGGER CLASS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Advanced logging system with multiple transports
 * @class Logger
 */
export class Logger {
  private static instance: Logger;
  private logs: LogEntry[] = [];
  private maxLogs = 10000;

  private constructor() {}

  static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  /**
   * Log a debug message
   */
  debug(message: string, data?: Record<string, unknown>, requestId?: string): void {
    this.log('debug', message, data, requestId);
  }

  /**
   * Log an info message
   */
  info(message: string, data?: Record<string, unknown>, requestId?: string): void {
    this.log('info', message, data, requestId);
  }

  /**
   * Log a warning message
   */
  warn(message: string, data?: Record<string, unknown>, requestId?: string): void {
    this.log('warn', message, data, requestId);
  }

  /**
   * Log an error message
   */
  error(message: string, data?: Record<string, unknown>, requestId?: string, stack?: string): void {
    this.log('error', message, data, requestId, stack);
  }

  /**
   * Log a critical message
   */
  critical(message: string, data?: Record<string, unknown>, requestId?: string, stack?: string): void {
    this.log('critical', message, data, requestId, stack);
  }

  private log(
    level: LogEntry['level'],
    message: string,
    data?: Record<string, unknown>,
    requestId?: string,
    stack?: string
  ): void {
    const entry: LogEntry = {
      level,
      message,
      timestamp: new Date().toISOString(),
      requestId,
      data,
      stack,
    };

    this.logs.push(entry);

    // Trim logs if exceeding max
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs);
    }

    // Console output
    const logMethod = level === 'critical' ? 'error' : level;
    console[logMethod](`[${entry.timestamp}] [${level.toUpperCase()}] ${requestId ? `[${requestId}] ` : ''}${message}`, data || '');
  }

  /**
   * Get logs filtered by level
   */
  getLogs(level?: LogEntry['level']): LogEntry[] {
    if (level) {
      return this.logs.filter((log) => log.level === level);
    }
    return [...this.logs];
  }

  /**
   * Get logs for a specific request
   */
  getRequestLogs(requestId: string): LogEntry[] {
    return this.logs.filter((log) => log.requestId === requestId);
  }

  /**
   * Clear all logs
   */
  clear(): void {
    this.logs = [];
  }
}

export const logger = Logger.getInstance();

// ═══════════════════════════════════════════════════════════════════════════════
// RESPONSE HELPERS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Create a successful API response
 * @param data Response data
 * @param requestId Request identifier
 * @param startTime Request start time for processing time calculation
 */
export function successResponse<T>(
  data: T,
  requestId: string,
  startTime: number
): NextResponse<ApiResponse<T>> {
  const response: ApiResponse<T> = {
    success: true,
    data,
    requestId,
    timestamp: new Date().toISOString(),
    processingTime: Date.now() - startTime,
    version: API_VERSION,
  };

  return NextResponse.json(response, { status: 200 });
}

/**
 * Create an error API response
 * @param error Error details
 * @param requestId Request identifier
 * @param startTime Request start time
 * @param statusCode HTTP status code
 */
export function errorResponse(
  error: ApiError,
  requestId: string,
  startTime: number,
  statusCode: number = 400
): NextResponse<ApiResponse> {
  const response: ApiResponse = {
    success: false,
    error,
    requestId,
    timestamp: new Date().toISOString(),
    processingTime: Date.now() - startTime,
    version: API_VERSION,
  };

  logger.error(error.message, { code: error.code, details: error.details }, requestId);

  return NextResponse.json(response, { status: statusCode });
}

/**
 * Create a validation error response
 */
export function validationError(
  message: string,
  field: string,
  requestId: string,
  startTime: number
): NextResponse<ApiResponse> {
  return errorResponse(
    {
      code: 'VALIDATION_ERROR',
      message,
      details: { field },
      suggestion: `Please provide a valid value for '${field}'`,
    },
    requestId,
    startTime,
    400
  );
}

/**
 * Create an unauthorized error response
 */
export function unauthorizedError(
  requestId: string,
  startTime: number
): NextResponse<ApiResponse> {
  return errorResponse(
    {
      code: 'UNAUTHORIZED',
      message: 'Authentication required',
      suggestion: 'Please provide a valid API key or token',
    },
    requestId,
    startTime,
    401
  );
}

/**
 * Create a rate limit exceeded response
 */
export function rateLimitError(
  requestId: string,
  startTime: number,
  retryAfter: number
): NextResponse<ApiResponse> {
  const response = errorResponse(
    {
      code: 'RATE_LIMIT_EXCEEDED',
      message: 'Rate limit exceeded',
      details: { retryAfter },
      suggestion: `Please retry after ${retryAfter} seconds`,
    },
    requestId,
    startTime,
    429
  );

  response.headers.set('Retry-After', String(retryAfter));
  return response;
}

// ═══════════════════════════════════════════════════════════════════════════════
// REQUEST UTILITIES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Generate a unique request ID
 */
export function generateRequestId(): string {
  return `req_${uuidv4().replace(/-/g, '').substring(0, 16)}`;
}

/**
 * Generate a unique download ID
 */
export function generateDownloadId(): string {
  return `dl_${uuidv4().replace(/-/g, '').substring(0, 16)}`;
}

/**
 * Generate a unique batch ID
 */
export function generateBatchId(): string {
  return `batch_${uuidv4().replace(/-/g, '').substring(0, 12)}`;
}

/**
 * Generate a unique playlist ID
 */
export function generatePlaylistId(): string {
  return `pl_${uuidv4().replace(/-/g, '').substring(0, 12)}`;
}

/**
 * Parse JSON body from request with error handling
 */
export async function parseJsonBody<T>(request: NextRequest): Promise<T | null> {
  try {
    const text = await request.text();
    if (!text) return null;
    return JSON.parse(text) as T;
  } catch (error) {
    return null;
  }
}

/**
 * Get client IP address from request
 */
export function getClientIp(request: NextRequest): string {
  const forwarded = request.headers.get('x-forwarded-for');
  if (forwarded) {
    return forwarded.split(',')[0].trim();
  }
  const realIp = request.headers.get('x-real-ip');
  if (realIp) {
    return realIp;
  }
  return 'unknown';
}

/**
 * Get user agent from request
 */
export function getUserAgent(request: NextRequest): string {
  return request.headers.get('user-agent') || 'unknown';
}

// ═══════════════════════════════════════════════════════════════════════════════
// VALIDATION UTILITIES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Validate URL format
 */
export function isValidUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return ['http:', 'https:'].includes(parsed.protocol);
  } catch {
    return false;
  }
}

/**
 * Validate file path (prevent directory traversal)
 */
export function isValidFilePath(path: string): boolean {
  // Prevent directory traversal
  if (path.includes('..')) return false;
  // Prevent absolute paths outside allowed directories
  if (path.startsWith('/') && !path.startsWith('/downloads')) return false;
  return true;
}

/**
 * Validate video quality
 */
export function isValidVideoQuality(quality: string): boolean {
  const validQualities = ['2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p', 'audio', 'best', 'worst'];
  return validQualities.includes(quality);
}

/**
 * Validate audio quality
 */
export function isValidAudioQuality(quality: string): boolean {
  const validQualities = ['flac', '320kbps', '192kbps', '128kbps', '64kbps'];
  return validQualities.includes(quality);
}

/**
 * Validate format
 */
export function isValidFormat(format: string): boolean {
  const validFormats = ['mp4', 'webm', 'mkv', 'avi', 'mov', 'flv', 'mp3', 'aac', 'ogg', 'flac', 'wav', 'm4a', 'opus'];
  return validFormats.includes(format.toLowerCase());
}

/**
 * Sanitize filename
 */
export function sanitizeFilename(filename: string): string {
  return filename
    .replace(/[<>:"/\\|?*]/g, '_')
    .replace(/\s+/g, '_')
    .substring(0, 255);
}

// ═══════════════════════════════════════════════════════════════════════════════
// RATE LIMITER CLASS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * In-memory rate limiter
 * @class RateLimiter
 */
export class RateLimiter {
  private static instance: RateLimiter;
  private requests: Map<string, number[]> = new Map();
  private cleanupInterval: NodeJS.Timeout;

  private constructor() {
    // Cleanup old entries every minute
    this.cleanupInterval = setInterval(() => this.cleanup(), 60000);
  }

  static getInstance(): RateLimiter {
    if (!RateLimiter.instance) {
      RateLimiter.instance = new RateLimiter();
    }
    return RateLimiter.instance;
  }

  /**
   * Check if request is allowed under rate limit
   */
  check(key: string, config: RateLimitConfig): RateLimitInfo {
    const now = Date.now();
    const windowStart = now - config.windowMs;

    // Get existing requests
    let requests = this.requests.get(key) || [];

    // Filter to current window
    requests = requests.filter((timestamp) => timestamp > windowStart);

    // Check limit
    const remaining = Math.max(0, config.maxRequests - requests.length);
    const limited = requests.length >= config.maxRequests;

    // Add current request if not limited
    if (!limited) {
      requests.push(now);
      this.requests.set(key, requests);
    }

    // Calculate reset time
    const oldestRequest = requests.length > 0 ? Math.min(...requests) : now;
    const resetAt = new Date(oldestRequest + config.windowMs);

    return {
      limit: config.maxRequests,
      remaining: limited ? 0 : remaining - 1,
      resetAt,
      retryAfter: limited ? Math.ceil((oldestRequest + config.windowMs - now) / 1000) : undefined,
    };
  }

  /**
   * Clear rate limit for a key
   */
  clear(key: string): void {
    this.requests.delete(key);
  }

  /**
   * Cleanup old entries
   */
  private cleanup(): void {
    const now = Date.now();
    for (const [key, timestamps] of this.requests.entries()) {
      const filtered = timestamps.filter((t) => now - t < 3600000); // Keep 1 hour
      if (filtered.length === 0) {
        this.requests.delete(key);
      } else {
        this.requests.set(key, filtered);
      }
    }
  }

  /**
   * Destroy the rate limiter
   */
  destroy(): void {
    clearInterval(this.cleanupInterval);
    this.requests.clear();
  }
}

export const rateLimiter = RateLimiter.getInstance();

// ═══════════════════════════════════════════════════════════════════════════════
// AUTHENTICATION
// ═══════════════════════════════════════════════════════════════════════════════

// Mock user store (in production, use a database)
const userStore: Map<string, UserSession> = new Map();

/**
 * Authenticate request
 * @returns User session if authenticated, null otherwise
 */
export async function authenticateRequest(request: NextRequest): Promise<UserSession | null> {
  // Check for API key
  const apiKey = request.headers.get('x-api-key');
  if (apiKey) {
    // Validate API key (in production, check against database)
    if (apiKey.startsWith('sk_live_') || apiKey.startsWith('sk_test_')) {
      // Mock session
      const session: UserSession = {
        sessionId: uuidv4(),
        userId: `user_${apiKey.substring(8, 16)}`,
        role: apiKey.startsWith('sk_live_') ? AuthLevel.USER : AuthLevel.USER,
        tier: apiKey.includes('pro') ? RateLimitTier.PRO : RateLimitTier.BASIC,
        createdAt: new Date(),
        expiresAt: new Date(Date.now() + 3600000), // 1 hour
        lastActivity: new Date(),
        ipAddress: getClientIp(request),
        userAgent: getUserAgent(request),
      };
      userStore.set(session.sessionId, session);
      return session;
    }
  }

  // Check for Bearer token
  const authHeader = request.headers.get('authorization');
  if (authHeader?.startsWith('Bearer ')) {
    const token = authHeader.substring(7);
    // Validate token (in production, verify JWT)
    if (token.length > 10) {
      const session: UserSession = {
        sessionId: uuidv4(),
        userId: `user_${token.substring(0, 8)}`,
        role: AuthLevel.USER,
        tier: RateLimitTier.BASIC,
        createdAt: new Date(),
        expiresAt: new Date(Date.now() + 3600000),
        lastActivity: new Date(),
        ipAddress: getClientIp(request),
        userAgent: getUserAgent(request),
      };
      userStore.set(session.sessionId, session);
      return session;
    }
  }

  return null;
}

/**
 * Check if user has required permission level
 */
export function hasPermission(session: UserSession | null, requiredLevel: AuthLevel): boolean {
  if (!session) return requiredLevel === AuthLevel.PUBLIC;
  
  const levels = [AuthLevel.PUBLIC, AuthLevel.USER, AuthLevel.ADMIN, AuthLevel.SUPER_ADMIN];
  return levels.indexOf(session.role) >= levels.indexOf(requiredLevel);
}

// ═══════════════════════════════════════════════════════════════════════════════
// MIDDLEWARE FACTORY
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Middleware context
 */
export interface MiddlewareContext {
  requestId: string;
  startTime: number;
  session: UserSession | null;
  clientIp: string;
  userAgent: string;
}

/**
 * Middleware function type
 */
export type MiddlewareFunction = (
  request: NextRequest,
  context: MiddlewareContext
) => Promise<NextResponse | null>;

/**
 * Create middleware chain
 */
export function createMiddleware(
  ...middlewares: MiddlewareFunction[]
): (request: NextRequest) => Promise<{ response: NextResponse | null; context: MiddlewareContext }> {
  return async (request: NextRequest) => {
    const requestId = generateRequestId();
    const startTime = Date.now();
    const clientIp = getClientIp(request);
    const userAgent = getUserAgent(request);

    // Try to authenticate
    const session = await authenticateRequest(request);

    const context: MiddlewareContext = {
      requestId,
      startTime,
      session,
      clientIp,
      userAgent,
    };

    // Log request
    logger.info(`Request started: ${request.method} ${request.nextUrl.pathname}`, {
      clientIp,
      userAgent,
      authenticated: !!session,
    }, requestId);

    // Run middlewares
    for (const middleware of middlewares) {
      const response = await middleware(request, context);
      if (response) {
        return { response, context };
      }
    }

    return { response: null, context };
  };
}

/**
 * Rate limiting middleware
 */
export function rateLimitMiddleware(
  tier: RateLimitTier = RateLimitTier.FREE
): MiddlewareFunction {
  return async (request: NextRequest, context: MiddlewareContext) => {
    const config = RATE_LIMIT_TIERS[tier];
    const key = context.session?.userId || context.clientIp;
    const rateLimitInfo = rateLimiter.check(key, config);

    if (rateLimitInfo.remaining === 0) {
      logger.warn(`Rate limit exceeded for ${key}`, {}, context.requestId);
      return rateLimitError(
        context.requestId,
        context.startTime,
        rateLimitInfo.retryAfter || 60
      );
    }

    return null;
  };
}

/**
 * Authentication middleware
 */
export function authMiddleware(
  requiredLevel: AuthLevel = AuthLevel.USER
): MiddlewareFunction {
  return async (request: NextRequest, context: MiddlewareContext) => {
    if (!hasPermission(context.session, requiredLevel)) {
      return unauthorizedError(context.requestId, context.startTime);
    }
    return null;
  };
}

/**
 * Request logging middleware
 */
export function loggingMiddleware(): MiddlewareFunction {
  return async (request: NextRequest, context: MiddlewareContext) => {
    logger.info(`Request completed: ${request.method} ${request.nextUrl.pathname}`, {
      duration: Date.now() - context.startTime,
    }, context.requestId);
    return null;
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// WEBSOCKET HELPERS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * WebSocket channel manager
 * @class WSChannelManager
 */
export class WSChannelManager {
  private static instance: WSChannelManager;
  private channels: Map<string, Set<string>> = new Map(); // channelId -> Set of connectionIds
  private connections: Map<string, WebSocket> = new Map(); // connectionId -> WebSocket

  private constructor() {}

  static getInstance(): WSChannelManager {
    if (!WSChannelManager.instance) {
      WSChannelManager.instance = new WSChannelManager();
    }
    return WSChannelManager.instance;
  }

  /**
   * Subscribe a connection to a channel
   */
  subscribe(channelId: string, connectionId: string, ws: WebSocket): void {
    if (!this.channels.has(channelId)) {
      this.channels.set(channelId, new Set());
    }
    this.channels.get(channelId)!.add(connectionId);
    this.connections.set(connectionId, ws);
  }

  /**
   * Unsubscribe a connection from a channel
   */
  unsubscribe(channelId: string, connectionId: string): void {
    this.channels.get(channelId)?.delete(connectionId);
    this.connections.delete(connectionId);
  }

  /**
   * Broadcast message to all connections in a channel
   */
  broadcast(channelId: string, message: unknown): void {
    const connections = this.channels.get(channelId);
    if (!connections) return;

    const messageStr = JSON.stringify(message);
    for (const connectionId of connections) {
      const ws = this.connections.get(connectionId);
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(messageStr);
      }
    }
  }

  /**
   * Get channel subscriber count
   */
  getSubscriberCount(channelId: string): number {
    return this.channels.get(channelId)?.size || 0;
  }
}

export const wsChannelManager = WSChannelManager.getInstance();

// ═══════════════════════════════════════════════════════════════════════════════
// FILE UTILITIES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Format bytes to human readable string
 */
export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

/**
 * Format duration in seconds to human readable string
 */
export function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Get file extension from URL or filename
 */
export function getFileExtension(urlOrFilename: string): string {
  const pathname = urlOrFilename.split('?')[0];
  const parts = pathname.split('.');
  return parts.length > 1 ? parts.pop()!.toLowerCase() : '';
}

/**
 * Get MIME type from extension
 */
export function getMimeType(extension: string): string {
  const mimeTypes: Record<string, string> = {
    mp4: 'video/mp4',
    webm: 'video/webm',
    mkv: 'video/x-matroska',
    avi: 'video/x-msvideo',
    mov: 'video/quicktime',
    mp3: 'audio/mpeg',
    aac: 'audio/aac',
    ogg: 'audio/ogg',
    flac: 'audio/flac',
    wav: 'audio/wav',
    m4a: 'audio/mp4',
    srt: 'application/x-subrip',
    vtt: 'text/vtt',
    jpg: 'image/jpeg',
    png: 'image/png',
    webp: 'image/webp',
  };
  return mimeTypes[extension.toLowerCase()] || 'application/octet-stream';
}
