/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    USE WEBSOCKET HOOK v3.0.1 ULTIMATE NEXUS                   ║
 * ║                    OMNIPOTENT SOVEREIGN EDITION                              ║
 * ╠══════════════════════════════════════════════════════════════════════════════╣
 * ║  Author: RAJSARASWATI JATAV (RS) - T3rmuxk1ng                                ║
 * ║  Description: WebSocket connection hook with auto-reconnect                  ║
 * ║  Features: Auto-reconnect, message queue, event handling, heartbeat         ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 * 
 * @module hooks/useWebSocket
 * @version 3.0.1
 * @author RAJSARASWATI JATAV (RS)
 */

'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  WSMessage,
  WSMessageType,
  WSConnectionOptions,
} from '@/types/api';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'reconnecting' | 'error';

export interface UseWebSocketOptions extends WSConnectionOptions {
  /** Auto-connect on mount */
  autoConnect?: boolean;
  /** Custom WebSocket port */
  port?: number;
  /** Connection URL path */
  path?: string;
  /** Debug mode */
  debug?: boolean;
}

export interface UseWebSocketReturn {
  /** Connection status */
  status: ConnectionStatus;
  /** Is connected */
  isConnected: boolean;
  /** Subscribe to a channel */
  subscribe: (channel: string) => void;
  /** Unsubscribe from a channel */
  unsubscribe: (channel: string) => void;
  /** Send a message */
  send: (message: WSMessage) => void;
  /** Register event handler */
  on: (eventType: WSMessageType | '*', handler: (data: unknown) => void) => void;
  /** Remove event handler */
  off: (eventType: WSMessageType | '*', handler: (data: unknown) => void) => void;
  /** Connect manually */
  connect: () => Promise<void>;
  /** Disconnect manually */
  disconnect: () => void;
  /** Reconnect */
  reconnect: () => void;
  /** Subscribed channels */
  channels: string[];
  /** Last received message */
  lastMessage: WSMessage | null;
  /** Connection error */
  error: Error | null;
}

// ═══════════════════════════════════════════════════════════════════════════════
// HOOK IMPLEMENTATION
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * useWebSocket Hook
 * @description WebSocket connection management with auto-reconnect and event handling
 * @param options Hook options
 * @returns WebSocket controls and state
 */
export function useWebSocket(options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const {
    autoConnect = true,
    port = 3003,
    path = '/',
    heartbeatInterval = 30000,
    autoReconnect = true,
    maxReconnectAttempts = 10,
    reconnectDelay = 1000,
    debug = false,
  } = options;

  // State
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [channels, setChannels] = useState<string[]>([]);
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null);
  const [error, setError] = useState<Error | null>(null);

  // Refs
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const messageQueueRef = useRef<WSMessage[]>([]);
  const eventHandlersRef = useRef<Map<string, Set<(data: unknown) => void>>>(new Map());
  const mountedRef = useRef(true);

  // ═══════════════════════════════════════════════════════════════════════════
  // LOGGING
  // ═══════════════════════════════════════════════════════════════════════════

  const log = useCallback(
    (...args: unknown[]) => {
      if (debug) {
        console.log('[WS]', ...args);
      }
    },
    [debug]
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // HEARTBEAT
  // ═══════════════════════════════════════════════════════════════════════════

  const startHeartbeat = useCallback(() => {
    if (heartbeatTimeoutRef.current) {
      clearInterval(heartbeatTimeoutRef.current);
    }

    heartbeatTimeoutRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        send({
          type: WSMessageType.HEARTBEAT,
          data: { ping: true },
          timestamp: new Date().toISOString(),
          messageId: `msg_${Date.now()}`,
        });
      }
    }, heartbeatInterval);
  }, [heartbeatInterval]);

  const stopHeartbeat = useCallback(() => {
    if (heartbeatTimeoutRef.current) {
      clearInterval(heartbeatTimeoutRef.current);
      heartbeatTimeoutRef.current = null;
    }
  }, []);

  // ═══════════════════════════════════════════════════════════════════════════
  // CONNECTION
  // ═══════════════════════════════════════════════════════════════════════════

  const connect = useCallback(async (): Promise<void> => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setStatus('connecting');
    setError(null);

    try {
      // Use gateway URL format with XTransformPort
      const wsUrl = `wss://${window.location.host}${path}?XTransformPort=${port}`;
      log('Connecting to:', wsUrl);

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        log('Connected');
        setStatus('connected');
        reconnectAttemptsRef.current = 0;
        startHeartbeat();
        flushMessageQueue();
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data as string) as WSMessage;
          setLastMessage(message);
          handleMessage(message);
        } catch (err) {
          log('Message parse error:', err);
        }
      };

      ws.onclose = (event) => {
        log('Disconnected:', event.reason);
        setStatus('disconnected');
        stopHeartbeat();
        handleReconnect();
      };

      ws.onerror = (err) => {
        log('Error:', err);
        setError(new Error('WebSocket error'));
        setStatus('error');
      };
    } catch (err) {
      log('Connection error:', err);
      setError(err instanceof Error ? err : new Error('Unknown error'));
      setStatus('error');
    }
  }, [port, path, log, startHeartbeat, stopHeartbeat]);

  const disconnect = useCallback(() => {
    log('Disconnecting');
    stopHeartbeat();
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close(1000, 'Client disconnect');
      wsRef.current = null;
    }
    setStatus('disconnected');
    setChannels([]);
  }, [log, stopHeartbeat]);

  const reconnect = useCallback(() => {
    reconnectAttemptsRef.current = 0;
    disconnect();
    connect();
  }, [connect, disconnect]);

  // ═══════════════════════════════════════════════════════════════════════════
  // RECONNECT LOGIC
  // ═══════════════════════════════════════════════════════════════════════════

  const handleReconnect = useCallback(() => {
    if (!autoReconnect || !mountedRef.current) return;
    if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
      log('Max reconnect attempts reached');
      setStatus('error');
      setError(new Error('Max reconnect attempts reached'));
      return;
    }

    setStatus('reconnecting');
    reconnectAttemptsRef.current++;

    const delay = reconnectDelay * Math.pow(2, reconnectAttemptsRef.current - 1);
    log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current})`);

    reconnectTimeoutRef.current = setTimeout(() => {
      connect();
    }, delay);
  }, [autoReconnect, maxReconnectAttempts, reconnectDelay, log, connect]);

  // ═══════════════════════════════════════════════════════════════════════════
  // MESSAGE HANDLING
  // ═══════════════════════════════════════════════════════════════════════════

  const handleMessage = useCallback((message: WSMessage) => {
    log('Message received:', message.type);

    // Call type-specific handlers
    const handlers = eventHandlersRef.current.get(message.type);
    if (handlers) {
      handlers.forEach((handler) => handler(message.data));
    }

    // Call generic handlers
    const genericHandlers = eventHandlersRef.current.get('*');
    if (genericHandlers) {
      genericHandlers.forEach((handler) => handler(message));
    }
  }, [log]);

  const flushMessageQueue = useCallback(() => {
    while (
      messageQueueRef.current.length > 0 &&
      wsRef.current?.readyState === WebSocket.OPEN
    ) {
      const message = messageQueueRef.current.shift();
      if (message) {
        wsRef.current.send(JSON.stringify(message));
      }
    }
  }, []);

  // ═══════════════════════════════════════════════════════════════════════════
  // CHANNEL MANAGEMENT
  // ═══════════════════════════════════════════════════════════════════════════

  const subscribe = useCallback((channel: string) => {
    log('Subscribing to:', channel);
    send({
      type: 'subscribe' as WSMessageType,
      data: { channel },
      timestamp: new Date().toISOString(),
      messageId: `msg_${Date.now()}`,
    });
    setChannels((prev) => [...new Set([...prev, channel])]);
  }, [log]);

  const unsubscribe = useCallback((channel: string) => {
    log('Unsubscribing from:', channel);
    send({
      type: 'unsubscribe' as WSMessageType,
      data: { channel },
      timestamp: new Date().toISOString(),
      messageId: `msg_${Date.now()}`,
    });
    setChannels((prev) => prev.filter((c) => c !== channel));
  }, [log]);

  // ═══════════════════════════════════════════════════════════════════════════
  // SEND MESSAGE
  // ═══════════════════════════════════════════════════════════════════════════

  const send = useCallback((message: WSMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
      log('Message sent:', message.type);
    } else {
      log('Message queued:', message.type);
      messageQueueRef.current.push(message);
    }
  }, [log]);

  // ═══════════════════════════════════════════════════════════════════════════
  // EVENT HANDLERS
  // ═══════════════════════════════════════════════════════════════════════════

  const on = useCallback(
    (eventType: WSMessageType | '*', handler: (data: unknown) => void) => {
      if (!eventHandlersRef.current.has(eventType)) {
        eventHandlersRef.current.set(eventType, new Set());
      }
      eventHandlersRef.current.get(eventType)!.add(handler);
    },
    []
  );

  const off = useCallback(
    (eventType: WSMessageType | '*', handler: (data: unknown) => void) => {
      eventHandlersRef.current.get(eventType)?.delete(handler);
    },
    []
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // LIFECYCLE
  // ═══════════════════════════════════════════════════════════════════════════

  useEffect(() => {
    mountedRef.current = true;

    if (autoConnect) {
      connect();
    }

    return () => {
      mountedRef.current = false;
      stopHeartbeat();
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounting');
        wsRef.current = null;
      }
    };
  }, [autoConnect, connect, stopHeartbeat]);

  // ═══════════════════════════════════════════════════════════════════════════
  // RETURN
  // ═══════════════════════════════════════════════════════════════════════════

  return {
    status,
    isConnected: status === 'connected',
    subscribe,
    unsubscribe,
    send,
    on,
    off,
    connect,
    disconnect,
    reconnect,
    channels,
    lastMessage,
    error,
  };
}

export default useWebSocket;
