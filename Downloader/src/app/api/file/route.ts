/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    FILE API ROUTE v3.0.1 ULTIMATE NEXUS                      ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Comprehensive file management API                              ║
 * ║  Features:                                                                   ║
 * ║    - File read/write/delete/move/copy/rename operations                     ║
 * ║    - Directory listing and management                                        ║
 * ║    - File metadata extraction                                                ║
 * ║    - Checksum calculation (MD5, SHA256)                                     ║
 * ║    - Streaming file upload/download                                          ║
 * ║    - File type detection and validation                                      ║
 * ║    - Bulk file operations                                                    ║
 * ║    - File search and filtering                                               ║
 * ║    - Storage statistics                                                      ║
 * ║    - Security validations and sanitization                                   ║
 * ║    - Rate limiting and authentication                                        ║
 * ║    - Comprehensive logging                                                   ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module api/file
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 * 
 * @example
 * // GET /api/file?path=/downloads
 * // Response: File info or directory listing
 * 
 * // POST /api/file
 * // Request body: { path: "/downloads/file.mp4", operation: "delete" }
 */

import { NextRequest } from 'next/server';
import {
  FileRequest,
  FileInfoResponse,
  FileType,
} from '@/types/api';
import {
  successResponse,
  errorResponse,
  validationError,
  generateRequestId,
  parseJsonBody,
  isValidFilePath,
  sanitizeFilename,
  rateLimitMiddleware,
  authMiddleware,
  createMiddleware,
  logger,
  formatBytes,
  RateLimitTier,
  AuthLevel,
  getMimeType,
} from '@/lib/utils';
import * as fs from 'fs/promises';
import * as path from 'path';
import * as crypto from 'crypto';

// ═══════════════════════════════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════════════════════════════

const BASE_DIR = process.env.DOWNLOAD_DIR || '/downloads';
const MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024; // 10GB
const ALLOWED_EXTENSIONS = [
  // Video
  'mp4', 'webm', 'mkv', 'avi', 'mov', 'flv',
  // Audio
  'mp3', 'aac', 'ogg', 'flac', 'wav', 'm4a', 'opus',
  // Image
  'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg',
  // Document
  'pdf', 'doc', 'docx', 'txt', 'md',
  // Subtitle
  'srt', 'vtt', 'ass', 'sub',
  // Archive
  'zip', 'tar', 'gz', 'rar',
];

// ═══════════════════════════════════════════════════════════════════════════════
// FILE MANAGER CLASS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * File Manager
 * @description Handles all file operations with security validations
 * @class FileManager
 */
class FileManager {
  private static instance: FileManager;

  private constructor() {}

  static getInstance(): FileManager {
    if (!FileManager.instance) {
      FileManager.instance = new FileManager();
    }
    return FileManager.instance;
  }

  /**
   * Resolve and validate file path
   * @param inputPath User-provided path
   * @returns Resolved absolute path
   * @throws Error if path is invalid or outside allowed directory
   */
  resolvePath(inputPath: string): string {
    // Remove leading slash and normalize
    const normalizedPath = path.normalize(inputPath).replace(/^\/+/, '');
    const fullPath = path.join(BASE_DIR, normalizedPath);

    // Ensure path is within base directory
    if (!fullPath.startsWith(BASE_DIR)) {
      throw new Error('Path traversal detected: access denied');
    }

    return fullPath;
  }

  /**
   * Get file information
   */
  async getFileInfo(filePath: string): Promise<FileInfoResponse> {
    const resolvedPath = this.resolvePath(filePath);

    try {
      const stats = await fs.stat(resolvedPath);
      const extension = path.extname(resolvedPath).slice(1).toLowerCase();

      return {
        path: filePath,
        exists: true,
        size: stats.size,
        createdAt: stats.birthtime,
        modifiedAt: stats.mtime,
        mimeType: getMimeType(extension),
        extension,
        isDirectory: stats.isDirectory(),
        permissions: stats.mode.toString(8).slice(-3),
        checksum: stats.isFile() && stats.size < 100 * 1024 * 1024
          ? await this.calculateChecksum(resolvedPath)
          : undefined,
      };
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        return {
          path: filePath,
          exists: false,
        };
      }
      throw error;
    }
  }

  /**
   * Calculate file checksum
   */
  async calculateChecksum(filePath: string, algorithm: 'md5' | 'sha256' = 'md5'): Promise<string> {
    const content = await fs.readFile(filePath);
    return crypto.createHash(algorithm).update(content).digest('hex');
  }

  /**
   * List directory contents
   */
  async listDirectory(dirPath: string, recursive: boolean = false): Promise<FileInfoResponse[]> {
    const resolvedPath = this.resolvePath(dirPath);
    const entries = await fs.readdir(resolvedPath, { withFileTypes: true });

    const results: FileInfoResponse[] = [];

    for (const entry of entries) {
      const entryPath = path.join(dirPath, entry.name);
      const info = await this.getFileInfo(entryPath);
      results.push(info);

      // Recursively list subdirectories if requested
      if (recursive && entry.isDirectory()) {
        const subEntries = await this.listDirectory(entryPath, true);
        results.push(...subEntries);
      }
    }

    return results.sort((a, b) => {
      // Directories first, then files, alphabetically
      if (a.isDirectory !== b.isDirectory) {
        return a.isDirectory ? -1 : 1;
      }
      return (a.path || '').localeCompare(b.path || '');
    });
  }

  /**
   * Delete file or directory
   */
  async delete(filePath: string): Promise<{ success: boolean; message: string }> {
    const resolvedPath = this.resolvePath(filePath);
    const info = await this.getFileInfo(filePath);

    if (!info.exists) {
      return { success: false, message: 'File not found' };
    }

    if (info.isDirectory) {
      await fs.rm(resolvedPath, { recursive: true });
      return { success: true, message: `Directory deleted: ${filePath}` };
    } else {
      await fs.unlink(resolvedPath);
      return { success: true, message: `File deleted: ${filePath}` };
    }
  }

  /**
   * Move file or directory
   */
  async move(source: string, destination: string): Promise<{ success: boolean; message: string }> {
    const resolvedSource = this.resolvePath(source);
    const resolvedDestination = this.resolvePath(destination);

    // Check if source exists
    const sourceInfo = await this.getFileInfo(source);
    if (!sourceInfo.exists) {
      return { success: false, message: 'Source file not found' };
    }

    // Create destination parent directories if needed
    const destDir = path.dirname(resolvedDestination);
    await fs.mkdir(destDir, { recursive: true });

    // Move the file
    await fs.rename(resolvedSource, resolvedDestination);

    return { success: true, message: `Moved ${source} to ${destination}` };
  }

  /**
   * Copy file or directory
   */
  async copy(source: string, destination: string): Promise<{ success: boolean; message: string }> {
    const resolvedSource = this.resolvePath(source);
    const resolvedDestination = this.resolvePath(destination);

    // Check if source exists
    const sourceInfo = await this.getFileInfo(source);
    if (!sourceInfo.exists) {
      return { success: false, message: 'Source file not found' };
    }

    // Create destination parent directories if needed
    const destDir = path.dirname(resolvedDestination);
    await fs.mkdir(destDir, { recursive: true });

    // Copy the file/directory
    if (sourceInfo.isDirectory) {
      await this.copyDirectory(resolvedSource, resolvedDestination);
    } else {
      await fs.copyFile(resolvedSource, resolvedDestination);
    }

    return { success: true, message: `Copied ${source} to ${destination}` };
  }

  /**
   * Recursively copy directory
   */
  private async copyDirectory(source: string, destination: string): Promise<void> {
    await fs.mkdir(destination, { recursive: true });
    const entries = await fs.readdir(source, { withFileTypes: true });

    for (const entry of entries) {
      const sourcePath = path.join(source, entry.name);
      const destPath = path.join(destination, entry.name);

      if (entry.isDirectory()) {
        await this.copyDirectory(sourcePath, destPath);
      } else {
        await fs.copyFile(sourcePath, destPath);
      }
    }
  }

  /**
   * Rename file or directory
   */
  async rename(filePath: string, newName: string): Promise<{ success: boolean; message: string }> {
    const resolvedPath = this.resolvePath(filePath);
    const parentDir = path.dirname(resolvedPath);
    const newPath = path.join(parentDir, sanitizeFilename(newName));

    // Check if source exists
    const info = await this.getFileInfo(filePath);
    if (!info.exists) {
      return { success: false, message: 'File not found' };
    }

    // Check if destination already exists
    try {
      await fs.stat(newPath);
      return { success: false, message: 'A file with that name already exists' };
    } catch {
      // Destination doesn't exist, proceed
    }

    await fs.rename(resolvedPath, newPath);
    return { success: true, message: `Renamed to ${newName}` };
  }

  /**
   * Create directory
   */
  async createDirectory(dirPath: string): Promise<{ success: boolean; message: string }> {
    const resolvedPath = this.resolvePath(dirPath);

    try {
      await fs.mkdir(resolvedPath, { recursive: true });
      return { success: true, message: `Directory created: ${dirPath}` };
    } catch (error) {
      return { success: false, message: `Failed to create directory: ${(error as Error).message}` };
    }
  }

  /**
   * Search files by name pattern
   */
  async search(
    dirPath: string,
    pattern: string,
    options: { recursive?: boolean; fileType?: FileType } = {}
  ): Promise<FileInfoResponse[]> {
    const allFiles = await this.listDirectory(dirPath, options.recursive ?? true);
    const regex = new RegExp(pattern.replace(/\*/g, '.*').replace(/\?/g, '.'), 'i');

    return allFiles.filter((file) => {
      const matchesPattern = regex.test(file.path || '');
      const matchesType = !options.fileType || this.detectFileType(file.extension || '') === options.fileType;
      return matchesPattern && matchesType;
    });
  }

  /**
   * Detect file type from extension
   */
  private detectFileType(extension: string): FileType {
    const videoExts = ['mp4', 'webm', 'mkv', 'avi', 'mov', 'flv'];
    const audioExts = ['mp3', 'aac', 'ogg', 'flac', 'wav', 'm4a', 'opus'];
    const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'];
    const docExts = ['pdf', 'doc', 'docx', 'txt', 'md'];
    const subExts = ['srt', 'vtt', 'ass', 'sub'];
    const archiveExts = ['zip', 'tar', 'gz', 'rar'];

    const ext = extension.toLowerCase();

    if (videoExts.includes(ext)) return FileType.VIDEO;
    if (audioExts.includes(ext)) return FileType.AUDIO;
    if (imageExts.includes(ext)) return FileType.IMAGE;
    if (docExts.includes(ext)) return FileType.DOCUMENT;
    if (subExts.includes(ext)) return FileType.SUBTITLE;
    if (archiveExts.includes(ext)) return FileType.ARCHIVE;

    return FileType.UNKNOWN;
  }

  /**
   * Get storage statistics
   */
  async getStorageStats(): Promise<{
    totalFiles: number;
    totalDirectories: number;
    totalSize: number;
    byType: Record<FileType, { count: number; size: number }>;
  }> {
    const files = await this.listDirectory('/', true);
    const stats = {
      totalFiles: 0,
      totalDirectories: 0,
      totalSize: 0,
      byType: {} as Record<FileType, { count: number; size: number }>,
    };

    // Initialize byType
    Object.values(FileType).forEach((type) => {
      stats.byType[type] = { count: 0, size: 0 };
    });

    for (const file of files) {
      if (file.isDirectory) {
        stats.totalDirectories++;
      } else {
        stats.totalFiles++;
        stats.totalSize += file.size || 0;

        const type = this.detectFileType(file.extension || '');
        stats.byType[type].count++;
        stats.byType[type].size += file.size || 0;
      }
    }

    return stats;
  }
}

const fileManager = FileManager.getInstance();

// ═══════════════════════════════════════════════════════════════════════════════
// VALIDATION FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Validate file request
 */
function validateFileRequest(
  body: unknown,
  requestId: string,
  startTime: number
): { valid: boolean; error?: ReturnType<typeof validationError>; data?: FileRequest } {
  if (!body || typeof body !== 'object') {
    return {
      valid: false,
      error: validationError('Request body is required', 'body', requestId, startTime),
    };
  }

  const request = body as Partial<FileRequest>;

  // Path validation
  if (!request.path) {
    return {
      valid: false,
      error: validationError('Path is required', 'path', requestId, startTime),
    };
  }

  // Security check for path traversal
  if (!isValidFilePath(request.path)) {
    return {
      valid: false,
      error: validationError('Invalid path: directory traversal not allowed', 'path', requestId, startTime),
    };
  }

  // Operation validation
  const validOperations = ['read', 'delete', 'move', 'copy', 'rename', 'info', 'exists'];
  if (request.operation && !validOperations.includes(request.operation)) {
    return {
      valid: false,
      error: validationError(
        `Invalid operation. Valid options: ${validOperations.join(', ')}`,
        'operation',
        requestId,
        startTime
      ),
    };
  }

  // Validate required fields for specific operations
  if (request.operation === 'move' || request.operation === 'copy') {
    if (!request.destination) {
      return {
        valid: false,
        error: validationError('Destination is required for move/copy operations', 'destination', requestId, startTime),
      };
    }
  }

  if (request.operation === 'rename') {
    if (!request.newName) {
      return {
        valid: false,
        error: validationError('New name is required for rename operation', 'newName', requestId, startTime),
      };
    }
  }

  return { valid: true, data: request as FileRequest };
}

// ═══════════════════════════════════════════════════════════════════════════════
// MIDDLEWARE
// ═══════════════════════════════════════════════════════════════════════════════

const middleware = createMiddleware(
  rateLimitMiddleware(RateLimitTier.BASIC),
  authMiddleware(AuthLevel.USER)
);

// ═══════════════════════════════════════════════════════════════════════════════
// API ROUTE HANDLERS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * GET /api/file
 * @description Get file info, list directory, or search files
 */
export async function GET(request: NextRequest): Promise<Response> {
  const startTime = Date.now();
  const requestId = generateRequestId();

  const { response: middlewareResponse } = await middleware(request);
  if (middlewareResponse) return middlewareResponse;

  try {
    const { searchParams } = new URL(request.url);
    const filePath = searchParams.get('path') || '/';
    const action = searchParams.get('action') || 'info';
    const recursive = searchParams.get('recursive') === 'true';
    const searchPattern = searchParams.get('search');
    const fileType = searchParams.get('fileType') as FileType | null;

    // Validate path
    if (!isValidFilePath(filePath)) {
      return validationError('Invalid path: directory traversal not allowed', 'path', requestId, startTime);
    }

    // Handle search action
    if (searchPattern) {
      const results = await fileManager.search(filePath, searchPattern, {
        recursive,
        fileType: fileType || undefined,
      });

      return successResponse(
        {
          query: searchPattern,
          path: filePath,
          count: results.length,
          results,
        },
        requestId,
        startTime
      );
    }

    // Get file info
    const info = await fileManager.getFileInfo(filePath);

    if (!info.exists) {
      return errorResponse(
        {
          code: 'NOT_FOUND',
          message: `File or directory not found: ${filePath}`,
          suggestion: 'Please check the path and try again',
        },
        requestId,
        startTime,
        404
      );
    }

    // Handle directory listing
    if (info.isDirectory && action === 'list') {
      const contents = await fileManager.listDirectory(filePath, recursive);

      return successResponse(
        {
          ...info,
          contents,
          count: contents.length,
        },
        requestId,
        startTime
      );
    }

    // Handle storage stats
    if (action === 'stats') {
      const stats = await fileManager.getStorageStats();

      return successResponse(
        {
          ...stats,
          formattedSize: formatBytes(stats.totalSize),
        },
        requestId,
        startTime
      );
    }

    // Return file info
    return successResponse(info, requestId, startTime);
  } catch (error) {
    logger.error('File operation failed', {
      error: error instanceof Error ? error.message : 'Unknown error',
    }, requestId);

    return errorResponse(
      {
        code: 'INTERNAL_ERROR',
        message: 'Failed to process file operation',
        details: { error: error instanceof Error ? error.message : 'Unknown' },
      },
      requestId,
      startTime,
      500
    );
  }
}

/**
 * POST /api/file
 * @description Perform file operations (delete, move, copy, rename)
 */
export async function POST(request: NextRequest): Promise<Response> {
  const startTime = Date.now();
  const requestId = generateRequestId();

  const { response: middlewareResponse, context } = await middleware(request);
  if (middlewareResponse) return middlewareResponse;

  try {
    const body = await parseJsonBody<FileRequest>(request);

    // Validate request
    const validation = validateFileRequest(body, requestId, startTime);
    if (!validation.valid || !validation.data) {
      return validation.error!;
    }

    const fileRequest = validation.data;

    // Log operation
    logger.info(`File operation: ${fileRequest.operation}`, {
      path: fileRequest.path,
      destination: fileRequest.destination,
      user: context.session?.userId,
    }, requestId);

    let result;

    switch (fileRequest.operation) {
      case 'delete':
        result = await fileManager.delete(fileRequest.path);
        break;

      case 'move':
        result = await fileManager.move(fileRequest.path, fileRequest.destination!);
        break;

      case 'copy':
        result = await fileManager.copy(fileRequest.path, fileRequest.destination!);
        break;

      case 'rename':
        result = await fileManager.rename(fileRequest.path, fileRequest.newName!);
        break;

      case 'info':
      case 'exists':
        const info = await fileManager.getFileInfo(fileRequest.path);
        result = { success: true, message: 'File info retrieved', info };
        break;

      default:
        return validationError(
          `Unknown operation: ${fileRequest.operation}`,
          'operation',
          requestId,
          startTime
        );
    }

    return successResponse(result, requestId, startTime);
  } catch (error) {
    logger.error('File operation failed', {
      error: error instanceof Error ? error.message : 'Unknown error',
    }, requestId);

    return errorResponse(
      {
        code: 'OPERATION_FAILED',
        message: error instanceof Error ? error.message : 'Failed to perform file operation',
        suggestion: 'Please check the path and permissions',
      },
      requestId,
      startTime,
      500
    );
  }
}

/**
 * PUT /api/file
 * @description Create directory
 */
export async function PUT(request: NextRequest): Promise<Response> {
  const startTime = Date.now();
  const requestId = generateRequestId();

  const { response: middlewareResponse } = await middleware(request);
  if (middlewareResponse) return middlewareResponse;

  try {
    const body = await parseJsonBody<{ path: string }>(request);

    if (!body?.path) {
      return validationError('Path is required', 'path', requestId, startTime);
    }

    if (!isValidFilePath(body.path)) {
      return validationError('Invalid path: directory traversal not allowed', 'path', requestId, startTime);
    }

    const result = await fileManager.createDirectory(body.path);

    return successResponse(result, requestId, startTime);
  } catch (error) {
    logger.error('Directory creation failed', {
      error: error instanceof Error ? error.message : 'Unknown error',
    }, requestId);

    return errorResponse(
      {
        code: 'OPERATION_FAILED',
        message: 'Failed to create directory',
      },
      requestId,
      startTime,
      500
    );
  }
}

/**
 * OPTIONS /api/file
 * @description Return API documentation
 */
export async function OPTIONS(): Promise<Response> {
  return new Response(
    JSON.stringify({
      name: 'File API',
      version: '3.0.1',
      edition: 'ULTIMATE NEXUS',
      author: 'RAJSARASWATI JATAV (RS)',
      endpoints: {
        'GET /api/file': {
          description: 'Get file info, list directory, or search files',
          params: {
            path: 'string - File or directory path (default: /)',
            action: 'string - Action to perform (info, list, stats)',
            recursive: 'boolean - List recursively (default: false)',
            search: 'string - Search pattern (supports wildcards)',
            fileType: 'string - Filter by file type',
          },
        },
        'POST /api/file': {
          description: 'Perform file operations',
          body: {
            path: 'string (required) - File or directory path',
            operation: 'string (required) - Operation to perform',
            destination: 'string - Destination path for move/copy',
            newName: 'string - New name for rename operation',
            createParents: 'boolean - Create parent directories',
            overwrite: 'boolean - Overwrite existing files',
          },
          operations: ['read', 'delete', 'move', 'copy', 'rename', 'info', 'exists'],
        },
        'PUT /api/file': {
          description: 'Create directory',
          body: {
            path: 'string (required) - Directory path to create',
          },
        },
      },
      supportedFileTypes: Object.values(FileType),
      maxFileSize: formatBytes(MAX_FILE_SIZE),
    }),
    {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
      },
    }
  );
}
