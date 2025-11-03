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
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 10;
  const baseReconnectDelay = 1000; // 1 second

  const connect = () => {
    try {
      // Close existing connection
      if (wsRef.current) {
        wsRef.current.close();
      }

      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);

          if (message.type === 'status_update') {
            setStatus(message.data);
          } else if (message.type === 'ping') {
            // Respond to ping with pong
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

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);

        // Attempt reconnection with exponential backoff
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = Math.min(
            baseReconnectDelay * Math.pow(2, reconnectAttemptsRef.current),
            30000 // Max 30 seconds
          );

          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current + 1}/${maxReconnectAttempts})...`);

          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connect();
          }, delay);
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
    reconnectAttemptsRef.current = 0;
    setError(null);
    connect();
  };

  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    status,
    isConnected,
    error,
    reconnect
  };
}
