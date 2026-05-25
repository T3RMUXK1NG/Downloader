/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    API TYPES v3.0.1 ULTIMATE NEXUS                           ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Comprehensive TypeScript types for API routes                  ║
 * ║  Features: Request/Response types, DTOs, Validation schemas, Error types     ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module types/api
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

// ═══════════════════════════════════════════════════════════════════════════════
// ENUMERATIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Download status enumeration
 * @description Represents all possible states of a download operation
 */
export enum DownloadStatus {
  /** Download is queued and waiting to start */
  PENDING = 'pending',
  /** Download is actively in progress */
  DOWNLOADING = 'downloading',
  /** Download is temporarily paused */
  PAUSED = 'paused',
  /** Download completed successfully */
  COMPLETED = 'completed',
  /** Download failed with an error */
  FAILED = 'failed',
  /** Download was cancelled by user */
  CANCELLED = 'cancelled',
  /** Download is being retried after failure */
  RETRYING = 'retrying',
  /** Download is being validated */
  VALIDATING = 'validating',
  /** Download is being processed (conversion, etc.) */
  PROCESSING = 'processing'
}

/**
 * File type enumeration
 * @description Supported file types for download and processing
 */
export enum FileType {
  VIDEO = 'video',
  AUDIO = 'audio',
  IMAGE = 'image',
  DOCUMENT = 'document',
  ARCHIVE = 'archive',
  SUBTITLE = 'subtitle',
  METADATA = 'metadata',
  THUMBNAIL = 'thumbnail',
  PLAYLIST = 'playlist',
  UNKNOWN = 'unknown'
}

/**
 * Video quality enumeration
 * @description Supported video quality options
 */
export enum VideoQuality {
  Q4K = '2160p',
  Q2K = '1440p',
  Q1080P = '1080p',
  Q720P = '720p',
  Q480P = '480p',
  Q360P = '360p',
  Q240P = '240p',
  Q144P = '144p',
  AUDIO_ONLY = 'audio',
  BEST = 'best',
  WORST = 'worst'
}

/**
 * Audio quality enumeration
 * @description Supported audio quality options
 */
export enum AudioQuality {
  LOSSLESS = 'flac',
  HIGH = '320kbps',
  MEDIUM = '192kbps',
  LOW = '128kbps',
  MINIMUM = '64kbps'
}

/**
 * Audio format enumeration
 * @description Supported audio output formats
 */
export enum AudioFormat {
  MP3 = 'mp3',
  AAC = 'aac',
  OGG = 'ogg',
  FLAC = 'flac',
  WAV = 'wav',
  M4A = 'm4a',
  OPUS = 'opus'
}

/**
 * Video format enumeration
 * @description Supported video output formats
 */
export enum VideoFormat {
  MP4 = 'mp4',
  WEBM = 'webm',
  MKV = 'mkv',
  AVI = 'avi',
  MOV = 'mov',
  FLV = 'flv'
}

/**
 * Batch operation status enumeration
 */
export enum BatchStatus {
  QUEUED = 'queued',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
  PAUSED = 'paused'
}

/**
 * Authentication level enumeration
 */
export enum AuthLevel {
  PUBLIC = 'public',
  USER = 'user',
  ADMIN = 'admin',
  SUPER_ADMIN = 'super_admin'
}

/**
 * Rate limit tier enumeration
 */
export enum RateLimitTier {
  FREE = 'free',
  BASIC = 'basic',
  PRO = 'pro',
  ENTERPRISE = 'enterprise'
}

/**
 * WebSocket message type enumeration
 */
export enum WSMessageType {
  DOWNLOAD_PROGRESS = 'download_progress',
  DOWNLOAD_COMPLETE = 'download_complete',
  DOWNLOAD_ERROR = 'download_error',
  BATCH_PROGRESS = 'batch_progress',
  QUEUE_UPDATE = 'queue_update',
  SYSTEM_ALERT = 'system_alert',
  AUTH_EVENT = 'auth_event',
  HEARTBEAT = 'heartbeat'
}

// ═══════════════════════════════════════════════════════════════════════════════
// INTERFACES - REQUEST TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Base request interface
 * @description Common fields for all API requests
 */
export interface BaseRequest {
  /** Unique request identifier */
  requestId?: string;
  /** Request timestamp */
  timestamp?: Date;
  /** Client version */
  clientVersion?: string;
  /** Additional metadata */
  metadata?: Record<string, unknown>;
}

/**
 * Download request interface
 * @description Request payload for initiating a download
 */
export interface DownloadRequest extends BaseRequest {
  /** URL to download from */
  url: string;
  /** Output filename (optional, auto-generated if not provided) */
  filename?: string;
  /** Output directory path */
  outputDir?: string;
  /** Video quality preference */
  videoQuality?: VideoQuality;
  /** Audio quality preference */
  audioQuality?: AudioQuality;
  /** Output format */
  format?: VideoFormat | AudioFormat;
  /** File type hint */
  fileType?: FileType;
  /** Whether to download subtitles */
  downloadSubtitles?: boolean;
  /** Subtitle language codes (e.g., ['en', 'es']) */
  subtitleLanguages?: string[];
  /** Whether to download thumbnail */
  downloadThumbnail?: boolean;
  /** Whether to embed metadata */
  embedMetadata?: boolean;
  /** Proxy server URL */
  proxy?: string;
  /** Custom headers for the request */
  headers?: Record<string, string>;
  /** Cookies for authentication */
  cookies?: string;
  /** Username for HTTP auth */
  username?: string;
  /** Password for HTTP auth */
  password?: string;
  /** Whether to overwrite existing files */
  overwrite?: boolean;
  /** Maximum download speed in bytes/sec (0 = unlimited) */
  maxSpeed?: number;
  /** Number of retry attempts */
  retries?: number;
  /** Timeout in seconds */
  timeout?: number;
  /** Whether to use WebSocket for progress updates */
  useWebSocket?: boolean;
  /** Webhook URL for completion notification */
  webhookUrl?: string;
  /** Tags for organization */
  tags?: string[];
}

/**
 * File operation request interface
 */
export interface FileRequest extends BaseRequest {
  /** File path or identifier */
  path: string;
  /** Operation to perform */
  operation: 'read' | 'delete' | 'move' | 'copy' | 'rename' | 'info' | 'exists';
  /** Destination path for move/copy operations */
  destination?: string;
  /** New filename for rename operation */
  newName?: string;
  /** Whether to create parent directories */
  createParents?: boolean;
  /** Whether to overwrite existing files */
  overwrite?: boolean;
}

/**
 * Info request interface
 */
export interface InfoRequest extends BaseRequest {
  /** URL to get information about */
  url: string;
  /** Whether to fetch full metadata */
  fullMetadata?: boolean;
  /** Whether to include available formats */
  includeFormats?: boolean;
  /** Whether to include subtitle options */
  includeSubtitles?: boolean;
  /** Whether to include thumbnail info */
  includeThumbnails?: boolean;
  /** Proxy server URL */
  proxy?: string;
  /** Custom headers */
  headers?: Record<string, string>;
}

/**
 * Batch download request interface
 */
export interface BatchRequest extends BaseRequest {
  /** List of URLs to download */
  urls: string[];
  /** Batch operation name */
  name?: string;
  /** Common output directory for all downloads */
  outputDir?: string;
  /** Common video quality for all downloads */
  videoQuality?: VideoQuality;
  /** Common audio quality for all downloads */
  audioQuality?: AudioQuality;
  /** Common output format */
  format?: VideoFormat | AudioFormat;
  /** Maximum concurrent downloads */
  concurrentDownloads?: number;
  /** Maximum downloads per minute (rate limiting) */
  rateLimit?: number;
  /** Whether to stop on first error */
  stopOnError?: boolean;
  /** Maximum retries per download */
  maxRetries?: number;
  /** Delay between downloads in seconds */
  delayBetweenDownloads?: number;
  /** Whether to use WebSocket for progress updates */
  useWebSocket?: boolean;
  /** Webhook URL for batch completion */
  webhookUrl?: string;
  /** Tags for organization */
  tags?: string[];
  /** Priority level (higher = more important) */
  priority?: number;
}

/**
 * Playlist download request interface
 */
export interface PlaylistRequest extends BaseRequest {
  /** Playlist URL */
  url: string;
  /** Output directory */
  outputDir?: string;
  /** Video quality preference */
  videoQuality?: VideoQuality;
  /** Audio quality preference */
  audioQuality?: AudioQuality;
  /** Output format */
  format?: VideoFormat | AudioFormat;
  /** Item range to download (e.g., '1-10', '5,7,9') */
  itemRange?: string;
  /** Reverse playlist order */
  reverse?: boolean;
  /** Shuffle playlist items */
  shuffle?: boolean;
  /** Maximum concurrent downloads */
  concurrentDownloads?: number;
  /** Download archive file for tracking */
  archiveFile?: string;
  /** Whether to skip already downloaded items */
  skipDownloaded?: boolean;
  /** Whether to download thumbnails */
  downloadThumbnails?: boolean;
  /** Whether to download subtitles */
  downloadSubtitles?: boolean;
  /** Subtitle language codes */
  subtitleLanguages?: string[];
  /** Webhook URL for progress updates */
  webhookUrl?: string;
  /** Whether to use WebSocket for real-time updates */
  useWebSocket?: boolean;
  /** Tags for organization */
  tags?: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// INTERFACES - RESPONSE TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * API response wrapper interface
 * @description Standard response format for all API endpoints
 */
export interface ApiResponse<T = unknown> {
  /** Whether the request was successful */
  success: boolean;
  /** Response data */
  data?: T;
  /** Error message if not successful */
  error?: ApiError;
  /** Request ID for tracking */
  requestId: string;
  /** Response timestamp */
  timestamp: string;
  /** Processing time in milliseconds */
  processingTime: number;
  /** API version */
  version: string;
}

/**
 * API error interface
 */
export interface ApiError {
  /** Error code */
  code: string;
  /** Error message */
  message: string;
  /** Error details */
  details?: Record<string, unknown>;
  /** Stack trace (only in development) */
  stack?: string;
  /** Suggested fix */
  suggestion?: string;
}

/**
 * Download response interface
 */
export interface DownloadResponse {
  /** Download ID */
  downloadId: string;
  /** Download status */
  status: DownloadStatus;
  /** Output file path */
  filePath?: string;
  /** File size in bytes */
  fileSize?: number;
  /** Download progress percentage */
  progress?: number;
  /** Download speed in bytes/sec */
  speed?: number;
  /** Estimated time remaining in seconds */
  eta?: number;
  /** Error message if failed */
  error?: string;
  /** WebSocket channel for updates */
  wsChannel?: string;
}

/**
 * File info response interface
 */
export interface FileInfoResponse {
  /** File path */
  path: string;
  /** Whether file exists */
  exists: boolean;
  /** File size in bytes */
  size?: number;
  /** Creation timestamp */
  createdAt?: Date;
  /** Last modified timestamp */
  modifiedAt?: Date;
  /** File MIME type */
  mimeType?: string;
  /** File extension */
  extension?: string;
  /** Whether it's a directory */
  isDirectory?: boolean;
  /** File permissions */
  permissions?: string;
  /** Checksum (MD5) */
  checksum?: string;
}

/**
 * Media info response interface
 */
export interface MediaInfoResponse {
  /** Source URL */
  url: string;
  /** Media title */
  title: string;
  /** Description */
  description?: string;
  /** Duration in seconds */
  duration?: number;
  /** Uploader/author */
  uploader?: string;
  /** Upload date */
  uploadDate?: string;
  /** View count */
  viewCount?: number;
  /** Like count */
  likeCount?: number;
  /** Thumbnail URL */
  thumbnail?: string;
  /** Available formats */
  formats?: MediaFormat[];
  /** Available subtitles */
  subtitles?: SubtitleInfo[];
  /** Tags/categories */
  tags?: string[];
  /** Platform/source */
  platform?: string;
  /** Original ID */
  id?: string;
}

/**
 * Media format info interface
 */
export interface MediaFormat {
  /** Format ID */
  formatId: string;
  /** Format description */
  description?: string;
  /** File extension */
  extension: string;
  /** Resolution (for video) */
  resolution?: string;
  /** Video codec */
  videoCodec?: string;
  /** Audio codec */
  audioCodec?: string;
  /** Filesize in bytes */
  filesize?: number;
  /** Bitrate */
  bitrate?: number;
  /** FPS (for video) */
  fps?: number;
  /** Whether format includes video */
  hasVideo: boolean;
  /** Whether format includes audio */
  hasAudio: boolean;
}

/**
 * Subtitle info interface
 */
export interface SubtitleInfo {
  /** Language code */
  language: string;
  /** Language name */
  languageName: string;
  /** Whether auto-generated */
  autoGenerated: boolean;
  /** Subtitle format */
  format: string;
}

/**
 * Batch response interface
 */
export interface BatchResponse {
  /** Batch operation ID */
  batchId: string;
  /** Batch status */
  status: BatchStatus;
  /** Total items in batch */
  totalItems: number;
  /** Completed items count */
  completedItems: number;
  /** Failed items count */
  failedItems: number;
  /** Pending items count */
  pendingItems: number;
  /** Overall progress percentage */
  progress: number;
  /** Individual download statuses */
  items: BatchItemStatus[];
  /** WebSocket channel for updates */
  wsChannel?: string;
  /** Estimated time remaining */
  eta?: number;
}

/**
 * Batch item status interface
 */
export interface BatchItemStatus {
  /** Item URL */
  url: string;
  /** Download ID */
  downloadId?: string;
  /** Status */
  status: DownloadStatus;
  /** Progress percentage */
  progress?: number;
  /** Error message if failed */
  error?: string;
  /** Output file path */
  filePath?: string;
}

/**
 * Playlist response interface
 */
export interface PlaylistResponse {
  /** Playlist ID */
  playlistId: string;
  /** Playlist title */
  title: string;
  /** Total items in playlist */
  totalItems: number;
  /** Downloaded items count */
  downloadedItems: number;
  /** Failed items count */
  failedItems: number;
  /** Overall progress percentage */
  progress: number;
  /** Individual item statuses */
  items: PlaylistItemStatus[];
  /** WebSocket channel for updates */
  wsChannel?: string;
  /** Estimated time remaining */
  eta?: number;
}

/**
 * Playlist item status interface
 */
export interface PlaylistItemStatus {
  /** Item position in playlist */
  position: number;
  /** Item title */
  title?: string;
  /** Item URL */
  url: string;
  /** Download ID */
  downloadId?: string;
  /** Status */
  status: DownloadStatus;
  /** Progress percentage */
  progress?: number;
  /** Error message if failed */
  error?: string;
  /** Output file path */
  filePath?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// INTERFACES - WEBSOCKET TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * WebSocket message interface
 */
export interface WSMessage<T = unknown> {
  /** Message type */
  type: WSMessageType;
  /** Message data */
  data: T;
  /** Timestamp */
  timestamp: string;
  /** Message ID */
  messageId: string;
}

/**
 * Download progress WebSocket message
 */
export interface WSDownloadProgress {
  /** Download ID */
  downloadId: string;
  /** Progress percentage (0-100) */
  progress: number;
  /** Downloaded bytes */
  downloadedBytes: number;
  /** Total bytes */
  totalBytes: number;
  /** Download speed in bytes/sec */
  speed: number;
  /** Estimated time remaining in seconds */
  eta: number;
  /** Current status */
  status: DownloadStatus;
}

/**
 * WebSocket connection options
 */
export interface WSConnectionOptions {
  /** Heartbeat interval in milliseconds */
  heartbeatInterval?: number;
  /** Reconnect on disconnect */
  autoReconnect?: boolean;
  /** Maximum reconnect attempts */
  maxReconnectAttempts?: number;
  /** Reconnect delay in milliseconds */
  reconnectDelay?: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// INTERFACES - AUTHENTICATION & SECURITY
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Authentication credentials interface
 */
export interface AuthCredentials {
  /** API key */
  apiKey?: string;
  /** Bearer token */
  token?: string;
  /** Basic auth username */
  username?: string;
  /** Basic auth password */
  password?: string;
}

/**
 * User session interface
 */
export interface UserSession {
  /** Session ID */
  sessionId: string;
  /** User ID */
  userId: string;
  /** User role */
  role: AuthLevel;
  /** Rate limit tier */
  tier: RateLimitTier;
  /** Session creation time */
  createdAt: Date;
  /** Session expiry time */
  expiresAt: Date;
  /** Last activity time */
  lastActivity: Date;
  /** IP address */
  ipAddress?: string;
  /** User agent */
  userAgent?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// INTERFACES - RATE LIMITING & QUOTA
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Rate limit info interface
 */
export interface RateLimitInfo {
  /** Maximum requests allowed */
  limit: number;
  /** Remaining requests */
  remaining: number;
  /** Reset timestamp */
  resetAt: Date;
  /** Retry after seconds (if limited) */
  retryAfter?: number;
}

/**
 * Rate limit configuration
 */
export interface RateLimitConfig {
  /** Window size in milliseconds */
  windowMs: number;
  /** Maximum requests per window */
  maxRequests: number;
  /** Skip failed requests */
  skipFailedRequests?: boolean;
  /** Skip successful requests */
  skipSuccessfulRequests?: boolean;
  /** Key generator function */
  keyGenerator?: (req: Request) => string;
  /** Handler for rate limit exceeded */
  handler?: (req: Request, res: Response) => void;
}

// ═══════════════════════════════════════════════════════════════════════════════
// INTERFACES - QUEUE MANAGEMENT
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Queue item interface
 */
export interface QueueItem<T = unknown> {
  /** Item ID */
  id: string;
  /** Item data */
  data: T;
  /** Priority (higher = more important) */
  priority: number;
  /** Added timestamp */
  addedAt: Date;
  /** Started timestamp */
  startedAt?: Date;
  /** Completed timestamp */
  completedAt?: Date;
  /** Status */
  status: 'pending' | 'running' | 'completed' | 'failed';
  /** Retry count */
  retries: number;
  /** Error message */
  error?: string;
}

/**
 * Queue configuration interface
 */
export interface QueueConfig {
  /** Maximum concurrent items */
  concurrency: number;
  /** Maximum queue size */
  maxSize: number;
  /** Maximum retries per item */
  maxRetries: number;
  /** Retry delay in milliseconds */
  retryDelay: number;
  /** Enable priority queue */
  priorityQueue: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// INTERFACES - LOGGING & MONITORING
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Log entry interface
 */
export interface LogEntry {
  /** Log level */
  level: 'debug' | 'info' | 'warn' | 'error' | 'critical';
  /** Log message */
  message: string;
  /** Timestamp */
  timestamp: string;
  /** Request ID */
  requestId?: string;
  /** User ID */
  userId?: string;
  /** Additional data */
  data?: Record<string, unknown>;
  /** Stack trace */
  stack?: string;
}

/**
 * Performance metrics interface
 */
export interface PerformanceMetrics {
  /** Request count */
  requestCount: number;
  /** Average response time in ms */
  avgResponseTime: number;
  /** Error rate (0-1) */
  errorRate: number;
  /** Active connections */
  activeConnections: number;
  /** Queue size */
  queueSize: number;
  /** Memory usage in MB */
  memoryUsage: number;
  /** CPU usage percentage */
  cpuUsage: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// TYPE GUARDS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Type guard for DownloadRequest
 */
export function isDownloadRequest(obj: unknown): obj is DownloadRequest {
  return typeof obj === 'object' && obj !== null && 'url' in obj;
}

/**
 * Type guard for BatchRequest
 */
export function isBatchRequest(obj: unknown): obj is BatchRequest {
  return typeof obj === 'object' && obj !== null && 'urls' in obj && Array.isArray((obj as BatchRequest).urls);
}

/**
 * Type guard for PlaylistRequest
 */
export function isPlaylistRequest(obj: unknown): obj is PlaylistRequest {
  return typeof obj === 'object' && obj !== null && 'url' in obj;
}

/**
 * Type guard for ApiResponse
 */
export function isApiResponse<T>(obj: unknown): obj is ApiResponse<T> {
  return typeof obj === 'object' && obj !== null && 'success' in obj && 'requestId' in obj;
}

// ═══════════════════════════════════════════════════════════════════════════════
// UTILITY TYPES
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Make all properties optional recursively
 */
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

/**
 * Make specific keys required
 */
export type RequireKeys<T, K extends keyof T> = T & Required<Pick<T, K>>;

/**
 * Omit keys from type
 */
export type OmitKeys<T, K extends keyof T> = Omit<T, K>;

/**
 * Pick keys from type
 */
export type PickKeys<T, K extends keyof T> = Pick<T, K>;

/**
 * Nullable type
 */
export type Nullable<T> = T | null;

/**
 * Optional type
 */
export type Optional<T> = T | undefined;

/**
 * Async function type
 */
export type AsyncFunction<T = void> = () => Promise<T>;

/**
 * Event handler type
 */
export type EventHandler<T = unknown> = (data: T) => void;

/**
 * Pagination parameters
 */
export interface PaginationParams {
  page: number;
  limit: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

/**
 * Paginated response
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
  hasMore: boolean;
}
