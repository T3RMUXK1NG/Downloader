/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   VIDEO PLAYER v3.0.1 ULTIMATE NEXUS                         ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Video preview player with custom controls                      ║
 * ║  Features: Play/pause, volume, fullscreen, progress, keyboard controls      ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Play,
  Pause,
  Volume2,
  VolumeX,
  Maximize,
  Minimize,
  SkipBack,
  SkipForward,
  Settings,
  Loader2,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface VideoPlayerProps {
  /** Video source URL */
  src: string;
  /** Poster image URL */
  poster?: string;
  /** Video title */
  title?: string;
  /** Auto play on mount */
  autoPlay?: boolean;
  /** Mute on mount */
  muted?: boolean;
  /** Loop video */
  loop?: boolean;
  /** Show controls */
  showControls?: boolean;
  /** Additional class names */
  className?: string;
  /** On play callback */
  onPlay?: () => void;
  /** On pause callback */
  onPause?: () => void;
  /** On ended callback */
  onEnded?: () => void;
  /** On time update callback */
  onTimeUpdate?: (currentTime: number, duration: number) => void;
}

// ═══════════════════════════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

const formatTime = (seconds: number): string => {
  if (!isFinite(seconds) || seconds < 0) return '0:00';
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export const VideoPlayer: React.FC<VideoPlayerProps> = ({
  src,
  poster,
  title,
  autoPlay = false,
  muted = false,
  loop = false,
  showControls = true,
  className,
  onPlay,
  onPause,
  onEnded,
  onTimeUpdate,
}) => {
  const videoRef = React.useRef<HTMLVideoElement>(null);
  const containerRef = React.useRef<HTMLDivElement>(null);
  const progressRef = React.useRef<HTMLDivElement>(null);

  const [isPlaying, setIsPlaying] = React.useState(false);
  const [isMuted, setIsMuted] = React.useState(muted);
  const [volume, setVolume] = React.useState(1);
  const [currentTime, setCurrentTime] = React.useState(0);
  const [duration, setDuration] = React.useState(0);
  const [isBuffering, setIsBuffering] = React.useState(false);
  const [isFullscreen, setIsFullscreen] = React.useState(false);
  const [showControlsOverlay, setShowControlsOverlay] = React.useState(true);
  const [isDragging, setIsDragging] = React.useState(false);

  const controlsTimeoutRef = React.useRef<NodeJS.Timeout>();

  // Hide controls after inactivity
  const resetControlsTimeout = React.useCallback(() => {
    if (controlsTimeoutRef.current) {
      clearTimeout(controlsTimeoutRef.current);
    }
    setShowControlsOverlay(true);
    if (isPlaying) {
      controlsTimeoutRef.current = setTimeout(() => {
        setShowControlsOverlay(false);
      }, 3000);
    }
  }, [isPlaying]);

  // Event handlers
  const handlePlay = React.useCallback(() => {
    setIsPlaying(true);
    onPlay?.();
    resetControlsTimeout();
  }, [onPlay, resetControlsTimeout]);

  const handlePause = React.useCallback(() => {
    setIsPlaying(false);
    onPause?.();
    setShowControlsOverlay(true);
  }, [onPause]);

  const handleEnded = React.useCallback(() => {
    setIsPlaying(false);
    onEnded?.();
    setShowControlsOverlay(true);
  }, [onEnded]);

  const handleTimeUpdate = React.useCallback(() => {
    const video = videoRef.current;
    if (video) {
      setCurrentTime(video.currentTime);
      onTimeUpdate?.(video.currentTime, video.duration);
    }
  }, [onTimeUpdate]);

  const handleLoadedMetadata = React.useCallback(() => {
    const video = videoRef.current;
    if (video) {
      setDuration(video.duration);
    }
  }, []);

  const handleWaiting = React.useCallback(() => {
    setIsBuffering(true);
  }, []);

  const handleCanPlay = React.useCallback(() => {
    setIsBuffering(false);
  }, []);

  // Toggle play/pause
  const togglePlay = React.useCallback(() => {
    const video = videoRef.current;
    if (!video) return;
    if (isPlaying) {
      video.pause();
    } else {
      video.play();
    }
  }, [isPlaying]);

  // Toggle mute
  const toggleMute = React.useCallback(() => {
    const video = videoRef.current;
    if (video) {
      video.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  }, [isMuted]);

  // Handle volume change
  const handleVolumeChange = React.useCallback((newVolume: number) => {
    const video = videoRef.current;
    if (video) {
      video.volume = newVolume;
      setVolume(newVolume);
      if (newVolume === 0) {
        setIsMuted(true);
        video.muted = true;
      } else {
        setIsMuted(false);
        video.muted = false;
      }
    }
  }, []);

  // Seek to position
  const seekTo = React.useCallback((time: number) => {
    const video = videoRef.current;
    if (video) {
      video.currentTime = Math.max(0, Math.min(time, duration));
    }
  }, [duration]);

  // Handle progress bar click
  const handleProgressClick = React.useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const rect = progressRef.current?.getBoundingClientRect();
    if (rect && duration > 0) {
      const pos = (e.clientX - rect.left) / rect.width;
      seekTo(pos * duration);
    }
  }, [duration, seekTo]);

  // Skip forward/backward
  const skip = React.useCallback((seconds: number) => {
    seekTo(currentTime + seconds);
  }, [currentTime, seekTo]);

  // Toggle fullscreen
  const toggleFullscreen = React.useCallback(async () => {
    const container = containerRef.current;
    if (!container) return;

    try {
      if (!document.fullscreenElement) {
        await container.requestFullscreen();
        setIsFullscreen(true);
      } else {
        await document.exitFullscreen();
        setIsFullscreen(false);
      }
    } catch {
      // Fullscreen not supported
    }
  }, []);

  // Keyboard controls
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (document.activeElement?.tagName === 'INPUT') return;

      switch (e.key) {
        case ' ':
        case 'k':
          e.preventDefault();
          togglePlay();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          skip(-10);
          break;
        case 'ArrowRight':
          e.preventDefault();
          skip(10);
          break;
        case 'ArrowUp':
          e.preventDefault();
          handleVolumeChange(Math.min(1, volume + 0.1));
          break;
        case 'ArrowDown':
          e.preventDefault();
          handleVolumeChange(Math.max(0, volume - 0.1));
          break;
        case 'm':
          toggleMute();
          break;
        case 'f':
          toggleFullscreen();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [togglePlay, skip, handleVolumeChange, volume, toggleMute, toggleFullscreen]);

  // Fullscreen change listener
  React.useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div
      ref={containerRef}
      className={cn(
        'relative group bg-black rounded-xl overflow-hidden',
        isFullscreen && 'rounded-none',
        className
      )}
      onMouseMove={resetControlsTimeout}
      onMouseLeave={() => isPlaying && setShowControlsOverlay(false)}
      role="figure"
      aria-label={title || 'Video player'}
    >
      {/* Video element */}
      <video
        ref={videoRef}
        src={src}
        poster={poster}
        autoPlay={autoPlay}
        muted={muted}
        loop={loop}
        playsInline
        className="w-full h-full object-contain"
        onPlay={handlePlay}
        onPause={handlePause}
        onEnded={handleEnded}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onWaiting={handleWaiting}
        onCanPlay={handleCanPlay}
        onClick={togglePlay}
      />

      {/* Loading overlay */}
      <AnimatePresence>
        {isBuffering && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 flex items-center justify-center bg-black/30"
          >
            <Loader2 className="w-12 h-12 text-white animate-spin" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Controls overlay */}
      {showControls && (
        <AnimatePresence>
          {(showControlsOverlay || !isPlaying) && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 flex flex-col justify-end bg-gradient-to-t from-black/80 via-transparent to-transparent"
            >
              {/* Center play button */}
              <div className="absolute inset-0 flex items-center justify-center">
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={togglePlay}
                  className="w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center hover:bg-white/30 transition-colors"
                  aria-label={isPlaying ? 'Pause' : 'Play'}
                >
                  {isPlaying ? (
                    <Pause className="w-8 h-8 sm:w-10 sm:h-10 text-white" fill="white" />
                  ) : (
                    <Play className="w-8 h-8 sm:w-10 sm:h-10 text-white ml-1" fill="white" />
                  )}
                </motion.button>
              </div>

              {/* Bottom controls */}
              <div className="p-3 sm:p-4 space-y-2 sm:space-y-3">
                {/* Progress bar */}
                <div
                  ref={progressRef}
                  className="relative h-1.5 sm:h-2 bg-white/30 rounded-full cursor-pointer group/progress"
                  onClick={handleProgressClick}
                  role="slider"
                  aria-label="Video progress"
                  aria-valuemin={0}
                  aria-valuemax={duration}
                  aria-valuenow={currentTime}
                >
                  <motion.div
                    className="absolute top-0 left-0 h-full bg-primary rounded-full"
                    style={{ width: `${progressPercent}%` }}
                  />
                  <motion.div
                    className="absolute top-1/2 -translate-y-1/2 w-3 h-3 sm:w-4 sm:h-4 bg-white rounded-full shadow-lg opacity-0 group-hover/progress:opacity-100 transition-opacity"
                    style={{ left: `calc(${progressPercent}% - 6px)` }}
                  />
                </div>

                {/* Controls row */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 sm:gap-3">
                    {/* Skip back */}
                    <button
                      onClick={() => skip(-10)}
                      className="p-1.5 sm:p-2 rounded-lg hover:bg-white/20 transition-colors"
                      aria-label="Skip back 10 seconds"
                    >
                      <SkipBack className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                    </button>

                    {/* Play/Pause */}
                    <button
                      onClick={togglePlay}
                      className="p-2 sm:p-2.5 rounded-full bg-white/20 hover:bg-white/30 transition-colors"
                      aria-label={isPlaying ? 'Pause' : 'Play'}
                    >
                      {isPlaying ? (
                        <Pause className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                      ) : (
                        <Play className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                      )}
                    </button>

                    {/* Skip forward */}
                    <button
                      onClick={() => skip(10)}
                      className="p-1.5 sm:p-2 rounded-lg hover:bg-white/20 transition-colors"
                      aria-label="Skip forward 10 seconds"
                    >
                      <SkipForward className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                    </button>

                    {/* Volume */}
                    <div className="hidden sm:flex items-center gap-2">
                      <button
                        onClick={toggleMute}
                        className="p-1.5 sm:p-2 rounded-lg hover:bg-white/20 transition-colors"
                        aria-label={isMuted ? 'Unmute' : 'Mute'}
                      >
                        {isMuted || volume === 0 ? (
                          <VolumeX className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                        ) : (
                          <Volume2 className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                        )}
                      </button>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={isMuted ? 0 : volume}
                        onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
                        className="w-16 sm:w-20 h-1 bg-white/30 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-white"
                        aria-label="Volume"
                      />
                    </div>

                    {/* Time */}
                    <span className="text-xs sm:text-sm text-white font-mono">
                      {formatTime(currentTime)} / {formatTime(duration)}
                    </span>
                  </div>

                  <div className="flex items-center gap-1 sm:gap-2">
                    {/* Fullscreen */}
                    <button
                      onClick={toggleFullscreen}
                      className="p-1.5 sm:p-2 rounded-lg hover:bg-white/20 transition-colors"
                      aria-label={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
                    >
                      {isFullscreen ? (
                        <Minimize className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                      ) : (
                        <Maximize className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      )}
    </div>
  );
};

export default VideoPlayer;
