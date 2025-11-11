'use client';

import { useEffect, useState } from 'react';
import { AlarmStatistics } from '@/lib/types/alarm';
import { getAlarmStatistics } from '@/lib/api/alarms';

const AUTO_REFRESH_INTERVAL = 10000; // 10 seconds

export function EquipmentGrid() {
  const [statistics, setStatistics] = useState<AlarmStatistics[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [countdown, setCountdown] = useState(10);

  const fetchStatistics = async () => {
    try {
      const data = await getAlarmStatistics();
      setStatistics(data.equipment);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch alarm statistics:', err);
      setError('알람 통계 조회 실패 - Oracle DB 연결을 확인해주세요');
      // Keep previous data on error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchStatistics();

    // Auto-refresh every 10 seconds
    const refreshInterval = setInterval(() => {
      fetchStatistics();
      setCountdown(10); // Reset countdown
    }, AUTO_REFRESH_INTERVAL);

    // Countdown timer (1 second interval)
    const countdownInterval = setInterval(() => {
      setCountdown((prev) => (prev > 0 ? prev - 1 : 10));
    }, 1000);

    return () => {
      clearInterval(refreshInterval);
      clearInterval(countdownInterval);
    };
  }, []);

  if (loading && statistics.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h2 className="text-lg font-bold mb-4">설비별 알람 통계</h2>
        <div className="flex items-center justify-center py-8">
          <div className="animate-pulse text-gray-400">
            알람 통계를 불러오는 중...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold">설비별 알람 통계</h2>
        <div className="text-xs text-gray-400">
          C/Time: <span className="font-mono">{countdown}초</span>
        </div>
      </div>

      {error && (
        <div className="mb-4 bg-yellow-900/30 border border-yellow-700 rounded-lg p-3">
          <p className="text-xs text-yellow-200">{error}</p>
          <p className="text-xs text-yellow-300 mt-1">이전 데이터를 유지합니다. {countdown}초 후 재시도합니다.</p>
        </div>
      )}

      {statistics.length === 0 ? (
        <div className="text-center text-gray-400 py-8">
          알람 데이터가 없습니다.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-2 px-3 font-medium text-gray-300">설비명</th>
                <th className="text-right py-2 px-3 font-medium text-gray-300">알람 합계</th>
                <th className="text-right py-2 px-3 font-medium text-gray-300">일반</th>
              </tr>
            </thead>
            <tbody>
              {statistics.map((stat, index) => (
                <tr
                  key={stat.equipment_code}
                  className={`border-b border-gray-700 hover:bg-gray-700/50 transition-colors ${
                    index % 2 === 0 ? 'bg-gray-800' : 'bg-gray-750'
                  }`}
                >
                  <td className="py-2 px-3 text-gray-200">{stat.equipment_name}</td>
                  <td className="py-2 px-3 text-right">
                    <span
                      className={`font-mono font-medium ${
                        stat.alarm_count > 0 ? 'text-red-400' : 'text-gray-400'
                      }`}
                    >
                      {stat.alarm_count}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-right">
                    <span className="font-mono font-medium text-gray-400">
                      {stat.general_count}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
