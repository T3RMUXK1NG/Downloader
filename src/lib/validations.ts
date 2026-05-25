/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║               VALIDATION SCHEMAS v3.2.0 ULTIMATE NEXUS                       ║
 * ║                  OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Comprehensive Zod validation schemas for all API routes       ║
 * ║  Features:                                                                   ║
 * ║    - Zod schema definitions for all request types                           ║
 * ║    - Custom validation refinements                                          ║
 * ║    - Error message customization                                            ║
 * ║    - Type inference from schemas                                            ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module lib/validations
 * @version 3.2.0
 * @author RAJSARASWATI JATAV (RS)
 */

import { z } from 'zod';

// ═══════════════════════════════════════════════════════════════════════════════
// ENUMERATIONS
// ═══════════════════════════════════════════════════════════════════════════════

export const VideoQualitySchema = z.enum([
  '2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p',
  'audio', 'best', 'worst'
]);

export const AudioQualitySchema = z.enum([
  'flac', '320kbps', '192kbps', '128kbps', '64kbps'
]);

export const VideoFormatSchema = z.enum([
  'mp4', 'webm', 'mkv', 'avi', 'mov', 'flv'
]);

export const AudioFormatSchema = z.enum([
  'mp3', 'aac', 'ogg', 'flac', 'wav', 'm4a', 'opus'
]);

export const FileTypeSchema = z.enum([
  'video', 'audio', 'image', 'document', 'archive', 'subtitle', 'metadata', 'thumbnail', 'playlist', 'unknown'
]);

export const DownloadStatusSchema = z.enum([
  'pending', 'downloading', 'paused', 'completed', 'failed', 'cancelled', 'retrying', 'validating', 'processing'
]);

export const BatchStatusSchema = z.enum([
  'queued', 'running', 'completed', 'failed', 'cancelled', 'paused'
]);

// ═══════════════════════════════════════════════════════════════════════════════
// CUSTOM VALIDATIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * URL validation with custom error messages
 */
export const UrlSchema = z.string().url('Invalid URL format. Must be a valid HTTP/HTTPS URL').max(2048, 'URL too long (max 2048 characters)');

/**
 * Optional URL validation
 */
export const OptionalUrlSchema = z.string().url('Invalid URL format').max(2048).optional();

/**
 * File path validation (prevents directory traversal)
 */
export const FilePathSchema = z.string()
  .min(1, 'Path is required')
  .max(4096, 'Path too long')
  .refine(
    (path) => !path.includes('..') && !path.includes('~'),
    'Invalid path: directory traversal not allowed'
  );

/**
 * Safe file path (relative or within allowed directories)
 */
export const SafeFilePathSchema = z.string()
  .min(1, 'Path is required')
  .max(4096, 'Path too long')
  .refine(
    (path) => !path.includes('..'),
    'Invalid path: directory traversal not allowed'
  );

/**
 * Filename validation (sanitized)
 */
export const FilenameSchema = z.string()
  .min(1, 'Filename is required')
  .max(255, 'Filename too long')
  .refine(
    (name) => !/[<>:"/\\|?*\x00-\x1f]/.test(name),
    'Filename contains invalid characters'
  );

/**
 * Proxy URL validation
 */
export const ProxyUrlSchema = z.string()
  .regex(
    /^(https?|socks[45]):\/\/.+/
    , 'Invalid proxy URL. Must be HTTP, HTTPS, SOCKS4, or SOCKS5'
  )
  .optional();

/**
 * Webhook URL validation
 */
export const WebhookUrlSchema = z.string().url('Invalid webhook URL').optional();

/**
 * Positive number validation
 */
export const PositiveNumberSchema = (min: number = 0, max: number = Infinity) =>
  z.number().min(min).max(max);

/**
 * Port number validation
 */
export const PortSchema = z.number().int().min(1).max(65535);

/**
 * Email validation
 */
export const EmailSchema = z.string().email('Invalid email format');

/**
 * Language code validation (ISO 639-1)
 */
export const LanguageCodeSchema = z.string().regex(/^[a-z]{2}(-[A-Z]{2})?$/, 'Invalid language code');

/**
 * Time range validation (HH:MM:SS or seconds)
 */
export const TimeRangeSchema = z.string()
  .regex(/^(\d+:)?[0-5]?\d:[0-5]\d$|^\d+(\.\d+)?$/, 'Invalid time format')
  .optional();

/**
 * Cron expression validation (basic)
 */
export const CronExpressionSchema = z.string()
  .regex(
    /^(\*|([0-9]|[1-5][0-9])(-([0-9]|[1-5][0-9]))?(,([0-9]|[1-5][0-9])(-([0-9]|[1-5][0-9]))?)*)\s+(\*|([0-9]|1[0-9]|2[0-3])(-([0-9]|1[0-9]|2[0-3]))?(,([0-9]|1[0-9]|2[0-3])(-([0-9]|1[0-9]|2[0-3]))?)*)\s+(\*|([1-9]|[12][0-9]|3[01])(-([1-9]|[12][0-9]|3[01]))?(,([1-9]|[12][0-9]|3[01])(-([1-9]|[12][0-9]|3[01]))?)*)\s+(\*|([1-9]|1[0-2])(-([1-9]|1[0-2]))?(,([1-9]|1[0-2])(-([1-9]|1[0-2]))?)*)\s+(\*|([0-6])(-([0-6]))?(,([0-6])(-([0-6]))?)*)$/,
    'Invalid cron expression'
  )
  .optional();

/**
 * Tags validation
 */
export const TagsSchema = z.array(z.string().max(50)).max(20).optional();

// ═══════════════════════════════════════════════════════════════════════════════
// REQUEST SCHEMAS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Base request schema with common fields
 */
export const BaseRequestSchema = z.object({
  requestId: z.string().optional(),
  timestamp: z.date().optional(),
  clientVersion: z.string().optional(),
  metadata: z.record(z.unknown()).optional(),
});

/**
 * Download request schema
 */
export const DownloadRequestSchema = BaseRequestSchema.extend({
  url: UrlSchema,
  filename: FilenameSchema.optional(),
  outputDir: SafeFilePathSchema.optional(),
  videoQuality: VideoQualitySchema.optional(),
  audioQuality: AudioQualitySchema.optional(),
  format: z.union([VideoFormatSchema, AudioFormatSchema]).optional(),
  fileType: FileTypeSchema.optional(),
  downloadSubtitles: z.boolean().optional(),
  subtitleLanguages: z.array(LanguageCodeSchema).max(20).optional(),
  downloadThumbnail: z.boolean().optional(),
  embedMetadata: z.boolean().optional(),
  proxy: ProxyUrlSchema,
  headers: z.record(z.string()).optional(),
  cookies: z.string().max(8192).optional(),
  username: z.string().max(256).optional(),
  password: z.string().max(256).optional(),
  overwrite: z.boolean().optional(),
  maxSpeed: z.number().min(0).max(10737418240).optional(), // Max 10GB/s
  retries: z.number().int().min(0).max(10).optional(),
  timeout: z.number().int().min(0).max(3600).optional(),
  useWebSocket: z.boolean().optional(),
  webhookUrl: WebhookUrlSchema,
  tags: TagsSchema,
});

/**
 * Batch download request schema
 */
export const BatchRequestSchema = BaseRequestSchema.extend({
  urls: z.array(UrlSchema).min(1, 'At least one URL is required').max(100, 'Maximum 100 URLs allowed'),
  name: z.string().max(256).optional(),
  outputDir: SafeFilePathSchema.optional(),
  videoQuality: VideoQualitySchema.optional(),
  audioQuality: AudioQualitySchema.optional(),
  format: z.union([VideoFormatSchema, AudioFormatSchema]).optional(),
  concurrentDownloads: z.number().int().min(1).max(10).optional(),
  rateLimit: z.number().int().min(1).max(1000).optional(),
  stopOnError: z.boolean().optional(),
  maxRetries: z.number().int().min(0).max(10).optional(),
  delayBetweenDownloads: z.number().min(0).max(300).optional(),
  useWebSocket: z.boolean().optional(),
  webhookUrl: WebhookUrlSchema,
  tags: TagsSchema,
  priority: z.number().int().min(0).max(100).optional(),
});

/**
 * Playlist download request schema
 */
export const PlaylistRequestSchema = BaseRequestSchema.extend({
  url: UrlSchema,
  outputDir: SafeFilePathSchema.optional(),
  videoQuality: VideoQualitySchema.optional(),
  audioQuality: AudioQualitySchema.optional(),
  format: z.union([VideoFormatSchema, AudioFormatSchema]).optional(),
  itemRange: z.string().max(256).optional(),
  reverse: z.boolean().optional(),
  shuffle: z.boolean().optional(),
  concurrentDownloads: z.number().int().min(1).max(10).optional(),
  archiveFile: SafeFilePathSchema.optional(),
  skipDownloaded: z.boolean().optional(),
  downloadThumbnails: z.boolean().optional(),
  downloadSubtitles: z.boolean().optional(),
  subtitleLanguages: z.array(LanguageCodeSchema).max(20).optional(),
  webhookUrl: WebhookUrlSchema,
  useWebSocket: z.boolean().optional(),
  tags: TagsSchema,
});

/**
 * Info request schema
 */
export const InfoRequestSchema = BaseRequestSchema.extend({
  url: UrlSchema,
  fullMetadata: z.boolean().optional(),
  includeFormats: z.boolean().optional(),
  includeSubtitles: z.boolean().optional(),
  includeThumbnails: z.boolean().optional(),
  proxy: ProxyUrlSchema,
  headers: z.record(z.string()).optional(),
});

/**
 * Convert request schema
 */
export const ConvertRequestSchema = BaseRequestSchema.extend({
  inputPath: z.union([UrlSchema, SafeFilePathSchema]),
  outputFormat: z.union([VideoFormatSchema, AudioFormatSchema]),
  outputFilename: FilenameSchema.optional(),
  outputDir: SafeFilePathSchema.optional(),
  videoQuality: VideoQualitySchema.optional(),
  audioQuality: AudioQualitySchema.optional(),
  videoCodec: z.string().max(50).optional(),
  audioCodec: z.string().max(50).optional(),
  videoBitrate: z.string().max(20).optional(),
  audioBitrate: z.string().max(20).optional(),
  frameRate: z.number().int().min(1).max(120).optional(),
  resolution: z.string().regex(/^\d+x\d+$/, 'Invalid resolution format').optional(),
  aspectRatio: z.string().max(20).optional(),
  hardwareAcceleration: z.enum(['none', 'nvenc', 'amf', 'qsv', 'videotoolbox', 'auto']).optional(),
  customOptions: z.array(z.string()).max(50).optional(),
  startTime: z.number().min(0).optional(),
  endTime: z.number().min(0).optional(),
  duration: z.number().min(0).optional(),
  subtitleFile: SafeFilePathSchema.optional(),
  preserveMetadata: z.boolean().optional(),
  copyVideo: z.boolean().optional(),
  copyAudio: z.boolean().optional(),
  audioFilters: z.array(z.string()).max(20).optional(),
  videoFilters: z.array(z.string()).max(20).optional(),
  passes: z.number().int().min(1).max(2).optional(),
  threads: z.number().int().min(1).max(64).optional(),
  priority: z.enum(['low', 'normal', 'high']).optional(),
  webhookUrl: WebhookUrlSchema,
  useWebSocket: z.boolean().optional(),
  overwrite: z.boolean().optional(),
});

/**
 * Subtitle request schema
 */
export const SubtitleRequestSchema = BaseRequestSchema.extend({
  operation: z.enum(['download', 'convert', 'embed', 'extract', 'translate', 'generate', 'sync']),
  mediaPath: z.union([UrlSchema, SafeFilePathSchema]).optional(),
  subtitlePath: z.union([UrlSchema, SafeFilePathSchema]).optional(),
  outputDir: SafeFilePathSchema.optional(),
  outputFilename: FilenameSchema.optional(),
  outputFormat: z.enum(['srt', 'vtt', 'ass', 'ssa', 'sub', 'sbv', 'ttml', 'json']).optional(),
  language: LanguageCodeSchema.optional(),
  targetLanguage: LanguageCodeSchema.optional(),
  languages: z.array(LanguageCodeSchema).max(20).optional(),
  includeAutoGenerated: z.boolean().optional(),
  timeOffset: z.number().optional(),
  embedInVideo: z.boolean().optional(),
  videoOutputPath: SafeFilePathSchema.optional(),
  burnIntoVideo: z.boolean().optional(),
  useWebSocket: z.boolean().optional(),
  webhookUrl: WebhookUrlSchema,
  overwrite: z.boolean().optional(),
});

/**
 * Thumbnail request schema
 */
export const ThumbnailRequestSchema = BaseRequestSchema.extend({
  mediaPath: z.union([UrlSchema, SafeFilePathSchema]),
  outputDir: SafeFilePathSchema.optional(),
  outputPrefix: z.string().max(256).optional(),
  outputFormat: z.enum(['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp']).optional(),
  mode: z.enum(['single', 'multiple', 'sprite', 'animated', 'keyframe']).optional(),
  timestamp: z.number().min(0).optional(),
  timestamps: z.array(z.number().min(0)).max(100).optional(),
  count: z.number().int().min(1).max(100).optional(),
  interval: z.number().min(0.1).optional(),
  width: z.number().int().min(1).max(4096).optional(),
  height: z.number().int().min(1).max(4096).optional(),
  maintainAspectRatio: z.boolean().optional(),
  quality: z.number().int().min(1).max(100).optional(),
  spriteColumns: z.number().int().min(1).max(50).optional(),
  spriteRows: z.number().int().min(1).max(50).optional(),
  animatedDuration: z.number().min(1).max(60).optional(),
  animatedFps: z.number().int().min(1).max(30).optional(),
  animatedFormat: z.enum(['gif', 'webp']).optional(),
  filters: z.array(z.string()).max(20).optional(),
  useWebSocket: z.boolean().optional(),
  webhookUrl: WebhookUrlSchema,
  overwrite: z.boolean().optional(),
});

/**
 * Metadata request schema
 */
export const MetadataRequestSchema = BaseRequestSchema.extend({
  operation: z.enum(['extract', 'edit', 'remove', 'copy']),
  sourcePath: z.union([UrlSchema, SafeFilePathSchema]),
  targetPath: SafeFilePathSchema.optional(),
  outputDir: SafeFilePathSchema.optional(),
  outputFilename: FilenameSchema.optional(),
  outputFormat: z.enum(['json', 'xml', 'txt']).optional(),
  metadataType: z.enum(['all', 'video', 'audio', 'exif', 'id3', 'xmp', 'iptc', 'custom']).optional(),
  fields: z.array(z.string()).max(100).optional(),
  metadata: z.array(z.object({
    key: z.string(),
    value: z.union([z.string(), z.number(), z.boolean(), z.null()]),
    namespace: z.string().optional(),
    type: z.enum(['string', 'number', 'boolean', 'date']).optional(),
    editable: z.boolean().optional(),
  })).optional(),
  removeAll: z.boolean().optional(),
  removeFields: z.array(z.string()).max(100).optional(),
  preserveFileTime: z.boolean().optional(),
  createBackup: z.boolean().optional(),
  useWebSocket: z.boolean().optional(),
  webhookUrl: WebhookUrlSchema,
});

/**
 * Schedule request schema
 */
export const ScheduleRequestSchema = BaseRequestSchema.extend({
  operation: z.enum(['create', 'update', 'cancel', 'pause', 'resume', 'list', 'delete']),
  scheduleId: z.string().optional(),
  name: z.string().max(256).optional(),
  url: UrlSchema.optional(),
  scheduledTime: z.string().datetime().optional(),
  cronExpression: CronExpressionSchema,
  recurrence: z.object({
    type: z.enum(['none', 'daily', 'weekly', 'monthly', 'custom']),
    interval: z.number().int().min(1).max(365).optional(),
    daysOfWeek: z.array(z.number().int().min(0).max(6)).max(7).optional(),
    daysOfMonth: z.array(z.number().int().min(1).max(31)).max(31).optional(),
    endDate: z.string().datetime().optional(),
    maxOccurrences: z.number().int().min(1).max(1000).optional(),
  }).optional(),
  videoQuality: VideoQualitySchema.optional(),
  audioQuality: AudioQualitySchema.optional(),
  format: z.union([VideoFormatSchema, AudioFormatSchema]).optional(),
  outputDir: SafeFilePathSchema.optional(),
  filename: FilenameSchema.optional(),
  priority: z.number().int().min(1).max(10).optional(),
  tags: TagsSchema,
  webhookUrl: WebhookUrlSchema,
  maxRetries: z.number().int().min(0).max(10).optional(),
  condition: z.object({
    type: z.enum(['file_exists', 'file_not_exists', 'url_available', 'time_range', 'custom']),
    value: z.string(),
    negate: z.boolean().optional(),
  }).optional(),
  metadata: z.record(z.unknown()).optional(),
});

/**
 * Cloud request schema
 */
export const CloudRequestSchema = BaseRequestSchema.extend({
  operation: z.enum(['upload', 'download', 'sync', 'list', 'delete', 'move', 'copy', 'mkdir', 'info']),
  provider: z.enum(['dropbox', 'google_drive', 'one_drive', 'aws_s3', 'mega', 'p_cloud', 'box', 'webdav', 'ftp', 'sftp']),
  localPath: SafeFilePathSchema.optional(),
  cloudPath: z.string().max(4096).optional(),
  destinationPath: z.string().max(4096).optional(),
  folderName: z.string().max(256).optional(),
  credentials: z.object({
    accessToken: z.string().optional(),
    refreshToken: z.string().optional(),
    apiKey: z.string().optional(),
    apiSecret: z.string().optional(),
    username: z.string().optional(),
    password: z.string().optional(),
    host: z.string().optional(),
    port: PortSchema.optional(),
    bucket: z.string().optional(),
    region: z.string().optional(),
  }).optional(),
  syncDirection: z.enum(['upload', 'download', 'bidirectional']).optional(),
  includeHidden: z.boolean().optional(),
  overwrite: z.boolean().optional(),
  createParents: z.boolean().optional(),
  chunkSize: z.number().int().min(1024).max(104857600).optional(),
  parallelTransfers: z.number().int().min(1).max(10).optional(),
  useWebSocket: z.boolean().optional(),
  webhookUrl: WebhookUrlSchema,
});

/**
 * AI request schema
 */
export const AIRequestSchema = BaseRequestSchema.extend({
  feature: z.enum([
    'analyze', 'summarize', 'translate', 'transcribe', 'recommend',
    'tag', 'detect_duplicates', 'quality_predict', 'content_moderate', 'sentiment'
  ]),
  input: z.string().max(1000000),
  inputType: z.enum(['text', 'url', 'file', 'audio', 'video', 'image']).optional(),
  model: z.enum(['gpt-4', 'gpt-3.5-turbo', 'claude', 'gemini', 'llama', 'custom']).optional(),
  targetLanguage: LanguageCodeSchema.optional(),
  prompt: z.string().max(10000).optional(),
  maxTokens: z.number().int().min(1).max(100000).optional(),
  temperature: z.number().min(0).max(2).optional(),
  params: z.record(z.unknown()).optional(),
  includeConfidence: z.boolean().optional(),
  useWebSocket: z.boolean().optional(),
  webhookUrl: WebhookUrlSchema,
});

/**
 * File request schema
 */
export const FileRequestSchema = BaseRequestSchema.extend({
  path: SafeFilePathSchema,
  operation: z.enum(['read', 'delete', 'move', 'copy', 'rename', 'info', 'exists']),
  destination: SafeFilePathSchema.optional(),
  newName: FilenameSchema.optional(),
  createParents: z.boolean().optional(),
  overwrite: z.boolean().optional(),
});

/**
 * Proxy request schema
 */
export const ProxyRequestSchema = BaseRequestSchema.extend({
  operation: z.enum(['add', 'remove', 'update', 'test', 'rotate', 'clear']),
  proxy: z.object({
    url: z.string().max(2048),
    type: z.enum(['http', 'https', 'socks4', 'socks5']).optional(),
    country: z.string().max(10).optional(),
    tags: TagsSchema,
    priority: z.number().int().min(0).max(100).optional(),
    maxConnections: z.number().int().min(1).max(100).optional(),
  }).optional(),
  proxyId: z.string().optional(),
  proxies: z.array(z.object({
    url: z.string().max(2048),
    type: z.enum(['http', 'https', 'socks4', 'socks5']).optional(),
    country: z.string().max(10).optional(),
    tags: TagsSchema,
    priority: z.number().int().min(0).max(100).optional(),
    maxConnections: z.number().int().min(1).max(100).optional(),
  })).max(100).optional(),
  proxyIds: z.array(z.string()).max(100).optional(),
  testUrl: UrlSchema.optional(),
  testTimeout: z.number().int().min(1000).max(60000).optional(),
  filter: z.object({
    type: z.enum(['http', 'https', 'socks4', 'socks5']).optional(),
    country: z.string().max(10).optional(),
    minResponseTime: z.number().min(0).optional(),
    maxResponseTime: z.number().min(0).optional(),
    minUptime: z.number().min(0).max(100).optional(),
    tags: TagsSchema,
    status: z.enum(['active', 'inactive', 'testing', 'failed']).optional(),
  }).optional(),
});

/**
 * Trim request schema
 */
export const TrimRequestSchema = BaseRequestSchema.extend({
  inputPath: z.union([UrlSchema, SafeFilePathSchema]),
  outputDir: SafeFilePathSchema.optional(),
  outputFormat: z.union([VideoFormatSchema, AudioFormatSchema]).optional(),
  startTime: z.number().min(0).optional(),
  endTime: z.number().min(0).optional(),
  duration: z.number().min(0).optional(),
  segments: z.array(z.object({
    name: z.string().max(256).optional(),
    startTime: z.number().min(0),
    endTime: z.number().min(0),
    outputFilename: FilenameSchema.optional(),
  })).max(100).optional(),
  mode: z.enum(['copy', 'encode', 'auto']).optional(),
  outputPrefix: z.string().max(256).optional(),
  videoQuality: z.string().max(50).optional(),
  audioQuality: z.string().max(50).optional(),
  videoCodec: z.string().max(50).optional(),
  audioCodec: z.string().max(50).optional(),
  preserveMetadata: z.boolean().optional(),
  customOptions: z.array(z.string()).max(50).optional(),
  keyframeAccurate: z.boolean().optional(),
  threads: z.number().int().min(1).max(64).optional(),
  useWebSocket: z.boolean().optional(),
  webhookUrl: WebhookUrlSchema,
  overwrite: z.boolean().optional(),
});

/**
 * Merge request schema
 */
export const MergeRequestSchema = BaseRequestSchema.extend({
  inputFiles: z.array(z.object({
    path: z.union([UrlSchema, SafeFilePathSchema]),
    startTime: z.number().min(0).optional(),
    endTime: z.number().min(0).optional(),
    volume: z.number().min(0).max(2).optional(),
    label: z.string().max(256).optional(),
  })).min(2, 'At least 2 input files are required').max(100, 'Maximum 100 input files allowed'),
  outputDir: SafeFilePathSchema.optional(),
  outputFilename: FilenameSchema.optional(),
  outputFormat: z.union([VideoFormatSchema, AudioFormatSchema]).optional(),
  transitions: z.array(z.object({
    type: z.enum(['none', 'fade', 'dissolve', 'wipe', 'slide', 'zoom']),
    duration: z.number().min(0).max(10),
    params: z.record(z.unknown()).optional(),
  })).max(100).optional(),
  defaultTransition: z.object({
    type: z.enum(['none', 'fade', 'dissolve', 'wipe', 'slide', 'zoom']),
    duration: z.number().min(0).max(10),
    params: z.record(z.unknown()).optional(),
  }).optional(),
  resolution: z.string().regex(/^\d+x\d+$/).optional(),
  frameRate: z.number().int().min(1).max(120).optional(),
  videoQuality: z.string().max(50).optional(),
  audioQuality: z.string().max(50).optional(),
  videoCodec: z.string().max(50).optional(),
  audioCodec: z.string().max(50).optional(),
  normalizeAudio: z.boolean().optional(),
  normalizeVideo: z.boolean().optional(),
  backgroundAudio: SafeFilePathSchema.optional(),
  backgroundAudioVolume: z.number().min(0).max(1).optional(),
  outputVolume: z.number().min(0).max(2).optional(),
  threads: z.number().int().min(1).max(64).optional(),
  preserveMetadata: z.boolean().optional(),
  customOptions: z.array(z.string()).max(50).optional(),
  useWebSocket: z.boolean().optional(),
  webhookUrl: WebhookUrlSchema,
  overwrite: z.boolean().optional(),
});

// ═══════════════════════════════════════════════════════════════════════════════
// TYPE EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export type DownloadRequestInput = z.infer<typeof DownloadRequestSchema>;
export type BatchRequestInput = z.infer<typeof BatchRequestSchema>;
export type PlaylistRequestInput = z.infer<typeof PlaylistRequestSchema>;
export type InfoRequestInput = z.infer<typeof InfoRequestSchema>;
export type ConvertRequestInput = z.infer<typeof ConvertRequestSchema>;
export type SubtitleRequestInput = z.infer<typeof SubtitleRequestSchema>;
export type ThumbnailRequestInput = z.infer<typeof ThumbnailRequestSchema>;
export type MetadataRequestInput = z.infer<typeof MetadataRequestSchema>;
export type ScheduleRequestInput = z.infer<typeof ScheduleRequestSchema>;
export type CloudRequestInput = z.infer<typeof CloudRequestSchema>;
export type AIRequestInput = z.infer<typeof AIRequestSchema>;
export type FileRequestInput = z.infer<typeof FileRequestSchema>;
export type ProxyRequestInput = z.infer<typeof ProxyRequestSchema>;
export type TrimRequestInput = z.infer<typeof TrimRequestSchema>;
export type MergeRequestInput = z.infer<typeof MergeRequestSchema>;

// ═══════════════════════════════════════════════════════════════════════════════
// VALIDATION HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Parse and validate request body with Zod schema
 * @param schema Zod schema to validate against
 * @param data Data to validate
 * @returns Validation result with success flag and data or errors
 */
export function validateWithZod<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): { success: true; data: T } | { success: false; errors: z.ZodError } {
  const result = schema.safeParse(data);
  if (result.success) {
    return { success: true, data: result.data };
  }
  return { success: false, errors: result.error };
}

/**
 * Format Zod validation errors for API response
 * @param error Zod error object
 * @returns Formatted error object
 */
export function formatZodErrors(error: z.ZodError): {
  code: string;
  message: string;
  details: Array<{ field: string; message: string }>;
} {
  return {
    code: 'VALIDATION_ERROR',
    message: 'Request validation failed',
    details: error.errors.map((err) => ({
      field: err.path.join('.'),
      message: err.message,
    })),
  };
}

/**
 * Create a partial schema for PATCH operations
 * @param schema Zod object schema
 * @returns Partial schema where all fields are optional
 */
export function createPartialSchema<T extends z.ZodRawShape>(
  schema: z.ZodObject<T>
): z.ZodOptional<z.ZodObject<T>> {
  return schema.partial();
}
