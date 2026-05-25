/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   PROGRESS BAR v3.0.1 ULTIMATE NEXUS                         ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Animated progress bar with multiple styles                     ║
 * ║  Features: Gradient, animated, striped, indeterminate, circular              ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface ProgressBarProps {
  /** Current value */
  value: number;
  /** Maximum value */
  max?: number;
  /** Progress variant */
  variant?: 'default' | 'gradient' | 'striped' | 'glow';
  /** Color theme */
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'info';
  /** Size */
  size?: 'sm' | 'md' | 'lg';
  /** Show percentage label */
  showLabel?: boolean;
  /** Label position */
  labelPosition?: 'inside' | 'outside' | 'tooltip';
  /** Custom label */
  label?: string;
  /** Animated stripes */
  animated?: boolean;
  /** Indeterminate loading state */
  indeterminate?: boolean;
  /** Additional class names */
  className?: string;
  /** Custom color (overrides color prop) */
  customColor?: string;
  /** On click handler */
  onClick?: (value: number, percent: number) => void;
}

// ═══════════════════════════════════════════════════════════════════════════════
// COLOR MAPPINGS
// ═══════════════════════════════════════════════════════════════════════════════

const colorClasses: Record<string, { bg: string; gradient: string; glow: string }> = {
  primary: {
    bg: 'bg-primary',
    gradient: 'from-primary via-primary/80 to-primary',
    glow: 'shadow-primary/50',
  },
  success: {
    bg: 'bg-green-500',
    gradient: 'from-green-500 via-emerald-500 to-green-500',
    glow: 'shadow-green-500/50',
  },
  warning: {
    bg: 'bg-amber-500',
    gradient: 'from-amber-500 via-orange-500 to-amber-500',
    glow: 'shadow-amber-500/50',
  },
  danger: {
    bg: 'bg-red-500',
    gradient: 'from-red-500 via-rose-500 to-red-500',
    glow: 'shadow-red-500/50',
  },
  info: {
    bg: 'bg-blue-500',
    gradient: 'from-blue-500 via-cyan-500 to-blue-500',
    glow: 'shadow-blue-500/50',
  },
};

const sizeClasses: Record<string, string> = {
  sm: 'h-1.5',
  md: 'h-2.5',
  lg: 'h-4',
};

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  variant = 'default',
  color = 'primary',
  size = 'md',
  showLabel = false,
  labelPosition = 'outside',
  label,
  animated = false,
  indeterminate = false,
  className,
  customColor,
  onClick,
}) => {
  const percent = Math.min(100, Math.max(0, (value / max) * 100));
  const colorStyle = colorClasses[color] || colorClasses.primary;
  const sizeClass = sizeClasses[size] || sizeClasses.md;

  const handleBarClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (onClick) {
      const rect = e.currentTarget.getBoundingClientRect();
      const clickPercent = (e.clientX - rect.left) / rect.width;
      onClick(clickPercent * max, clickPercent * 100);
    }
  };

  const renderProgressContent = () => {
    if (indeterminate) {
      return (
        <motion.div
          className={cn(
            'h-full rounded-full',
            variant === 'gradient' && `bg-gradient-to-r ${colorStyle.gradient}`,
            variant === 'glow' && `bg-gradient-to-r ${colorStyle.gradient} shadow-lg ${colorStyle.glow}`,
            variant === 'default' && colorStyle.bg,
            variant === 'striped' && colorStyle.bg
          )}
          style={customColor ? { backgroundColor: customColor } : undefined}
          animate={{
            x: ['-100%', '200%'],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'linear',
          }}
        />
      );
    }

    return (
      <motion.div
        className={cn(
          'h-full rounded-full relative overflow-hidden',
          variant === 'gradient' && `bg-gradient-to-r ${colorStyle.gradient}`,
          variant === 'glow' && `bg-gradient-to-r ${colorStyle.gradient} shadow-lg ${colorStyle.glow}`,
          variant === 'default' && colorStyle.bg,
          variant === 'striped' &&
            `${colorStyle.bg} bg-[length:1rem_1rem] bg-[linear-gradient(45deg,rgba(255,255,255,.15)_25%,transparent_25%,transparent_50%,rgba(255,255,255,.15)_50%,rgba(255,255,255,.15)_75%,transparent_75%,transparent)]`
        )}
        style={customColor ? { backgroundColor: customColor } : undefined}
        initial={{ width: 0 }}
        animate={{ width: `${percent}%` }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
      >
        {/* Animated stripes */}
        {animated && variant === 'striped' && (
          <motion.div
            className="absolute inset-0 bg-[length:1rem_1rem] bg-[linear-gradient(45deg,rgba(255,255,255,.15)_25%,transparent_25%,transparent_50%,rgba(255,255,255,.15)_50%,rgba(255,255,255,.15)_75%,transparent_75%,transparent)]"
            animate={{ backgroundPosition: ['0rem 0', '2rem 0'] }}
            transition={{ duration: 0.5, repeat: Infinity, ease: 'linear' }}
          />
        )}

        {/* Glow animation */}
        {variant === 'glow' && (
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
            animate={{ x: ['-100%', '100%'] }}
            transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          />
        )}

        {/* Inside label */}
        {showLabel && labelPosition === 'inside' && percent > 15 && (
          <span className="absolute inset-0 flex items-center justify-center text-xs font-medium text-white">
            {label || `${Math.round(percent)}%`}
          </span>
        )}
      </motion.div>
    );
  };

  return (
    <div className={cn('w-full', className)}>
      {/* Outside label */}
      {showLabel && labelPosition === 'outside' && (
        <div className="flex justify-between mb-1.5">
          <span className="text-xs font-medium text-foreground">{label}</span>
          <span className="text-xs font-medium text-muted-foreground">{Math.round(percent)}%</span>
        </div>
      )}

      {/* Progress bar container */}
      <div
        className={cn(
          'relative w-full overflow-hidden rounded-full bg-muted/50 dark:bg-muted/30',
          sizeClass,
          onClick && 'cursor-pointer'
        )}
        onClick={handleBarClick}
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
        aria-label={label || `Progress: ${Math.round(percent)}%`}
      >
        {renderProgressContent()}

        {/* Tooltip label */}
        <AnimatePresence>
          {showLabel && labelPosition === 'tooltip' && percent > 0 && !indeterminate && (
            <motion.div
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -5 }}
              className="absolute -top-7 px-2 py-0.5 rounded text-xs font-medium bg-popover text-popover-foreground shadow-md"
              style={{ left: `calc(${percent}% - 20px)` }}
            >
              {Math.round(percent)}%
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// CIRCULAR PROGRESS COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export interface CircularProgressProps {
  /** Current value */
  value: number;
  /** Maximum value */
  max?: number;
  /** Size in pixels */
  size?: number;
  /** Stroke width */
  strokeWidth?: number;
  /** Color theme */
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'info';
  /** Show percentage inside */
  showLabel?: boolean;
  /** Custom label */
  label?: string;
  /** Indeterminate loading state */
  indeterminate?: boolean;
  /** Additional class names */
  className?: string;
  /** Custom color */
  customColor?: string;
}

export const CircularProgress: React.FC<CircularProgressProps> = ({
  value,
  max = 100,
  size = 48,
  strokeWidth = 4,
  color = 'primary',
  showLabel = false,
  label,
  indeterminate = false,
  className,
  customColor,
}) => {
  const percent = Math.min(100, Math.max(0, (value / max) * 100));
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (percent / 100) * circumference;

  const colorMap: Record<string, string> = {
    primary: 'stroke-primary',
    success: 'stroke-green-500',
    warning: 'stroke-amber-500',
    danger: 'stroke-red-500',
    info: 'stroke-blue-500',
  };

  const strokeColor = colorMap[color] || colorMap.primary;

  return (
    <div
      className={cn('relative inline-flex items-center justify-center', className)}
      style={{ width: size, height: size }}
      role="progressbar"
      aria-valuenow={value}
      aria-valuemin={0}
      aria-valuemax={max}
    >
      {/* Background circle */}
      <svg className="absolute inset-0 -rotate-90" width={size} height={size}>
        <circle
          className="fill-none stroke-muted/30"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
        />
      </svg>

      {/* Progress circle */}
      <svg className="absolute inset-0 -rotate-90" width={size} height={size}>
        {indeterminate ? (
          <motion.circle
            className={cn('fill-none', strokeColor)}
            cx={size / 2}
            cy={size / 2}
            r={radius}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={`${circumference * 0.25} ${circumference * 0.75}`}
            style={customColor ? { stroke: customColor } : undefined}
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          />
        ) : (
          <motion.circle
            className={cn('fill-none', strokeColor)}
            cx={size / 2}
            cy={size / 2}
            r={radius}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            style={customColor ? { stroke: customColor } : undefined}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        )}
      </svg>

      {/* Center label */}
      {showLabel && !indeterminate && (
        <span className="text-xs font-medium text-foreground">
          {label || `${Math.round(percent)}%`}
        </span>
      )}
    </div>
  );
};

export default ProgressBar;
