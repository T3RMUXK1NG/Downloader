/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   AUDIO WAVEFORM v3.0.1 ULTIMATE NEXUS                       ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATEV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Audio visualization with animated waveform                     ║
 * ║  Features: Real-time visualization, play/pause, progress, duration          ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Play, Pause, Volume2, VolumeX, SkipBack, SkipForward } from 'lucide-react';
import { cn } from '@/lib/utils';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface AudioWaveformProps {
  /** Audio source URL */
  src: string;
  /** Audio title */
  title?: string;
  /** Artist name */
  artist?: string;
  /** Album art URL */
  albumArt?: string;
  /** Waveform bars (0-1 normalized) */
  waveform?: number[];
  /** Bar count for generated waveform */
  barCount?: number;
  /** Bar color */
  barColor?: string;
  /** Background color */
  backgroundColor?: string;
  /** Auto play */
  autoPlay?: boolean;
  /** On play callback */
  onPlay?: () => void;
  /** On pause callback */
  onPause?: () => void;
  /** On time update */
  onTimeUpdate?: (currentTime: number, duration: number) => void;
  /** Additional class names */
  className?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

const formatTime = (seconds: number): string => {
  if (!isFinite(seconds) || seconds < 0) return '0:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const generateWaveform = (count: number): number[] => {
  return Array.from({ length: count }, () => 0.2 + Math.random() * 0.8);
};

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export const AudioWaveform: React.FC<AudioWaveformProps> = ({
  src,
  title,
  artist,
  albumArt,
  waveform,
  barCount = 50,
  barColor = 'rgb(34, 197, 94)',
  backgroundColor = 'rgba(0, 0, 0, 0.1)',
  autoPlay = false,
  onPlay,
  onPause,
  onTimeUpdate,
  className,
}) => {
  const audioRef = React.useRef<HTMLAudioElement>(null);
  const animationRef = React.useRef<number>();

  const [isPlaying, setIsPlaying] = React.useState(false);
  const [isMuted, setIsMuted] = React.useState(false);
  const [currentTime, setCurrentTime] = React.useState(0);
  const [duration, setDuration] = React.useState(0);
  const [analyserData, setAnalyserData] = React.useState<number[]>([]);

  const bars = waveform || generateWaveform(barCount);
  const progress = duration > 0 ? currentTime / duration : 0;
  const progressIndex = Math.floor(progress * bars.length);

  // Audio context for visualization
  const [audioContext, setAudioContext] = React.useState<AudioContext | null>(null);
  const [analyser, setAnalyser] = React.useState<AnalyserNode | null>(null);

  const initAudioContext = React.useCallback(() => {
    if (!audioContext && audioRef.current) {
      const ctx = new AudioContext();
      const analyserNode = ctx.createAnalyser();
      analyserNode.fftSize = 256;
      const source = ctx.createMediaElementSource(audioRef.current);
      source.connect(analyserNode);
      analyserNode.connect(ctx.destination);
      setAudioContext(ctx);
      setAnalyser(analyserNode);
    }
  }, [audioContext]);

  const updateAnalyser = React.useCallback(() => {
    if (analyser && isPlaying) {
      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      analyser.getByteFrequencyData(dataArray);
      const normalized = Array.from(dataArray.slice(0, 50)).map((v) => v / 255);
      setAnalyserData(normalized);
      animationRef.current = requestAnimationFrame(updateAnalyser);
    }
  }, [analyser, isPlaying]);

  React.useEffect(() => {
    if (isPlaying && analyser) {
      updateAnalyser();
    }
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isPlaying, analyser, updateAnalyser]);

  const handlePlay = React.useCallback(() => {
    initAudioContext();
    setIsPlaying(true);
    onPlay?.();
  }, [initAudioContext, onPlay]);

  const handlePause = React.useCallback(() => {
    setIsPlaying(false);
    onPause?.();
  }, [onPause]);

  const handleTimeUpdate = React.useCallback(() => {
    const audio = audioRef.current;
    if (audio) {
      setCurrentTime(audio.currentTime);
      onTimeUpdate?.(audio.currentTime, audio.duration);
    }
  }, [onTimeUpdate]);

  const handleLoadedMetadata = React.useCallback(() => {
    const audio = audioRef.current;
    if (audio) {
      setDuration(audio.duration);
    }
  }, []);

  const togglePlay = React.useCallback(() => {
    const audio = audioRef.current;
    if (audio) {
      if (isPlaying) {
        audio.pause();
      } else {
        audio.play();
      }
    }
  }, [isPlaying]);

  const toggleMute = React.useCallback(() => {
    const audio = audioRef.current;
    if (audio) {
      audio.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  }, [isMuted]);

  const seekTo = React.useCallback((time: number) => {
    const audio = audioRef.current;
    if (audio) {
      audio.currentTime = Math.max(0, Math.min(time, duration));
    }
  }, [duration]);

  const skip = React.useCallback((seconds: number) => {
    seekTo(currentTime + seconds);
  }, [currentTime, seekTo]);

  const handleWaveformClick = React.useCallback((index: number) => {
    seekTo((index / bars.length) * duration);
  }, [bars.length, duration, seekTo]);

  return (
    <div
      className={cn(
        'relative rounded-2xl overflow-hidden p-4 sm:p-6',
        'bg-gradient-to-br from-card/80 to-card/40 backdrop-blur-sm',
        'border border-border/50 shadow-xl',
        className
      )}
      role="figure"
      aria-label={`Audio player: ${title || 'Unknown'}`}
    >
      <audio
        ref={audioRef}
        src={src}
        autoPlay={autoPlay}
        onPlay={handlePlay}
        onPause={handlePause}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
      />

      <div className="flex items-center gap-4 sm:gap-6">
        {/* Album art */}
        {albumArt && (
          <motion.img
            src={albumArt}
            alt={title || 'Album art'}
            className="w-16 h-16 sm:w-20 sm:h-20 rounded-xl object-cover shadow-lg"
            animate={isPlaying ? { rotate: [0, 360] } : {}}
            transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
          />
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Title and artist */}
          {(title || artist) && (
            <div className="mb-3 sm:mb-4">
              {title && (
                <h3 className="font-semibold text-foreground truncate text-sm sm:text-base">
                  {title}
                </h3>
              )}
              {artist && (
                <p className="text-xs sm:text-sm text-muted-foreground truncate">{artist}</p>
              )}
            </div>
          )}

          {/* Waveform */}
          <div
            className="relative h-12 sm:h-16 rounded-lg overflow-hidden"
            style={{ backgroundColor }}
            role="slider"
            aria-label="Audio progress"
            aria-valuemin={0}
            aria-valuemax={duration}
            aria-valuenow={currentTime}
          >
            <div className="absolute inset-0 flex items-center justify-center gap-0.5 sm:gap-1 px-1">
              {bars.map((bar, index) => {
                const isActive = index <= progressIndex;
                const height = isPlaying && analyserData[index]
                  ? analyserData[index] * 100
                  : bar * 100;

                return (
                  <motion.button
                    key={index}
                    className="flex-1 h-full flex items-center justify-center"
                    onClick={() => handleWaveformClick(index)}
                    whileHover={{ scaleY: 1.2 }}
                    aria-label={`Seek to ${Math.round((index / bars.length) * duration)} seconds`}
                  >
                    <motion.div
                      className="w-full rounded-full"
                      style={{
                        height: `${height}%`,
                        backgroundColor: isActive ? barColor : `${barColor}40`,
                        minHeight: '4px',
                      }}
                      animate={
                        isPlaying
                          ? {
                              height: [
                                `${height}%`,
                                `${(analyserData[index] || bar) * 100}%`,
                                `${height}%`,
                              ],
                            }
                          : {}
                      }
                      transition={{
                        duration: 0.1,
                        ease: 'easeOut',
                      }}
                    />
                  </motion.button>
                );
              })}
            </div>

            {/* Progress line */}
            <motion.div
              className="absolute top-0 bottom-0 w-0.5 bg-white/50"
              style={{ left: `${progress * 100}%` }}
            />
          </div>

          {/* Controls */}
          <div className="flex items-center justify-between mt-3 sm:mt-4">
            <div className="flex items-center gap-1 sm:gap-2">
              {/* Skip back */}
              <button
                onClick={() => skip(-10)}
                className="p-1.5 sm:p-2 rounded-lg hover:bg-muted/50 transition-colors"
                aria-label="Skip back 10 seconds"
              >
                <SkipBack className="w-4 h-4 sm:w-5 sm:h-5 text-muted-foreground" />
              </button>

              {/* Play/Pause */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={togglePlay}
                className="p-2.5 sm:p-3 rounded-full bg-primary text-primary-foreground shadow-lg hover:shadow-xl transition-shadow"
                aria-label={isPlaying ? 'Pause' : 'Play'}
              >
                {isPlaying ? (
                  <Pause className="w-5 h-5 sm:w-6 sm:h-6" />
                ) : (
                  <Play className="w-5 h-5 sm:w-6 sm:h-6 ml-0.5" />
                )}
              </motion.button>

              {/* Skip forward */}
              <button
                onClick={() => skip(10)}
                className="p-1.5 sm:p-2 rounded-lg hover:bg-muted/50 transition-colors"
                aria-label="Skip forward 10 seconds"
              >
                <SkipForward className="w-4 h-4 sm:w-5 sm:h-5 text-muted-foreground" />
              </button>
            </div>

            {/* Time and volume */}
            <div className="flex items-center gap-2 sm:gap-4">
              <span className="text-xs sm:text-sm text-muted-foreground font-mono">
                {formatTime(currentTime)} / {formatTime(duration)}
              </span>

              <button
                onClick={toggleMute}
                className="p-1.5 sm:p-2 rounded-lg hover:bg-muted/50 transition-colors"
                aria-label={isMuted ? 'Unmute' : 'Mute'}
              >
                {isMuted ? (
                  <VolumeX className="w-4 h-4 sm:w-5 sm:h-5 text-muted-foreground" />
                ) : (
                  <Volume2 className="w-4 h-4 sm:w-5 sm:h-5 text-muted-foreground" />
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AudioWaveform;
