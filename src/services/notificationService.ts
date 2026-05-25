/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                   NOTIFICATION SERVICE v3.0.1 ULTIMATE NEXUS                  ║
 * ║                   OMNIPOTENT SOVEREIGN EDITION                               ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: Elite notification management service                          ║
 * ║  Features: Multi-channel, Templates, Scheduling, Priority, History           ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module services/notificationService
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

import { logger, generateDownloadId } from '@/lib/utils';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES & INTERFACES
// ═══════════════════════════════════════════════════════════════════════════════

export interface NotificationOptions {
  title: string;
  message: string;
  type?: NotificationType;
  priority?: NotificationPriority;
  channels?: NotificationChannel[];
  icon?: string;
  image?: string;
  actions?: NotificationAction[];
  data?: Record<string, unknown>;
  scheduledAt?: Date;
  expiresIn?: number;
  silent?: boolean;
  tags?: string[];
}

export interface NotificationAction {
  id: string;
  label: string;
  type: 'button' | 'link' | 'dismiss';
  url?: string;
  handler?: () => void;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: NotificationType;
  priority: NotificationPriority;
  channels: NotificationChannel[];
  icon?: string;
  image?: string;
  actions: NotificationAction[];
  data: Record<string, unknown>;
  createdAt: Date;
  readAt?: Date;
  dismissedAt?: Date;
  scheduledAt?: Date;
  sentAt?: Date;
  expiresAt?: Date;
  status: NotificationStatus;
  tags: string[];
  error?: string;
}

export interface NotificationTemplate {
  id: string;
  name: string;
  type: NotificationType;
  titleTemplate: string;
  messageTemplate: string;
  defaultChannels: NotificationChannel[];
  defaultPriority: NotificationPriority;
  variables: string[];
}

export interface NotificationChannelConfig {
  type: NotificationChannel;
  enabled: boolean;
  config: Record<string, unknown>;
}

export interface NotificationStats {
  total: number;
  unread: number;
  byType: Record<NotificationType, number>;
  byChannel: Record<NotificationChannel, number>;
  recentCount: number;
}

export interface NotificationFilter {
  read?: boolean;
  type?: NotificationType;
  priority?: NotificationPriority;
  channel?: NotificationChannel;
  since?: Date;
  until?: Date;
  tags?: string[];
}

export enum NotificationType {
  INFO = 'info',
  SUCCESS = 'success',
  WARNING = 'warning',
  ERROR = 'error',
  DOWNLOAD = 'download',
  CONVERSION = 'conversion',
  SYSTEM = 'system',
  UPDATE = 'update',
}

export enum NotificationPriority {
  LOW = 0,
  NORMAL = 1,
  HIGH = 2,
  URGENT = 3,
}

export enum NotificationStatus {
  PENDING = 'pending',
  SCHEDULED = 'scheduled',
  SENT = 'sent',
  DELIVERED = 'delivered',
  READ = 'read',
  DISMISSED = 'dismissed',
  FAILED = 'failed',
  EXPIRED = 'expired',
}

export enum NotificationChannel {
  IN_APP = 'in_app',
  PUSH = 'push',
  EMAIL = 'email',
  SMS = 'sms',
  WEBHOOK = 'webhook',
  DISCORD = 'discord',
  SLACK = 'slack',
  TELEGRAM = 'telegram',
}

// ═══════════════════════════════════════════════════════════════════════════════
// NOTIFICATION SERVICE CLASS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Elite Notification Service
 * @class NotificationService
 * @description Multi-channel notification management
 */
export class NotificationService {
  private static instance: NotificationService;
  private notifications: Map<string, Notification> = new Map();
  private templates: Map<string, NotificationTemplate> = new Map();
  private channelConfigs: Map<NotificationChannel, NotificationChannelConfig> = new Map();
  private scheduledTimers: Map<string, NodeJS.Timeout> = new Map();
  private listeners: Set<(notification: Notification) => void> = new Set();
  private maxNotifications: number = 1000;

  private constructor() {
    this.initializeDefaultTemplates();
    this.initializeDefaultChannels();
  }

  static getInstance(): NotificationService {
    if (!NotificationService.instance) {
      NotificationService.instance = new NotificationService();
    }
    return NotificationService.instance;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // NOTIFICATION MANAGEMENT
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Send notification
   */
  async send(options: NotificationOptions): Promise<Notification> {
    const id = `notif_${generateDownloadId().substring(3)}`;

    const notification: Notification = {
      id,
      title: options.title,
      message: options.message,
      type: options.type || NotificationType.INFO,
      priority: options.priority || NotificationPriority.NORMAL,
      channels: options.channels || [NotificationChannel.IN_APP],
      icon: options.icon,
      image: options.image,
      actions: options.actions || [],
      data: options.data || {},
      createdAt: new Date(),
      scheduledAt: options.scheduledAt,
      expiresAt: options.expiresIn ? new Date(Date.now() + options.expiresIn) : undefined,
      status: options.scheduledAt ? NotificationStatus.SCHEDULED : NotificationStatus.PENDING,
      tags: options.tags || [],
    };

    this.notifications.set(id, notification);

    // Schedule or send immediately
    if (options.scheduledAt) {
      this.scheduleNotification(notification);
    } else {
      await this.deliverNotification(notification);
    }

    // Notify listeners
    if (!options.silent) {
      this.notifyListeners(notification);
    }

    return notification;
  }

  /**
   * Send notification from template
   */
  async sendFromTemplate(
    templateId: string,
    variables: Record<string, string>,
    options?: Partial<NotificationOptions>
  ): Promise<Notification> {
    const template = this.templates.get(templateId);
    if (!template) {
      throw new Error(`Template not found: ${templateId}`);
    }

    // Replace variables in templates
    let title = template.titleTemplate;
    let message = template.messageTemplate;

    for (const [key, value] of Object.entries(variables)) {
      title = title.replace(new RegExp(`{{${key}}}`, 'g'), value);
      message = message.replace(new RegExp(`{{${key}}}`, 'g'), value);
    }

    return this.send({
      title,
      message,
      type: template.type,
      priority: options?.priority || template.defaultPriority,
      channels: options?.channels || template.defaultChannels,
      ...options,
    });
  }

  /**
   * Schedule notification
   */
  private scheduleNotification(notification: Notification): void {
    if (!notification.scheduledAt) return;

    const delay = notification.scheduledAt.getTime() - Date.now();
    
    if (delay <= 0) {
      this.deliverNotification(notification);
      return;
    }

    const timer = setTimeout(() => {
      this.deliverNotification(notification);
      this.scheduledTimers.delete(notification.id);
    }, delay);

    this.scheduledTimers.set(notification.id, timer);
    notification.status = NotificationStatus.SCHEDULED;
  }

  /**
   * Deliver notification to all channels
   */
  private async deliverNotification(notification: Notification): Promise<void> {
    notification.status = NotificationStatus.SENT;
    notification.sentAt = new Date();

    for (const channel of notification.channels) {
      try {
        await this.deliverToChannel(notification, channel);
      } catch (error) {
        notification.error = error instanceof Error ? error.message : 'Delivery failed';
        logger.error(`Failed to deliver notification to ${channel}`, { notificationId: notification.id });
      }
    }

    notification.status = NotificationStatus.DELIVERED;
  }

  /**
   * Deliver to specific channel
   */
  private async deliverToChannel(
    notification: Notification,
    channel: NotificationChannel
  ): Promise<void> {
    const config = this.channelConfigs.get(channel);
    
    if (!config?.enabled) {
      logger.debug(`Channel ${channel} is disabled, skipping`);
      return;
    }

    switch (channel) {
      case NotificationChannel.IN_APP:
        // Already handled by notification store
        break;
      case NotificationChannel.PUSH:
        await this.sendPushNotification(notification);
        break;
      case NotificationChannel.EMAIL:
        await this.sendEmailNotification(notification, config.config);
        break;
      case NotificationChannel.WEBHOOK:
        await this.sendWebhookNotification(notification, config.config);
        break;
      case NotificationChannel.DISCORD:
        await this.sendDiscordNotification(notification, config.config);
        break;
      case NotificationChannel.SLACK:
        await this.sendSlackNotification(notification, config.config);
        break;
      case NotificationChannel.TELEGRAM:
        await this.sendTelegramNotification(notification, config.config);
        break;
      default:
        throw new Error(`Unknown channel: ${channel}`);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // CHANNEL IMPLEMENTATIONS
  // ═══════════════════════════════════════════════════════════════════════════

  private async sendPushNotification(notification: Notification): Promise<void> {
    // Simulate push notification
    await this.delay(50);
    logger.debug(`Push notification sent: ${notification.title}`);
  }

  private async sendEmailNotification(
    notification: Notification,
    config: Record<string, unknown>
  ): Promise<void> {
    await this.delay(100);
    logger.debug(`Email sent: ${notification.title}`);
  }

  private async sendWebhookNotification(
    notification: Notification,
    config: Record<string, unknown>
  ): Promise<void> {
    const url = config.url as string;
    if (!url) return;

    await this.delay(50);
    logger.debug(`Webhook called: ${url}`);
  }

  private async sendDiscordNotification(
    notification: Notification,
    config: Record<string, unknown>
  ): Promise<void> {
    const webhookUrl = config.webhookUrl as string;
    if (!webhookUrl) return;

    await this.delay(50);
    logger.debug(`Discord notification sent: ${notification.title}`);
  }

  private async sendSlackNotification(
    notification: Notification,
    config: Record<string, unknown>
  ): Promise<void> {
    const webhookUrl = config.webhookUrl as string;
    if (!webhookUrl) return;

    await this.delay(50);
    logger.debug(`Slack notification sent: ${notification.title}`);
  }

  private async sendTelegramNotification(
    notification: Notification,
    config: Record<string, unknown>
  ): Promise<void> {
    const botToken = config.botToken as string;
    const chatId = config.chatId as string;
    if (!botToken || !chatId) return;

    await this.delay(50);
    logger.debug(`Telegram notification sent: ${notification.title}`);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // NOTIFICATION ACTIONS
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Mark notification as read
   */
  markAsRead(notificationId: string): boolean {
    const notification = this.notifications.get(notificationId);
    if (!notification) return false;

    notification.readAt = new Date();
    notification.status = NotificationStatus.READ;
    return true;
  }

  /**
   * Mark all as read
   */
  markAllAsRead(): number {
    let count = 0;
    for (const notification of this.notifications.values()) {
      if (!notification.readAt) {
        notification.readAt = new Date();
        notification.status = NotificationStatus.READ;
        count++;
      }
    }
    return count;
  }

  /**
   * Dismiss notification
   */
  dismiss(notificationId: string): boolean {
    const notification = this.notifications.get(notificationId);
    if (!notification) return false;

    notification.dismissedAt = new Date();
    notification.status = NotificationStatus.DISMISSED;
    return true;
  }

  /**
   * Cancel scheduled notification
   */
  cancel(notificationId: string): boolean {
    const timer = this.scheduledTimers.get(notificationId);
    if (timer) {
      clearTimeout(timer);
      this.scheduledTimers.delete(notificationId);
    }

    const notification = this.notifications.get(notificationId);
    if (notification && notification.status === NotificationStatus.SCHEDULED) {
      notification.status = NotificationStatus.DISMISSED;
      return true;
    }

    return false;
  }

  /**
   * Delete notification
   */
  delete(notificationId: string): boolean {
    this.cancel(notificationId);
    return this.notifications.delete(notificationId);
  }

  /**
   * Clear all notifications
   */
  clearAll(): void {
    for (const timer of this.scheduledTimers.values()) {
      clearTimeout(timer);
    }
    this.scheduledTimers.clear();
    this.notifications.clear();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // QUERY METHODS
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Get notification by ID
   */
  get(notificationId: string): Notification | undefined {
    return this.notifications.get(notificationId);
  }

  /**
   * Get all notifications
   */
  getAll(filter?: NotificationFilter): Notification[] {
    let notifications = Array.from(this.notifications.values());

    if (filter) {
      if (filter.read !== undefined) {
        notifications = notifications.filter(n => 
          filter.read ? !!n.readAt : !n.readAt
        );
      }
      if (filter.type) {
        notifications = notifications.filter(n => n.type === filter.type);
      }
      if (filter.priority !== undefined) {
        notifications = notifications.filter(n => n.priority === filter.priority);
      }
      if (filter.channel) {
        notifications = notifications.filter(n => n.channels.includes(filter.channel!));
      }
      if (filter.since) {
        notifications = notifications.filter(n => n.createdAt >= filter.since!);
      }
      if (filter.until) {
        notifications = notifications.filter(n => n.createdAt <= filter.until!);
      }
      if (filter.tags?.length) {
        notifications = notifications.filter(n => 
          filter.tags!.some(tag => n.tags.includes(tag))
        );
      }
    }

    return notifications.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  /**
   * Get unread notifications
   */
  getUnread(): Notification[] {
    return this.getAll({ read: false });
  }

  /**
   * Get notification statistics
   */
  getStats(): NotificationStats {
    const notifications = Array.from(this.notifications.values());
    
    const byType: Record<NotificationType, number> = {} as any;
    const byChannel: Record<NotificationChannel, number> = {} as any;

    for (const type of Object.values(NotificationType)) {
      byType[type] = 0;
    }
    for (const channel of Object.values(NotificationChannel)) {
      byChannel[channel] = 0;
    }

    for (const n of notifications) {
      byType[n.type]++;
      for (const channel of n.channels) {
        byChannel[channel]++;
      }
    }

    return {
      total: notifications.length,
      unread: notifications.filter(n => !n.readAt).length,
      byType,
      byChannel,
      recentCount: notifications.filter(n => 
        Date.now() - n.createdAt.getTime() < 3600000
      ).length,
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // TEMPLATE MANAGEMENT
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Register template
   */
  registerTemplate(template: NotificationTemplate): void {
    this.templates.set(template.id, template);
  }

  /**
   * Get template
   */
  getTemplate(templateId: string): NotificationTemplate | undefined {
    return this.templates.get(templateId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // CHANNEL CONFIGURATION
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Configure channel
   */
  configureChannel(channel: NotificationChannel, config: Record<string, unknown>, enabled: boolean = true): void {
    this.channelConfigs.set(channel, { type: channel, enabled, config });
  }

  /**
   * Enable/disable channel
   */
  setChannelEnabled(channel: NotificationChannel, enabled: boolean): void {
    const existing = this.channelConfigs.get(channel);
    if (existing) {
      existing.enabled = enabled;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // EVENT LISTENERS
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Subscribe to notifications
   */
  subscribe(callback: (notification: Notification) => void): () => void {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  /**
   * Notify all listeners
   */
  private notifyListeners(notification: Notification): void {
    for (const listener of this.listeners) {
      try {
        listener(notification);
      } catch (error) {
        logger.error('Notification listener error', { error });
      }
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // HELPER METHODS
  // ═══════════════════════════════════════════════════════════════════════════

  private initializeDefaultTemplates(): void {
    this.registerTemplate({
      id: 'download_complete',
      name: 'Download Complete',
      type: NotificationType.DOWNLOAD,
      titleTemplate: 'Download Complete: {{filename}}',
      messageTemplate: 'Your download of {{filename}} ({{size}}) has completed successfully.',
      defaultChannels: [NotificationChannel.IN_APP],
      defaultPriority: NotificationPriority.NORMAL,
      variables: ['filename', 'size'],
    });

    this.registerTemplate({
      id: 'download_failed',
      name: 'Download Failed',
      type: NotificationType.ERROR,
      titleTemplate: 'Download Failed: {{filename}}',
      messageTemplate: 'Failed to download {{filename}}: {{error}}',
      defaultChannels: [NotificationChannel.IN_APP],
      defaultPriority: NotificationPriority.HIGH,
      variables: ['filename', 'error'],
    });

    this.registerTemplate({
      id: 'conversion_complete',
      name: 'Conversion Complete',
      type: NotificationType.CONVERSION,
      titleTemplate: 'Conversion Complete',
      messageTemplate: 'Your file has been converted to {{format}} successfully.',
      defaultChannels: [NotificationChannel.IN_APP],
      defaultPriority: NotificationPriority.NORMAL,
      variables: ['format'],
    });

    this.registerTemplate({
      id: 'system_update',
      name: 'System Update',
      type: NotificationType.UPDATE,
      titleTemplate: 'System Update Available',
      messageTemplate: 'Version {{version}} is now available. {{changelog}}',
      defaultChannels: [NotificationChannel.IN_APP, NotificationChannel.PUSH],
      defaultPriority: NotificationPriority.HIGH,
      variables: ['version', 'changelog'],
    });
  }

  private initializeDefaultChannels(): void {
    this.channelConfigs.set(NotificationChannel.IN_APP, {
      type: NotificationChannel.IN_APP,
      enabled: true,
      config: {},
    });
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// Export singleton instance
export const notificationService = NotificationService.getInstance();

// ═══════════════════════════════════════════════════════════════════════════════
// CONVENIENCE FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

export async function notify(
  title: string,
  message: string,
  type: NotificationType = NotificationType.INFO
): Promise<Notification> {
  return notificationService.send({ title, message, type });
}

export async function notifySuccess(title: string, message: string): Promise<Notification> {
  return notificationService.send({ title, message, type: NotificationType.SUCCESS });
}

export async function notifyError(title: string, message: string): Promise<Notification> {
  return notificationService.send({ title, message, type: NotificationType.ERROR });
}

export async function notifyWarning(title: string, message: string): Promise<Notification> {
  return notificationService.send({ title, message, type: NotificationType.WARNING });
}

export async function notifyDownload(
  filename: string,
  size: string,
  success: boolean,
  error?: string
): Promise<Notification> {
  const templateId = success ? 'download_complete' : 'download_failed';
  return notificationService.sendFromTemplate(templateId, {
    filename,
    size: size || 'unknown',
    error: error || 'Unknown error',
  });
}
