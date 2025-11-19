import { useEffect, useRef, useState, useCallback } from 'react';
import { WebSocketMessage, Equipment } from '../types/equipment';

interface UseWebSocketOptions {
  url: string;
  reconnectInterval?: number; // milliseconds
  maxReconnectAttempts?: number;
  onMessage?: (data: WebSocketMessage) => void;
  onError?: (error: Event) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  equipment: Equipment[];
  reconnectAttempts: number;
  error: string | null;
}

export function useWebSocket({
  url,
  reconnectInterval = 3000,
  maxReconnectAttempts = 5,
  onMessage,
  onError,
  onConnect,
  onDisconnect
}: UseWebSocketOptions): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const shouldReconnectRef = useRef(true);

  const connect = useCallback(() => {
    try {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        return;
      }

      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setReconnectAttempts(0);
        setError(null);
        onConnect?.();
      };

      ws.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data);

          if (data.type === 'equipment_status') {
            setEquipment(data.equipment);
          }

          onMessage?.(data);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onerror = (event) => {
        setError('WebSocket connection error');
        onError?.(event);
      };

      ws.onclose = () => {
        setIsConnected(false);
        wsRef.current = null;
        onDisconnect?.();

        // Attempt reconnection
        if (shouldReconnectRef.current && reconnectAttempts < maxReconnectAttempts) {
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectAttempts((prev) => prev + 1);
            connect();
          }, reconnectInterval);
        } else if (reconnectAttempts >= maxReconnectAttempts) {
          setError(`Failed to reconnect after ${maxReconnectAttempts} attempts`);
          // Set all equipment to disconnected state
          setEquipment((prev) =>
            prev.map((eq) => ({
              ...eq,
              status: 'disconnected' as const,
              color: 'gray' as const,
              tags: { ...eq.tags, connection: false }
            }))
          );
        }
      };
    } catch (err) {
      console.error('Failed to create WebSocket connection:', err);
      setError('Failed to create WebSocket connection');
    }
  }, [url, reconnectInterval, maxReconnectAttempts, reconnectAttempts, onMessage, onError, onConnect, onDisconnect]);

  useEffect(() => {
    shouldReconnectRef.current = true;
    connect();

    return () => {
      shouldReconnectRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return {
    isConnected,
    equipment,
    reconnectAttempts,
    error
  };
}
