/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   SPEED LIMITER v3.0.1 ULTIMATE NEXUS                        ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Download speed control with presets and custom input           ║
 * ║  Features: Slider, presets, custom input, real-time stats, graph             ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Gauge, Zap, Unlimited, Settings, TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '@/lib/utils';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface SpeedPreset {
  label: string;
  value: number; // in KB/s, 0 = unlimited
  description?: string;
}

export interface SpeedLimiterProps {
  /** Current speed limit in KB/s (0 = unlimited) */
  value?: number;
  /** On speed change */
  onChange?: (value: number) => void;
  /** Speed presets */
  presets?: SpeedPreset[];
  /** Maximum allowed speed in KB/s */
  maxSpeed?: number;
  /** Show custom input */
  showCustomInput?: boolean;
  /** Show current download stats */
  currentSpeed?: number;
  /** Show speed graph */
  showGraph?: boolean;
  /** Speed history for graph */
  speedHistory?: number[];
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Disabled state */
  disabled?: boolean;
  /** Additional class names */
  className?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// DEFAULT PRESETS
// ═══════════════════════════════════════════════════════════════════════════════

const defaultPresets: SpeedPreset[] = [
  { label: 'Unlimited', value: 0, description: 'No speed limit' },
  { label: '10 MB/s', value: 10240, description: 'Fast downloads' },
  { label: '5 MB/s', value: 5120, description: 'High speed' },
  { label: '2 MB/s', value: 2048, description: 'Medium speed' },
  { label: '1 MB/s', value: 1024, description: 'Standard speed' },
  { label: '512 KB/s', value: 512, description: 'Slow connection' },
  { label: '256 KB/s', value: 256, description: 'Very slow' },
];

// ═══════════════════════════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

const formatSpeed = (kbps: number): string => {
  if (kbps === 0) return 'Unlimited';
  if (kbps >= 1024) {
    return `${(kbps / 1024).toFixed(1)} MB/s`;
  }
  return `${kbps} KB/s`;
};

const parseSpeedInput = (input: string): number => {
  const match = input.match(/^(\d+(?:\.\d+)?)\s*(kb|mb|gb)?$/i);
  if (!match) return 0;
  const value = parseFloat(match[1]);
  const unit = (match[2] || 'kb').toLowerCase();
  switch (unit) {
    case 'mb':
      return Math.round(value * 1024);
    case 'gb':
      return Math.round(value * 1024 * 1024);
    default:
      return Math.round(value);
  }
};

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export const SpeedLimiter: React.FC<SpeedLimiterProps> = ({
  value = 0,
  onChange,
  presets = defaultPresets,
  maxSpeed = 102400, // 100 MB/s
  showCustomInput = true,
  currentSpeed = 0,
  showGraph = false,
  speedHistory = [],
  size = 'md',
  disabled = false,
  className,
}) => {
  const [customValue, setCustomValue] = React.useState('');
  const [showPresets, setShowPresets] = React.useState(false);
  const dropdownRef = React.useRef<HTMLDivElement>(null);

  const selectedPreset = presets.find((p) => p.value === value);
  const isActiveLimit = value > 0;

  // Close dropdown on outside click
  React.useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowPresets(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handlePresetSelect = (preset: SpeedPreset) => {
    onChange?.(preset.value);
    setShowPresets(false);
  };

  const handleCustomSubmit = () => {
    const parsed = parseSpeedInput(customValue);
    onChange?.(parsed);
    setCustomValue('');
  };

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange?.(Number(e.target.value));
  };

  // Calculate limit percentage for display
  const limitPercent = maxSpeed > 0 ? Math.min(100, (value / maxSpeed) * 100) : 0;

  return (
    <div
      ref={dropdownRef}
      className={cn(
        'rounded-2xl overflow-hidden',
        'bg-card/80 backdrop-blur-sm border border-border/50',
        'shadow-xl',
        className
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-border/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={cn(
              'w-10 h-10 rounded-xl flex items-center justify-center',
              isActiveLimit ? 'bg-amber-500/20' : 'bg-primary/20'
            )}>
              {isActiveLimit ? (
                <Gauge className="w-5 h-5 text-amber-500" />
              ) : (
                <Unlimited className="w-5 h-5 text-primary" />
              )}
            </div>
            <div>
              <h3 className="font-semibold text-foreground">Speed Limit</h3>
              <p className="text-xs text-muted-foreground">
                {selectedPreset ? selectedPreset.label : formatSpeed(value)}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Current speed indicator */}
            {currentSpeed > 0 && (
              <div className="px-3 py-1.5 rounded-lg bg-muted/50 flex items-center gap-2">
                <Zap className="w-4 h-4 text-amber-500" />
                <span className="text-sm font-medium">{formatSpeed(currentSpeed)}</span>
              </div>
            )}

            {/* Toggle presets */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowPresets(!showPresets)}
              disabled={disabled}
              className={cn(
                'px-3 py-1.5 rounded-lg border transition-colors',
                showPresets ? 'bg-primary text-primary-foreground' : 'border-border hover:bg-muted/50'
              )}
            >
              <Settings className="w-4 h-4" />
            </motion.button>
          </div>
        </div>
      </div>

      {/* Slider */}
      <div className="p-4 space-y-3">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Limit</span>
          <span className="font-medium text-foreground">{formatSpeed(value)}</span>
        </div>

        <div className="relative">
          <input
            type="range"
            min={0}
            max={maxSpeed}
            step={256}
            value={value}
            onChange={handleSliderChange}
            disabled={disabled}
            className={cn(
              'w-full h-2 rounded-full appearance-none cursor-pointer',
              'bg-muted/50 [&::-webkit-slider-thumb]:appearance-none',
              '[&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4',
              '[&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary',
              '[&::-webkit-slider-thumb]:shadow-lg [&::-webkit-slider-thumb]:cursor-pointer',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          />

          {/* Gradient overlay */}
          <div
            className="absolute inset-0 h-2 rounded-full bg-gradient-to-r from-primary/80 to-primary pointer-events-none"
            style={{ width: `${limitPercent}%` }}
          />
        </div>

        <div className="flex justify-between text-xs text-muted-foreground">
          <span>Unlimited</span>
          <span>{formatSpeed(maxSpeed)}</span>
        </div>
      </div>

      {/* Speed graph */}
      {showGraph && speedHistory.length > 0 && (
        <div className="px-4 pb-4">
          <div className="h-16 rounded-lg bg-muted/30 p-2">
            <svg className="w-full h-full" preserveAspectRatio="none">
              <defs>
                <linearGradient id="speedGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="rgb(34, 197, 94)" stopOpacity="0.5" />
                  <stop offset="100%" stopColor="rgb(34, 197, 94)" stopOpacity="0" />
                </linearGradient>
              </defs>
              <motion.path
                d={`M 0 ${16 - (speedHistory[0] || 0) * 16} ${speedHistory
                  .map((s, i) => `L ${(i / (speedHistory.length - 1)) * 100}% ${16 - s * 16}`)
                  .join(' ')} L 100% 16 L 0 16 Z`}
                fill="url(#speedGradient)"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              />
              <motion.path
                d={`M 0 ${16 - (speedHistory[0] || 0) * 16} ${speedHistory
                  .map((s, i) => `L ${(i / (speedHistory.length - 1)) * 100}% ${16 - s * 16}`)
                  .join(' ')}`}
                fill="none"
                stroke="rgb(34, 197, 94)"
                strokeWidth="2"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
              />
            </svg>
          </div>
        </div>
      )}

      {/* Presets dropdown */}
      <AnimatePresence>
        {showPresets && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="border-t border-border/50 overflow-hidden"
          >
            <div className="p-4 space-y-3">
              {/* Custom input */}
              {showCustomInput && (
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={customValue}
                    onChange={(e) => setCustomValue(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleCustomSubmit()}
                    placeholder="e.g., 5 MB/s"
                    disabled={disabled}
                    className="flex-1 px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleCustomSubmit}
                    disabled={disabled || !customValue}
                    className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium disabled:opacity-50"
                  >
                    Apply
                  </motion.button>
                </div>
              )}

              {/* Preset buttons */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {presets.map((preset) => (
                  <motion.button
                    key={preset.value}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handlePresetSelect(preset)}
                    disabled={disabled}
                    className={cn(
                      'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      value === preset.value
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted/50 hover:bg-muted text-foreground'
                    )}
                  >
                    {preset.label}
                  </motion.button>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Stats footer */}
      {currentSpeed > 0 && (
        <div className="px-4 py-3 border-t border-border/50 bg-muted/30">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <div className="flex items-center gap-1">
              <TrendingUp className="w-3 h-3 text-green-500" />
              <span>Current: {formatSpeed(currentSpeed)}</span>
            </div>
            {isActiveLimit && (
              <div className="flex items-center gap-1">
                <TrendingDown className="w-3 h-3 text-amber-500" />
                <span>Limit: {formatSpeed(value)}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SpeedLimiter;
