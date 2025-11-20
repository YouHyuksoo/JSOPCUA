/**
 * WebSocket Hook for Polling Engine
 *
 * React hook for real-time polling status updates via WebSocket
 */

import { useEffect, useRef, useState } from 'react';
import { EngineStatus } from '@/lib/api/pollingApi';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/polling';

interface UsePollingWebSocketResult {
  status: EngineStatus | null;
  isConnected: boolean;
  error: string | null;
  reconnect: () => void;
}

export function usePollingWebSocket(): UsePollingWebSocketResult {
  const [status, setStatus] = useState<EngineStatus | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const isMountedRef = useRef(true);
  const maxReconnectAttempts = 10;
  const baseReconnectDelay = 1000; // 1 second
  const heartbeatInterval = 60000; // Send heartbeat every 60 seconds (backend timeout is 120s)

  const connect = () => {
    // Don't connect if component is unmounted
    if (!isMountedRef.current) {
      console.log('Component unmounted, not connecting');
      return;
    }

    try {
      // Clear any pending reconnection attempts
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }

      // Clear heartbeat interval
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
        heartbeatIntervalRef.current = null;
      }

      // Close existing connection if any
      if (wsRef.current) {
        // Remove event listeners to prevent onclose from triggering reconnection
        wsRef.current.onclose = null;
        wsRef.current.onerror = null;
        wsRef.current.onmessage = null;
        wsRef.current.onopen = null;

        if (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING) {
          wsRef.current.close(1000, 'Reconnecting');
        }
        wsRef.current = null;
      }

      console.log('Attempting WebSocket connection...');
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected successfully');
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0; // Reset reconnection attempts on successful connection

        // Clear any existing heartbeat interval before starting a new one
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current);
        }

        // Start heartbeat to keep connection alive
        heartbeatIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            console.log('Sending heartbeat ping to server');
            ws.send(JSON.stringify({ type: 'ping' }));
          } else {
            console.warn('Heartbeat attempted but WebSocket is not open');
          }
        }, heartbeatInterval);
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);

          if (message.type === 'status_update') {
            setStatus(message.data);
          } else if (message.type === 'ping') {
            // Respond to server ping with pong
            console.log('Received ping from server, sending pong');
            ws.send(JSON.stringify({ type: 'pong' }));
          }
        } catch (err) {
          console.error('WebSocket message parse error:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('WebSocket connection error');
      };

      ws.onclose = (event) => {
        console.log(`WebSocket disconnected (code: ${event.code}, reason: ${event.reason || 'No reason'})`);
        setIsConnected(false);

        // Clear heartbeat interval
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current);
          heartbeatIntervalRef.current = null;
        }

        // Don't reconnect on normal closure (1000) or going away (1001)
        const isNormalClosure = event.code === 1000 || event.code === 1001;

        if (isNormalClosure) {
          console.log('WebSocket closed normally, not reconnecting');
          return;
        }

        // Only attempt reconnection if component is still mounted and not a normal closure
        if (isMountedRef.current && reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = Math.min(
            baseReconnectDelay * Math.pow(2, reconnectAttemptsRef.current),
            30000 // Max 30 seconds
          );

          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current + 1}/${maxReconnectAttempts})...`);

          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connect();
          }, delay);
        } else if (!isMountedRef.current) {
          console.log('Component unmounted, not reconnecting');
        } else {
          setError('Failed to connect after multiple attempts. Please refresh the page.');
        }
      };

    } catch (err) {
      console.error('WebSocket connection error:', err);
      setError(err instanceof Error ? err.message : 'Failed to connect');
    }
  };

  const reconnect = () => {
    console.log('Manual reconnect requested');
    reconnectAttemptsRef.current = 0;
    setError(null);
    connect();
  };

  useEffect(() => {
    isMountedRef.current = true;
    connect();

    // Handle page visibility changes (tab switching, minimizing, etc.)
    const handleVisibilityChange = () => {
      if (document.hidden) {
        console.log('Page hidden, WebSocket will maintain connection');
      } else {
        console.log('Page visible, checking WebSocket connection');
        // Only reconnect if connection was lost
        if (wsRef.current?.readyState !== WebSocket.OPEN && wsRef.current?.readyState !== WebSocket.CONNECTING) {
          console.log('Reconnecting WebSocket after page became visible');
          reconnect();
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Cleanup on unmount
    return () => {
      console.log('Cleaning up WebSocket...');
      isMountedRef.current = false;

      document.removeEventListener('visibilitychange', handleVisibilityChange);

      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }

      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }

      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounted'); // Normal closure
        wsRef.current = null;
      }
    };
  }, []); // Empty dependency array - only run once

  return {
    status,
    isConnected,
    error,
    reconnect
  };
}
