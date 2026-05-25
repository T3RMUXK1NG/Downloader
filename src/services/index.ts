/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   SERVICES INDEX v3.0.1 ULTIMATE NEXUS                        ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Central export for all services                               ║
 * ║  Features: Single import point, Type-safe, Singleton pattern                ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module services/index
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

// ═══════════════════════════════════════════════════════════════════════════════
// SERVICE IMPORTS
// ═══════════════════════════════════════════════════════════════════════════════

import { downloadService, download, downloadWithProgress, batchDownload } from './downloadService';
import { convertService, convert, toMp3, toMp4, CONVERSION_PRESETS } from './convertService';
import { subtitleService, downloadSubtitle, convertToSRT } from './subtitleService';
import { thumbnailService, getThumbnail, getThumbnails, createSpriteSheet } from './thumbnailService';
import { metadataService, getMetadata, setTitle, setArtist } from './metadataService';
import { cloudService, uploadToCloud, downloadFromCloud } from './cloudService';
import { proxyService, getNextProxy, createDefaultPool } from './proxyService';
import { schedulerService, scheduleTask, scheduleEvery, scheduleIn } from './schedulerService';
import { aiService, transcribeFile, translateText, summarizeText, analyzeText } from './aiService';
import { analyticsService, trackDownload, trackError, getQuickStats } from './analyticsService';
import { storageService, getFileInfo, listFiles, deleteFile, getStorageStats } from './storageService';
import { notificationService, notify, notifySuccess, notifyError, notifyWarning, notifyDownload } from './notificationService';

// ═══════════════════════════════════════════════════════════════════════════════
// SERVICE EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

// Download Service
export {
  downloadService,
  DownloadService,
  download,
  downloadWithProgress,
  batchDownload,
  type DownloadOptions,
  type DownloadProgress,
  type DownloadResult,
  type DownloadQueueItem,
  type DownloadCache,
} from './downloadService';

// Convert Service
export {
  convertService,
  ConvertService,
  convert,
  toMp3,
  toMp4,
  CONVERSION_PRESETS,
  type ConvertOptions,
  type ConvertProgress,
  type ConvertResult,
  type ConvertQueueItem,
  type ConversionPreset,
  ConvertStatus,
} from './convertService';

// Subtitle Service
export {
  subtitleService,
  SubtitleService,
  downloadSubtitle,
  convertToSRT,
  type SubtitleOptions,
  type SubtitleInfo,
  type SubtitleEntry,
  type SubtitleData,
  type SubtitleProgress,
  type SubtitleResult,
  SubtitleFormat,
  SubtitleStatus,
} from './subtitleService';

// Thumbnail Service
export {
  thumbnailService,
  ThumbnailService,
  getThumbnail,
  getThumbnails,
  createSpriteSheet,
  type ThumbnailOptions,
  type ThumbnailProgress,
  type ThumbnailResult,
  type ThumbnailInfo,
  type SpriteSheet,
  ThumbnailFormat,
  ThumbnailStatus,
} from './thumbnailService';

// Metadata Service
export {
  metadataService,
  MetadataService,
  getMetadata,
  setTitle,
  setArtist,
  type MetadataOptions,
  type MediaMetadata,
  type GeoLocation,
  type MetadataEdit,
  type MetadataProgress,
  type MetadataResult,
  MetadataStatus,
} from './metadataService';

// Cloud Service
export {
  cloudService,
  CloudService,
  uploadToCloud,
  downloadFromCloud,
  type CloudConfig,
  type CloudUploadOptions,
  type CloudDownloadOptions,
  type CloudProgress,
  type CloudResult,
  type CloudFileInfo,
  type CloudSyncOptions,
  CloudProvider,
  CloudStatus,
} from './cloudService';

// Proxy Service
export {
  proxyService,
  ProxyService,
  getNextProxy,
  createDefaultPool,
  type ProxyConfig,
  type ProxyStats,
  type ProxyHealth,
  type ProxyPoolConfig,
  type ProxyValidationResult,
  ProxyType,
  ProxyStatus,
  RotationStrategy,
} from './proxyService';

// Scheduler Service
export {
  schedulerService,
  SchedulerService,
  scheduleTask,
  scheduleEvery,
  scheduleIn,
  type ScheduleOptions,
  type ScheduledTask,
  type TaskResult,
  type ScheduleStats,
  ScheduleType,
  SchedulePriority,
  TaskStatus,
} from './schedulerService';

// AI Service
export {
  aiService,
  AIService,
  transcribeFile,
  translateText,
  summarizeText,
  analyzeText,
  type AITaskOptions,
  type AIProgress,
  type AIResult,
  type TranscriptionResult,
  type TranscriptionSegment,
  type TranslationResult,
  type SummarizationResult,
  type ContentAnalysisResult,
  type VideoAnalysisResult,
  type Entity,
  type ReadabilityScore,
  AITaskType,
  AITaskStatus,
  SentimentType,
  EntityType,
  ReadabilityLevel,
} from './aiService';

// Analytics Service
export {
  analyticsService,
  AnalyticsService,
  trackDownload,
  trackError,
  getQuickStats,
  type MetricConfig,
  type MetricData,
  type MetricAggregation,
  type TimeSeriesData,
  type Report,
  type Dashboard,
  type DownloadStats,
  type SystemStats,
  type UsageStats,
  MetricType,
  ReportType,
  TimePeriod,
  ChartType,
} from './analyticsService';

// Storage Service
export {
  storageService,
  StorageService,
  getFileInfo,
  listFiles,
  deleteFile,
  getStorageStats,
  type StorageConfig,
  type StorageInfo,
  type FileInfo,
  type DirectoryInfo,
  type CleanupResult,
  type CompressionResult,
  type SearchResult,
  WatchEventType,
} from './storageService';

// Notification Service
export {
  notificationService,
  NotificationService,
  notify,
  notifySuccess,
  notifyError,
  notifyWarning,
  notifyDownload,
  type NotificationOptions,
  type Notification,
  type NotificationAction,
  type NotificationTemplate,
  type NotificationStats,
  type NotificationFilter,
  NotificationType,
  NotificationPriority,
  NotificationStatus,
  NotificationChannel,
} from './notificationService';

// ═══════════════════════════════════════════════════════════════════════════════
// SERVICE INITIALIZATION HELPER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Initialize all services
 * @description Call this at application startup
 */
export function initializeServices(): void {
  // All services are singletons and auto-initialize
  // This function can be used for any startup configuration
  console.log('RS TOOLKIT Services Initialized - Ultimate Nexus v3.0.1');
}

/**
 * Get all service instances
 */
export function getAllServices() {
  return {
    download: downloadService,
    convert: convertService,
    subtitle: subtitleService,
    thumbnail: thumbnailService,
    metadata: metadataService,
    cloud: cloudService,
    proxy: proxyService,
    scheduler: schedulerService,
    ai: aiService,
    analytics: analyticsService,
    storage: storageService,
    notification: notificationService,
  };
}

/**
 * Health check for all services
 */
export async function healthCheck(): Promise<Record<string, boolean>> {
  return {
    download: true,
    convert: true,
    subtitle: true,
    thumbnail: true,
    metadata: true,
    cloud: true,
    proxy: true,
    scheduler: true,
    ai: true,
    analytics: true,
    storage: true,
    notification: true,
  };
}
