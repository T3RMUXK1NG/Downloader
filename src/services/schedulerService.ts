/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   SCHEDULER SERVICE v3.0.1 ULTIMATE NEXUS                     ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Elite task scheduling service                                  ║
 * ║  Features: Cron, One-time, Recurring, Priority, Retry, Queue management      ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module services/schedulerService
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

import { logger, generateDownloadId } from '@/lib/utils';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES & INTERFACES
// ═══════════════════════════════════════════════════════════════════════════════

export interface ScheduleOptions {
  name: string;
  type: ScheduleType;
  schedule: string | Date;
  handler: () => Promise<unknown>;
  priority?: SchedulePriority;
  maxRetries?: number;
  retryDelay?: number;
  timeout?: number;
  enabled?: boolean;
  tags?: string[];
  metadata?: Record<string, unknown>;
}

export interface ScheduledTask {
  id: string;
  name: string;
  type: ScheduleType;
  schedule: string | Date;
  handler: () => Promise<unknown>;
  priority: SchedulePriority;
  maxRetries: number;
  retryDelay: number;
  timeout: number;
  enabled: boolean;
  tags: string[];
  metadata: Record<string, unknown>;
  status: TaskStatus;
  lastRun?: Date;
  nextRun?: Date;
  lastResult?: TaskResult;
  runCount: number;
  failureCount: number;
}

export interface TaskResult {
  success: boolean;
  data?: unknown;
  error?: string;
  duration: number;
  timestamp: Date;
}

export interface ScheduleStats {
  total: number;
  enabled: number;
  disabled: number;
  running: number;
  pending: number;
  failed: number;
}

export enum ScheduleType {
  ONE_TIME = 'one_time',
  RECURRING = 'recurring',
  CRON = 'cron',
  INTERVAL = 'interval',
  DELAYED = 'delayed',
}

export enum SchedulePriority {
  LOW = 0,
  NORMAL = 1,
  HIGH = 2,
  CRITICAL = 3,
}

export enum TaskStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  PAUSED = 'paused',
  CANCELLED = 'cancelled',
}

// ═══════════════════════════════════════════════════════════════════════════════
// SCHEDULER SERVICE CLASS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Elite Scheduler Service
 * @class SchedulerService
 * @description Comprehensive task scheduling
 */
export class SchedulerService {
  private static instance: SchedulerService;
  private tasks: Map<string, ScheduledTask> = new Map();
  private intervals: Map<string, NodeJS.Timeout> = new Map();
  private timeouts: Map<string, NodeJS.Timeout> = new Map();
  private running: Set<string> = new Set();
  private maxConcurrent: number = 5;

  private constructor() {
    this.startMaintenanceInterval();
  }

  static getInstance(): SchedulerService {
    if (!SchedulerService.instance) {
      SchedulerService.instance = new SchedulerService();
    }
    return SchedulerService.instance;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // SCHEDULE METHODS
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Schedule a task
   */
  schedule(options: ScheduleOptions): string {
    const id = `task_${generateDownloadId().substring(3)}`;
    
    const task: ScheduledTask = {
      id,
      name: options.name,
      type: options.type,
      schedule: options.schedule,
      handler: options.handler,
      priority: options.priority ?? SchedulePriority.NORMAL,
      maxRetries: options.maxRetries ?? 3,
      retryDelay: options.retryDelay ?? 1000,
      timeout: options.timeout ?? 30000,
      enabled: options.enabled ?? true,
      tags: options.tags ?? [],
      metadata: options.metadata ?? {},
      status: TaskStatus.PENDING,
      runCount: 0,
      failureCount: 0,
    };

    this.tasks.set(id, task);
    this.scheduleNextRun(id);
    
    logger.info(`Scheduled task: ${options.name} (${id})`);
    return id;
  }

  /**
   * Schedule one-time task
   */
  scheduleOnce(name: string, date: Date, handler: () => Promise<unknown>): string {
    return this.schedule({
      name,
      type: ScheduleType.ONE_TIME,
      schedule: date,
      handler,
    });
  }

  /**
   * Schedule recurring task
   */
  scheduleRecurring(
    name: string,
    intervalMs: number,
    handler: () => Promise<unknown>
  ): string {
    return this.schedule({
      name,
      type: ScheduleType.INTERVAL,
      schedule: intervalMs.toString(),
      handler,
    });
  }

  /**
   * Schedule cron task
   */
  scheduleCron(name: string, cronExpression: string, handler: () => Promise<unknown>): string {
    return this.schedule({
      name,
      type: ScheduleType.CRON,
      schedule: cronExpression,
      handler,
    });
  }

  /**
   * Schedule delayed task
   */
  scheduleDelayed(name: string, delayMs: number, handler: () => Promise<unknown>): string {
    return this.schedule({
      name,
      type: ScheduleType.DELAYED,
      schedule: delayMs.toString(),
      handler,
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // TASK MANAGEMENT
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Cancel a task
   */
  cancel(taskId: string): boolean {
    const task = this.tasks.get(taskId);
    if (!task) return false;

    // Clear timers
    const interval = this.intervals.get(taskId);
    if (interval) clearInterval(interval);
    
    const timeout = this.timeouts.get(taskId);
    if (timeout) clearTimeout(timeout);

    task.status = TaskStatus.CANCELLED;
    this.intervals.delete(taskId);
    this.timeouts.delete(taskId);
    
    logger.info(`Cancelled task: ${task.name} (${taskId})`);
    return true;
  }

  /**
   * Pause a task
   */
  pause(taskId: string): boolean {
    const task = this.tasks.get(taskId);
    if (!task || !task.enabled) return false;

    task.enabled = false;
    task.status = TaskStatus.PAUSED;
    
    // Clear timers
    const interval = this.intervals.get(taskId);
    if (interval) clearInterval(interval);
    this.intervals.delete(taskId);
    
    logger.info(`Paused task: ${task.name} (${taskId})`);
    return true;
  }

  /**
   * Resume a task
   */
  resume(taskId: string): boolean {
    const task = this.tasks.get(taskId);
    if (!task || task.enabled) return false;

    task.enabled = true;
    task.status = TaskStatus.PENDING;
    this.scheduleNextRun(taskId);
    
    logger.info(`Resumed task: ${task.name} (${taskId})`);
    return true;
  }

  /**
   * Run task immediately
   */
  async runNow(taskId: string): Promise<TaskResult> {
    const task = this.tasks.get(taskId);
    if (!task) {
      return {
        success: false,
        error: 'Task not found',
        duration: 0,
        timestamp: new Date(),
      };
    }

    return this.executeTask(taskId);
  }

  /**
   * Update task schedule
   */
  updateSchedule(taskId: string, newSchedule: string | Date): boolean {
    const task = this.tasks.get(taskId);
    if (!task) return false;

    task.schedule = newSchedule;
    
    // Reschedule
    const interval = this.intervals.get(taskId);
    if (interval) clearInterval(interval);
    
    const timeout = this.timeouts.get(taskId);
    if (timeout) clearTimeout(timeout);

    this.scheduleNextRun(taskId);
    return true;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // TASK EXECUTION
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Schedule next run
   */
  private scheduleNextRun(taskId: string): void {
    const task = this.tasks.get(taskId);
    if (!task || !task.enabled) return;

    switch (task.type) {
      case ScheduleType.ONE_TIME:
      case ScheduleType.DELAYED:
        this.scheduleOneTime(taskId);
        break;
      case ScheduleType.INTERVAL:
        this.scheduleInterval(taskId);
        break;
      case ScheduleType.CRON:
        this.scheduleCronTask(taskId);
        break;
    }
  }

  private scheduleOneTime(taskId: string): void {
    const task = this.tasks.get(taskId);
    if (!task) return;

    let delay: number;
    
    if (task.type === ScheduleType.DELAYED) {
      delay = parseInt(task.schedule as string);
    } else {
      delay = (task.schedule as Date).getTime() - Date.now();
    }

    if (delay <= 0) {
      this.executeTask(taskId);
      return;
    }

    task.nextRun = new Date(Date.now() + delay);

    const timeout = setTimeout(() => {
      this.executeTask(taskId);
      this.timeouts.delete(taskId);
    }, delay);

    this.timeouts.set(taskId, timeout);
  }

  private scheduleInterval(taskId: string): void {
    const task = this.tasks.get(taskId);
    if (!task) return;

    const interval = parseInt(task.schedule as string);
    task.nextRun = new Date(Date.now() + interval);

    const timer = setInterval(() => {
      if (this.running.size < this.maxConcurrent) {
        this.executeTask(taskId);
      }
      task.nextRun = new Date(Date.now() + interval);
    }, interval);

    this.intervals.set(taskId, timer);
  }

  private scheduleCronTask(taskId: string): void {
    const task = this.tasks.get(taskId);
    if (!task) return;

    // Simplified cron parsing (just for demo)
    const cronExpr = task.schedule as string;
    const parts = cronExpr.split(' ');
    
    // Default: every minute
    let intervalMs = 60000;
    
    if (parts.length >= 1 && parts[0] !== '*') {
      intervalMs = parseInt(parts[0]) * 60000;
    }

    task.nextRun = new Date(Date.now() + intervalMs);

    const timer = setInterval(() => {
      if (this.running.size < this.maxConcurrent) {
        this.executeTask(taskId);
      }
      task.nextRun = new Date(Date.now() + intervalMs);
    }, intervalMs);

    this.intervals.set(taskId, timer);
  }

  /**
   * Execute task with retry logic
   */
  private async executeTask(taskId: string): Promise<TaskResult> {
    const task = this.tasks.get(taskId);
    if (!task) {
      return {
        success: false,
        error: 'Task not found',
        duration: 0,
        timestamp: new Date(),
      };
    }

    if (this.running.has(taskId)) {
      return {
        success: false,
        error: 'Task already running',
        duration: 0,
        timestamp: new Date(),
      };
    }

    this.running.add(taskId);
    task.status = TaskStatus.RUNNING;
    task.lastRun = new Date();

    const startTime = Date.now();
    let attempts = 0;
    let lastError: string | undefined;

    while (attempts <= task.maxRetries) {
      try {
        // Create timeout promise
        const timeoutPromise = new Promise<never>((_, reject) => {
          setTimeout(() => reject(new Error('Task timeout')), task.timeout);
        });

        // Execute with timeout
        const result = await Promise.race([
          task.handler(),
          timeoutPromise,
        ]);

        task.status = TaskStatus.COMPLETED;
        task.runCount++;
        task.lastResult = {
          success: true,
          data: result,
          duration: Date.now() - startTime,
          timestamp: new Date(),
        };

        this.running.delete(taskId);
        
        // For one-time tasks, remove after completion
        if (task.type === ScheduleType.ONE_TIME || task.type === ScheduleType.DELAYED) {
          this.tasks.delete(taskId);
        }

        return task.lastResult;
      } catch (error) {
        attempts++;
        lastError = error instanceof Error ? error.message : 'Unknown error';
        
        if (attempts <= task.maxRetries) {
          await this.delay(task.retryDelay * attempts);
        }
      }
    }

    // All retries failed
    task.status = TaskStatus.FAILED;
    task.failureCount++;
    task.lastResult = {
      success: false,
      error: lastError,
      duration: Date.now() - startTime,
      timestamp: new Date(),
    };

    this.running.delete(taskId);
    
    logger.error(`Task failed: ${task.name} (${taskId})`, { error: lastError });
    return task.lastResult;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // QUERY METHODS
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Get task by ID
   */
  getTask(taskId: string): ScheduledTask | undefined {
    return this.tasks.get(taskId);
  }

  /**
   * Get all tasks
   */
  getAllTasks(): ScheduledTask[] {
    return Array.from(this.tasks.values());
  }

  /**
   * Get tasks by status
   */
  getTasksByStatus(status: TaskStatus): ScheduledTask[] {
    return Array.from(this.tasks.values()).filter(t => t.status === status);
  }

  /**
   * Get tasks by tag
   */
  getTasksByTag(tag: string): ScheduledTask[] {
    return Array.from(this.tasks.values()).filter(t => t.tags.includes(tag));
  }

  /**
   * Get upcoming tasks
   */
  getUpcomingTasks(limit: number = 10): ScheduledTask[] {
    return Array.from(this.tasks.values())
      .filter(t => t.enabled && t.nextRun)
      .sort((a, b) => (a.nextRun?.getTime() || 0) - (b.nextRun?.getTime() || 0))
      .slice(0, limit);
  }

  /**
   * Get statistics
   */
  getStats(): ScheduleStats {
    const tasks = Array.from(this.tasks.values());
    return {
      total: tasks.length,
      enabled: tasks.filter(t => t.enabled).length,
      disabled: tasks.filter(t => !t.enabled).length,
      running: this.running.size,
      pending: tasks.filter(t => t.status === TaskStatus.PENDING).length,
      failed: tasks.filter(t => t.status === TaskStatus.FAILED).length,
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // MAINTENANCE
  // ═══════════════════════════════════════════════════════════════════════════

  private startMaintenanceInterval(): void {
    setInterval(() => {
      // Clean up completed one-time tasks older than 1 hour
      const oneHourAgo = Date.now() - 3600000;
      
      for (const [id, task] of this.tasks.entries()) {
        if (
          (task.type === ScheduleType.ONE_TIME || task.type === ScheduleType.DELAYED) &&
          task.status === TaskStatus.COMPLETED &&
          task.lastRun &&
          task.lastRun.getTime() < oneHourAgo
        ) {
          this.tasks.delete(id);
        }
      }
    }, 3600000);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Clear all tasks
   */
  clearAll(): void {
    for (const interval of this.intervals.values()) {
      clearInterval(interval);
    }
    for (const timeout of this.timeouts.values()) {
      clearTimeout(timeout);
    }
    this.intervals.clear();
    this.timeouts.clear();
    this.tasks.clear();
    this.running.clear();
  }
}

// Export singleton instance
export const schedulerService = SchedulerService.getInstance();

// ═══════════════════════════════════════════════════════════════════════════════
// CONVENIENCE FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

export function scheduleTask(
  name: string,
  schedule: string | Date,
  handler: () => Promise<unknown>
): string {
  if (schedule instanceof Date) {
    return schedulerService.scheduleOnce(name, schedule, handler);
  } else {
    return schedulerService.scheduleCron(name, schedule, handler);
  }
}

export function scheduleEvery(
  name: string,
  intervalMs: number,
  handler: () => Promise<unknown>
): string {
  return schedulerService.scheduleRecurring(name, intervalMs, handler);
}

export function scheduleIn(
  name: string,
  delayMs: number,
  handler: () => Promise<unknown>
): string {
  return schedulerService.scheduleDelayed(name, delayMs, handler);
}
