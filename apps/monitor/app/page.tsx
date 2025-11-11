'use client';

import { useWebSocket } from '@/lib/hooks/useWebSocket';
import { EquipmentLayout } from '@/components/EquipmentLayout';
import { EquipmentGrid } from '@/components/EquipmentGrid';
import { AlarmList } from '@/components/AlarmList';
import { useEffect, useState } from 'react';
import { Equipment } from '@/lib/types/equipment';
import { getEquipmentColor } from '@/lib/utils';

const WEBSOCKET_URL = process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:8000/ws/monitor';

export default function MonitorPage() {
  const {
    isConnected,
    equipment: rawEquipment,
    reconnectAttempts,
    error
  } = useWebSocket({
    url: WEBSOCKET_URL,
    reconnectInterval: 3000,
    maxReconnectAttempts: 5,
    onConnect: () => console.log('WebSocket connected'),
    onDisconnect: () => console.log('WebSocket disconnected'),
    onError: (error) => console.error('WebSocket error:', error)
  });

  // Process equipment data to add color based on status
  const [equipment, setEquipment] = useState<Equipment[]>([]);

  useEffect(() => {
    const processedEquipment = rawEquipment.map((eq) => ({
      ...eq,
      color: getEquipmentColor(eq)
    }));
    setEquipment(processedEquipment);
  }, [rawEquipment]);

  return (
    <div className="min-h-screen p-4 bg-gray-900 text-white">
      <header className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">설비 모니터링 시스템</h1>
          <p className="text-sm text-gray-400">실시간 설비 상태 및 알람 모니터링</p>
        </div>

        {/* WebSocket connection status */}
        <div className="flex items-center gap-2">
          <div
            className={`w-3 h-3 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            } animate-pulse`}
          />
          <span className="text-sm">
            {isConnected ? 'WebSocket 연결됨' : 'WebSocket 연결 끊김'}
          </span>
          {reconnectAttempts > 0 && (
            <span className="text-xs text-gray-400">
              (재연결 시도: {reconnectAttempts}/5)
            </span>
          )}
        </div>
      </header>

      {/* Error message */}
      {error && (
        <div className="mb-4 bg-red-900 border border-red-700 rounded-lg p-4">
          <p className="text-sm font-medium text-red-200">⚠️ {error}</p>
          <p className="text-xs text-red-300 mt-1">
            WebSocket 재연결에 실패했습니다. 백엔드 서버를 확인해주세요.
          </p>
        </div>
      )}

      <main className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Equipment Grid (Phase 4) */}
        <div className="lg:col-span-3">
          <EquipmentGrid />
        </div>

        {/* Equipment Layout (Phase 3) */}
        <div className="lg:col-span-2">
          <EquipmentLayout equipment={equipment} />
        </div>

        {/* Alarm List (Phase 5) */}
        <div className="lg:col-span-1">
          <AlarmList />
        </div>
      </main>

      {/* Footer info */}
      <footer className="mt-4 text-center text-xs text-gray-500">
        <p>Feature 7: 실시간 설비 모니터링 웹 UI</p>
        <p>WebSocket: {WEBSOCKET_URL}</p>
      </footer>
    </div>
  );
}
