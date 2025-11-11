'use client';

import { useEffect, useState } from 'react';
import { Alarm } from '@/lib/types/alarm';
import { getRecentAlarms } from '@/lib/api/alarms';
import { formatTime } from '@/lib/utils';

const AUTO_REFRESH_INTERVAL = 10000; // 10 seconds
const ALARM_LIMIT = 5;

export function AlarmList() {
  const [alarms, setAlarms] = useState<Alarm[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAlarms = async () => {
    try {
      const data = await getRecentAlarms(ALARM_LIMIT);
      setAlarms(data.alarms);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch recent alarms:', err);
      setError('알람 조회 실패');
      // Keep previous data on error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchAlarms();

    // Auto-refresh every 10 seconds
    const refreshInterval = setInterval(() => {
      fetchAlarms();
    }, AUTO_REFRESH_INTERVAL);

    return () => {
      clearInterval(refreshInterval);
    };
  }, []);

  if (loading && alarms.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h2 className="text-lg font-bold mb-4">최근 알람 목록</h2>
        <div className="flex items-center justify-center py-8">
          <div className="animate-pulse text-gray-400">
            알람 목록을 불러오는 중...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <h2 className="text-lg font-bold mb-4">최근 알람 목록 (최근 5개)</h2>

      {error && (
        <div className="mb-4 bg-yellow-900/30 border border-yellow-700 rounded-lg p-3">
          <p className="text-xs text-yellow-200">{error}</p>
          <p className="text-xs text-yellow-300 mt-1">이전 데이터를 유지합니다.</p>
        </div>
      )}

      {alarms.length === 0 ? (
        <div className="text-center text-gray-400 py-8">
          <svg
            className="w-12 h-12 mx-auto mb-2 opacity-50"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
            />
          </svg>
          <p>알람 데이터가 없습니다.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {alarms.map((alarm) => (
            <div
              key={alarm.alarm_id}
              className={`rounded-lg p-3 border transition-colors ${
                alarm.alarm_type === '알람'
                  ? 'bg-red-900/20 border-red-700 hover:bg-red-900/30'
                  : 'bg-yellow-900/20 border-yellow-700 hover:bg-yellow-900/30'
              }`}
            >
              <div className="flex items-start justify-between gap-2 mb-1">
                <span
                  className={`text-xs font-medium px-2 py-1 rounded ${
                    alarm.alarm_type === '알람'
                      ? 'bg-red-700 text-white'
                      : 'bg-yellow-700 text-gray-900'
                  }`}
                >
                  {alarm.alarm_type}
                </span>
                <span className="text-xs text-gray-400 font-mono">
                  {formatTime(new Date(alarm.occurred_at))}
                </span>
              </div>
              <p className="text-sm text-gray-200 font-medium mb-1">
                {alarm.equipment_name}
              </p>
              <p className="text-xs text-gray-300 line-clamp-2">
                {alarm.alarm_message}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
