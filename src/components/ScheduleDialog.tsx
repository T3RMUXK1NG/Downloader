/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   SCHEDULE DIALOG v3.0.1 ULTIMATE NEXUS                      ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Schedule downloads with date/time picker                       ║
 * ║  Features: One-time, recurring, cron expressions, timezone support           ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Calendar,
  Clock,
  Repeat,
  X,
  Check,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Info,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface ScheduleConfig {
  type: 'once' | 'daily' | 'weekly' | 'monthly' | 'custom';
  datetime?: Date;
  time?: string;
  daysOfWeek?: number[];
  dayOfMonth?: number;
  cronExpression?: string;
  timezone?: string;
}

export interface ScheduleDialogProps {
  /** Is dialog open */
  isOpen: boolean;
  /** On close */
  onClose: () => void;
  /** On schedule */
  onSchedule: (config: ScheduleConfig) => void;
  /** Initial configuration */
  initialConfig?: ScheduleConfig;
  /** Title */
  title?: string;
  /** Timezone options */
  timezones?: string[];
  /** Additional class names */
  className?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════════════════════════════

const DAYS_OF_WEEK = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

const defaultTimezones = [
  'UTC',
  'Asia/Kolkata',
  'America/New_York',
  'America/Los_Angeles',
  'Europe/London',
  'Europe/Paris',
  'Asia/Tokyo',
  'Asia/Shanghai',
];

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export const ScheduleDialog: React.FC<ScheduleDialogProps> = ({
  isOpen,
  onClose,
  onSchedule,
  initialConfig,
  title = 'Schedule Download',
  timezones = defaultTimezones,
  className,
}) => {
  const [config, setConfig] = React.useState<ScheduleConfig>(
    initialConfig || {
      type: 'once',
      datetime: new Date(),
      time: '00:00',
      daysOfWeek: [],
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    }
  );

  const [currentMonth, setCurrentMonth] = React.useState(new Date());
  const [error, setError] = React.useState<string | null>(null);

  // Reset form when dialog opens
  React.useEffect(() => {
    if (isOpen) {
      setConfig(
        initialConfig || {
          type: 'once',
          datetime: new Date(),
          time: '00:00',
          daysOfWeek: [],
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        }
      );
      setError(null);
    }
  }, [isOpen, initialConfig]);

  const handleSchedule = () => {
    // Validate
    if (config.type === 'once' && !config.datetime) {
      setError('Please select a date and time');
      return;
    }
    if (config.type === 'weekly' && (!config.daysOfWeek || config.daysOfWeek.length === 0)) {
      setError('Please select at least one day');
      return;
    }
    if (config.type === 'monthly' && !config.dayOfMonth) {
      setError('Please select a day of month');
      return;
    }
    if (config.type === 'custom' && !config.cronExpression) {
      setError('Please enter a cron expression');
      return;
    }

    onSchedule(config);
    onClose();
  };

  const handleDateSelect = (date: Date) => {
    const [hours, minutes] = (config.time || '00:00').split(':');
    date.setHours(parseInt(hours), parseInt(minutes));
    setConfig({ ...config, datetime: date });
  };

  const toggleDayOfWeek = (day: number) => {
    const current = config.daysOfWeek || [];
    const updated = current.includes(day) ? current.filter((d) => d !== day) : [...current, day];
    setConfig({ ...config, daysOfWeek: updated });
  };

  // Calendar generation
  const generateCalendarDays = () => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startOffset = firstDay.getDay();

    const days: (Date | null)[] = [];

    // Previous month padding
    for (let i = 0; i < startOffset; i++) {
      days.push(null);
    }

    // Current month days
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(new Date(year, month, i));
    }

    return days;
  };

  const isDateSelected = (date: Date) => {
    return config.datetime?.toDateString() === date.toDateString();
  };

  const isDateDisabled = (date: Date) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return date < today;
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          onClick={(e) => e.stopPropagation()}
          className={cn(
            'w-full max-w-lg rounded-2xl overflow-hidden',
            'bg-card/95 backdrop-blur-sm border border-border/50',
            'shadow-2xl',
            className
          )}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-border/50">
            <h2 className="text-lg font-semibold text-foreground">{title}</h2>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-muted/50 transition-colors"
            >
              <X className="w-5 h-5 text-muted-foreground" />
            </button>
          </div>

          {/* Content */}
          <div className="p-4 space-y-4 max-h-[70vh] overflow-y-auto">
            {/* Schedule type */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">Schedule Type</label>
              <div className="grid grid-cols-4 gap-2">
                {[
                  { value: 'once', label: 'Once' },
                  { value: 'daily', label: 'Daily' },
                  { value: 'weekly', label: 'Weekly' },
                  { value: 'monthly', label: 'Monthly' },
                ].map((option) => (
                  <motion.button
                    key={option.value}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setConfig({ ...config, type: option.value as ScheduleConfig['type'] })}
                    className={cn(
                      'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      config.type === option.value
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted/50 hover:bg-muted text-foreground'
                    )}
                  >
                    {option.label}
                  </motion.button>
                ))}
              </div>
            </div>

            {/* Time */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  <Clock className="w-4 h-4 inline mr-1" />
                  Time
                </label>
                <input
                  type="time"
                  value={config.time || '00:00'}
                  onChange={(e) => setConfig({ ...config, time: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  <Globe className="w-4 h-4 inline mr-1" />
                  Timezone
                </label>
                <select
                  value={config.timezone || timezones[0]}
                  onChange={(e) => setConfig({ ...config, timezone: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                >
                  {timezones.map((tz) => (
                    <option key={tz} value={tz}>
                      {tz}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Calendar for once/weekly/monthly */}
            {config.type === 'once' && (
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  <Calendar className="w-4 h-4 inline mr-1" />
                  Select Date
                </label>
                <div className="rounded-xl border border-border/50 p-3">
                  {/* Month navigation */}
                  <div className="flex items-center justify-between mb-3">
                    <button
                      onClick={() => setCurrentMonth(new Date(currentMonth.setMonth(currentMonth.getMonth() - 1)))}
                      className="p-1.5 rounded-lg hover:bg-muted/50"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </button>
                    <span className="text-sm font-medium">
                      {MONTHS[currentMonth.getMonth()]} {currentMonth.getFullYear()}
                    </span>
                    <button
                      onClick={() => setCurrentMonth(new Date(currentMonth.setMonth(currentMonth.getMonth() + 1)))}
                      className="p-1.5 rounded-lg hover:bg-muted/50"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Day headers */}
                  <div className="grid grid-cols-7 gap-1 mb-1">
                    {DAYS_OF_WEEK.map((day) => (
                      <div key={day} className="text-center text-xs text-muted-foreground py-1">
                        {day}
                      </div>
                    ))}
                  </div>

                  {/* Calendar grid */}
                  <div className="grid grid-cols-7 gap-1">
                    {generateCalendarDays().map((date, index) => (
                      <div key={index} className="aspect-square">
                        {date ? (
                          <motion.button
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            onClick={() => handleDateSelect(date)}
                            disabled={isDateDisabled(date)}
                            className={cn(
                              'w-full h-full rounded-lg text-sm flex items-center justify-center',
                              isDateSelected(date)
                                ? 'bg-primary text-primary-foreground'
                                : 'hover:bg-muted/50 text-foreground',
                              isDateDisabled(date) && 'text-muted-foreground/50 cursor-not-allowed'
                            )}
                          >
                            {date.getDate()}
                          </motion.button>
                        ) : (
                          <div />
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Weekly days selection */}
            {config.type === 'weekly' && (
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  <Repeat className="w-4 h-4 inline mr-1" />
                  Select Days
                </label>
                <div className="flex gap-1">
                  {DAYS_OF_WEEK.map((day, index) => (
                    <motion.button
                      key={day}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => toggleDayOfWeek(index)}
                      className={cn(
                        'flex-1 py-2 rounded-lg text-xs font-medium transition-colors',
                        config.daysOfWeek?.includes(index)
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted/50 hover:bg-muted text-foreground'
                      )}
                    >
                      {day}
                    </motion.button>
                  ))}
                </div>
              </div>
            )}

            {/* Monthly day selection */}
            {config.type === 'monthly' && (
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Day of Month
                </label>
                <select
                  value={config.dayOfMonth || 1}
                  onChange={(e) => setConfig({ ...config, dayOfMonth: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                >
                  {Array.from({ length: 31 }, (_, i) => i + 1).map((day) => (
                    <option key={day} value={day}>
                      {day}{day === 1 ? 'st' : day === 2 ? 'nd' : day === 3 ? 'rd' : 'th'} of the month
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Custom cron */}
            {config.type === 'custom' && (
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Cron Expression
                </label>
                <input
                  type="text"
                  value={config.cronExpression || ''}
                  onChange={(e) => setConfig({ ...config, cronExpression: e.target.value })}
                  placeholder="0 0 * * *"
                  className="w-full px-3 py-2 rounded-lg border border-input bg-background text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
                <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                  <Info className="w-3 h-3" />
                  Format: minute hour day month weekday
                </p>
              </div>
            )}

            {/* Error message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-3 rounded-lg bg-red-500/10 border border-red-500/20"
              >
                <p className="text-sm text-red-500 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  {error}
                </p>
              </motion.div>
            )}

            {/* Summary */}
            {config.datetime && (
              <div className="p-3 rounded-lg bg-muted/30">
                <p className="text-sm text-muted-foreground">
                  Scheduled for:{' '}
                  <span className="font-medium text-foreground">
                    {config.datetime.toLocaleDateString()} at {config.time}
                  </span>
                </p>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex justify-end gap-2 p-4 border-t border-border/50 bg-muted/30">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg border border-input hover:bg-muted/50 text-sm transition-colors"
            >
              Cancel
            </button>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleSchedule}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium"
            >
              <Check className="w-4 h-4" />
              Schedule
            </motion.button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ScheduleDialog;
