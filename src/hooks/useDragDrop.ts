/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    USE DRAG DROP HOOK v3.0.1 ULTIMATE NEXUS                   ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: File drag & drop management hook                               ║
 * ║  Features: File validation, multi-file, preview, progress, callbacks        ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module hooks/useDragDrop
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface DroppedFile {
  id: string;
  file: File;
  name: string;
  size: number;
  type: string;
  extension: string;
  preview?: string;
  progress: number;
  status: 'pending' | 'uploading' | 'completed' | 'error';
  error?: string;
}

export interface DragDropOptions {
  /** Accepted file types (MIME types or extensions) */
  accept?: string[];
  /** Maximum file size in bytes */
  maxSize?: number;
  /** Maximum number of files */
  maxFiles?: number;
  /** Allow multiple files */
  multiple?: boolean;
  /** Enable file preview */
  enablePreview?: boolean;
  /** Auto-upload on drop */
  autoUpload?: boolean;
  /** Custom upload function */
  onUpload?: (files: DroppedFile[]) => Promise<void>;
  /** Callback when files are dropped */
  onDrop?: (files: DroppedFile[]) => void;
  /** Callback when drag enters */
  onDragEnter?: () => void;
  /** Callback when drag leaves */
  onDragLeave?: () => void;
  /** Callback on error */
  onError?: (error: string) => void;
}

export interface UseDragDropReturn {
  /** Ref to attach to drop zone */
  dropRef: React.RefObject<HTMLDivElement | null>;
  /** Is dragging over */
  isDragging: boolean;
  /** Dropped files */
  files: DroppedFile[];
  /** Add files programmatically */
  addFiles: (fileList: FileList | File[]) => void;
  /** Remove a file */
  removeFile: (id: string) => void;
  /** Clear all files */
  clearFiles: () => void;
  /** Upload files */
  upload: () => Promise<void>;
  /** Get root props */
  getRootProps: () => React.HTMLAttributes<HTMLDivElement>;
  /** Get input props */
  getInputProps: () => React.InputHTMLAttributes<HTMLInputElement>;
  /** Has errors */
  hasErrors: boolean;
  /** Total size */
  totalSize: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// HOOK IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * useDragDrop Hook
 * @description File drag & drop management with validation and preview
 * @param options Hook options
 * @returns Drag & drop controls and state
 */
export function useDragDrop(options: DragDropOptions = {}): UseDragDropReturn {
  const {
    accept = [],
    maxSize = 100 * 1024 * 1024, // 100MB
    maxFiles = 10,
    multiple = true,
    enablePreview = true,
    autoUpload = false,
    onUpload,
    onDrop,
    onDragEnter,
    onDragLeave,
    onError,
  } = options;

  // State
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState<DroppedFile[]>([]);

  // Refs
  const dropRef = useRef<HTMLDivElement>(null);
  const dragCountRef = useRef(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // ═══════════════════════════════════════════════════════════════════════════
  // FILE VALIDATION
  // ═══════════════════════════════════════════════════════════════════════════

  const validateFile = useCallback(
    (file: File): string | null => {
      // Check file size
      if (file.size > maxSize) {
        return `File "${file.name}" exceeds maximum size of ${formatBytes(maxSize)}`;
      }

      // Check file type
      if (accept.length > 0) {
        const extension = file.name.split('.').pop()?.toLowerCase() || '';
        const mimeType = file.type;

        const isAccepted = accept.some((type) => {
          if (type.startsWith('.')) {
            return extension === type.slice(1).toLowerCase();
          }
          if (type.includes('*')) {
            return mimeType.startsWith(type.replace('*', ''));
          }
          return mimeType === type;
        });

        if (!isAccepted) {
          return `File type "${extension}" is not accepted`;
        }
      }

      return null;
    },
    [accept, maxSize]
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // CREATE DROPPED FILE
  // ═══════════════════════════════════════════════════════════════════════════

  const createDroppedFile = useCallback(
    async (file: File): Promise<DroppedFile> => {
      const id = `file_${Date.now()}_${Math.random().toString(36).substring(2, 10)}`;
      const extension = file.name.split('.').pop()?.toLowerCase() || '';

      const droppedFile: DroppedFile = {
        id,
        file,
        name: file.name,
        size: file.size,
        type: file.type,
        extension,
        progress: 0,
        status: 'pending',
      };

      // Generate preview for images
      if (enablePreview && file.type.startsWith('image/')) {
        droppedFile.preview = await generatePreview(file);
      }

      return droppedFile;
    },
    [enablePreview]
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // ADD FILES
  // ═══════════════════════════════════════════════════════════════════════════

  const addFiles = useCallback(
    async (fileList: FileList | File[]) => {
      const fileArray = Array.from(fileList);

      // Check max files
      if (files.length + fileArray.length > maxFiles) {
        onError?.(`Maximum ${maxFiles} files allowed`);
        return;
      }

      const newFiles: DroppedFile[] = [];
      const errors: string[] = [];

      for (const file of fileArray) {
        const error = validateFile(file);
        if (error) {
          errors.push(error);
          continue;
        }

        const droppedFile = await createDroppedFile(file);
        newFiles.push(droppedFile);
      }

      if (errors.length > 0) {
        onError?.(errors.join('\n'));
      }

      if (newFiles.length > 0) {
        setFiles((prev) => [...prev, ...newFiles]);
        onDrop?.(newFiles);

        if (autoUpload && onUpload) {
          uploadFiles(newFiles);
        }
      }
    },
    [files.length, maxFiles, validateFile, createDroppedFile, onError, onDrop, autoUpload, onUpload]
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // REMOVE FILE
  // ═══════════════════════════════════════════════════════════════════════════

  const removeFile = useCallback((id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  }, []);

  const clearFiles = useCallback(() => {
    setFiles([]);
  }, []);

  // ═══════════════════════════════════════════════════════════════════════════
  // UPLOAD FILES
  // ═══════════════════════════════════════════════════════════════════════════

  const uploadFiles = useCallback(
    async (filesToUpload: DroppedFile[]) => {
      if (!onUpload) return;

      // Mark as uploading
      setFiles((prev) =>
        prev.map((f) =>
          filesToUpload.some((ftu) => ftu.id === f.id)
            ? { ...f, status: 'uploading' as const }
            : f
        )
      );

      try {
        await onUpload(filesToUpload);

        // Mark as completed
        setFiles((prev) =>
          prev.map((f) =>
            filesToUpload.some((ftu) => ftu.id === f.id)
              ? { ...f, status: 'completed' as const, progress: 100 }
              : f
          )
        );
      } catch (error) {
        // Mark as error
        setFiles((prev) =>
          prev.map((f) =>
            filesToUpload.some((ftu) => ftu.id === f.id)
              ? {
                  ...f,
                  status: 'error' as const,
                  error: error instanceof Error ? error.message : 'Upload failed',
                }
              : f
          )
        );
      }
    },
    [onUpload]
  );

  const upload = useCallback(async () => {
    const pendingFiles = files.filter((f) => f.status === 'pending');
    if (pendingFiles.length > 0) {
      await uploadFiles(pendingFiles);
    }
  }, [files, uploadFiles]);

  // ═══════════════════════════════════════════════════════════════════════════
  // DRAG & DROP HANDLERS
  // ═══════════════════════════════════════════════════════════════════════════

  const handleDragEnter = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      event.stopPropagation();

      dragCountRef.current++;
      if (event.dataTransfer.items.length > 0) {
        setIsDragging(true);
        onDragEnter?.();
      }
    },
    [onDragEnter]
  );

  const handleDragLeave = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      event.stopPropagation();

      dragCountRef.current--;
      if (dragCountRef.current === 0) {
        setIsDragging(false);
        onDragLeave?.();
      }
    },
    [onDragLeave]
  );

  const handleDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      event.stopPropagation();

      setIsDragging(false);
      dragCountRef.current = 0;

      const droppedFiles = event.dataTransfer.files;
      if (droppedFiles.length > 0) {
        addFiles(droppedFiles);
      }
    },
    [addFiles]
  );

  const handleFileSelect = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const selectedFiles = event.target.files;
      if (selectedFiles && selectedFiles.length > 0) {
        addFiles(selectedFiles);
      }
      // Reset input
      if (inputRef.current) {
        inputRef.current.value = '';
      }
    },
    [addFiles]
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // BIND EVENTS
  // ═══════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    const dropZone = dropRef.current;
    if (!dropZone) return;

    const handleDragEnterEvent = (e: DragEvent) => {
      e.preventDefault();
      dragCountRef.current++;
      if (e.dataTransfer?.items.length) {
        setIsDragging(true);
        onDragEnter?.();
      }
    };

    const handleDragLeaveEvent = (e: DragEvent) => {
      e.preventDefault();
      dragCountRef.current--;
      if (dragCountRef.current === 0) {
        setIsDragging(false);
        onDragLeave?.();
      }
    };

    const handleDragOverEvent = (e: DragEvent) => {
      e.preventDefault();
    };

    const handleDropEvent = (e: DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      dragCountRef.current = 0;
      if (e.dataTransfer?.files.length) {
        addFiles(e.dataTransfer.files);
      }
    };

    dropZone.addEventListener('dragenter', handleDragEnterEvent);
    dropZone.addEventListener('dragleave', handleDragLeaveEvent);
    dropZone.addEventListener('dragover', handleDragOverEvent);
    dropZone.addEventListener('drop', handleDropEvent);

    return () => {
      dropZone.removeEventListener('dragenter', handleDragEnterEvent);
      dropZone.removeEventListener('dragleave', handleDragLeaveEvent);
      dropZone.removeEventListener('dragover', handleDragOverEvent);
      dropZone.removeEventListener('drop', handleDropEvent);
    };
  }, [addFiles, onDragEnter, onDragLeave]);

  // ═══════════════════════════════════════════════════════════════════════════
  // COMPUTED VALUES
  // ═══════════════════════════════════════════════════════════════════════════

  const hasErrors = files.some((f) => f.status === 'error');
  const totalSize = files.reduce((sum, f) => sum + f.size, 0);

  // ═══════════════════════════════════════════════════════════════════════════
  // PROPS GETTERS
  // ═══════════════════════════════════════════════════════════════════════════

  const getRootProps = useCallback((): React.HTMLAttributes<HTMLDivElement> => ({
    onDragEnter: handleDragEnter,
    onDragLeave: handleDragLeave,
    onDragOver: handleDragOver,
    onDrop: handleDrop,
  }), [handleDragEnter, handleDragLeave, handleDragOver, handleDrop]);

  const getInputProps = useCallback((): React.InputHTMLAttributes<HTMLInputElement> => ({
    type: 'file',
    multiple,
    accept: accept.join(','),
    onChange: handleFileSelect,
    style: { display: 'none' },
  }), [multiple, accept, handleFileSelect]);

  // ═══════════════════════════════════════════════════════════════════════════
  // RETURN
  // ═══════════════════════════════════════════════════════════════════════════

  return {
    dropRef,
    isDragging,
    files,
    addFiles,
    removeFile,
    clearFiles,
    upload,
    getRootProps,
    getInputProps,
    hasErrors,
    totalSize,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Generate image preview
 */
function generatePreview(file: File): Promise<string> {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.readAsDataURL(file);
  });
}

/**
 * Format bytes to human readable
 */
function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

export default useDragDrop;
