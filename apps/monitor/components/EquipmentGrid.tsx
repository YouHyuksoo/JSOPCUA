'use client';

import { useEffect, useState } from 'react';
import { EquipmentListItem } from '@/lib/types/equipment';
import { getEquipmentList } from '@/lib/api/equipment';

const AUTO_REFRESH_INTERVAL = 10000; // 10 seconds
const PAGE_SWITCH_INTERVAL = 30000; // 30 seconds (페이지 전환 간격)
const ITEMS_PER_PAGE = 50; // 페이지당 항목 수

export function EquipmentGrid() {
  const [equipmentList, setEquipmentList] = useState<EquipmentListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [countdown, setCountdown] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [pageSwitchCountdown, setPageSwitchCountdown] = useState(PAGE_SWITCH_INTERVAL / 1000);

  const fetchEquipmentList = async (page: number) => {
    try {
      const data = await getEquipmentList(page, ITEMS_PER_PAGE, 'Y'); // 사용 중인 설비만 조회
      setEquipmentList(data.equipment);
      setTotalPages(Math.ceil(data.total_count / ITEMS_PER_PAGE));
      setError(null);
    } catch (err) {
      console.error('Failed to fetch equipment list:', err);
      setError('설비 목록 조회 실패 - Oracle DB 연결을 확인해주세요');
      // Keep previous data on error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchEquipmentList(currentPage);

    // Auto-refresh every 10 seconds
    const refreshInterval = setInterval(() => {
      fetchEquipmentList(currentPage);
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
  }, [currentPage]);

  // 페이지 자동 전환 (2페이지 순환)
  useEffect(() => {
    if (totalPages <= 1) return; // 페이지가 1개 이하면 순환 불필요

    const pageSwitchInterval = setInterval(() => {
      setCurrentPage((prev) => {
        // 1페이지와 2페이지만 순환
        if (prev === 1) {
          return 2;
        } else {
          return 1;
        }
      });
      setPageSwitchCountdown(PAGE_SWITCH_INTERVAL / 1000); // Reset countdown
    }, PAGE_SWITCH_INTERVAL);

    // 페이지 전환 카운트다운 (1초 간격)
    const pageSwitchCountdownInterval = setInterval(() => {
      setPageSwitchCountdown((prev) => {
        if (prev <= 1) {
          return PAGE_SWITCH_INTERVAL / 1000;
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      clearInterval(pageSwitchInterval);
      clearInterval(pageSwitchCountdownInterval);
    };
  }, [totalPages]);

  if (loading && equipmentList.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h2 className="text-lg font-bold mb-4">설비 목록</h2>
        <div className="flex items-center justify-center py-8">
          <div className="animate-pulse text-gray-400">
            설비 목록을 불러오는 중...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-bold">설비 목록</h2>
          {totalPages > 1 && (
            <div className="text-xs text-gray-400">
              페이지 {currentPage} / {Math.min(2, totalPages)} 
              {totalPages > 2 && ` (전체 ${totalPages}페이지)`}
            </div>
          )}
        </div>
        <div className="flex items-center gap-4">
          {totalPages > 1 && (
            <div className="text-xs text-gray-400">
              페이지 전환: <span className="font-mono">{Math.floor(pageSwitchCountdown)}초</span>
            </div>
          )}
          <div className="text-xs text-gray-400">
            C/Time: <span className="font-mono">{countdown}초</span>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-4 bg-yellow-900/30 border border-yellow-700 rounded-lg p-3">
          <p className="text-xs text-yellow-200">{error}</p>
          <p className="text-xs text-yellow-300 mt-1">이전 데이터를 유지합니다. {countdown}초 후 재시도합니다.</p>
        </div>
      )}

      {equipmentList.length === 0 ? (
        <div className="text-center text-gray-400 py-8">
          설비 데이터가 없습니다.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-2 px-3 font-medium text-gray-300">설비코드</th>
                <th className="text-left py-2 px-3 font-medium text-gray-300">설비명</th>
                <th className="text-left py-2 px-3 font-medium text-gray-300">설비타입</th>
                <th className="text-left py-2 px-3 font-medium text-gray-300">라인코드</th>
                <th className="text-left py-2 px-3 font-medium text-gray-300">PLC코드</th>
                <th className="text-center py-2 px-3 font-medium text-gray-300">사용여부</th>
              </tr>
            </thead>
            <tbody>
              {equipmentList.map((item, index) => (
                <tr
                  key={item.machine_code}
                  className={`border-b border-gray-700 hover:bg-gray-700/50 transition-colors ${
                    index % 2 === 0 ? 'bg-gray-800' : 'bg-gray-750'
                  }`}
                >
                  <td className="py-2 px-3 text-gray-200 font-mono text-xs">{item.machine_code}</td>
                  <td className="py-2 px-3 text-gray-200">{item.machine_name}</td>
                  <td className="py-2 px-3 text-gray-400">{item.machine_type || '-'}</td>
                  <td className="py-2 px-3 text-gray-400">{item.line_code || '-'}</td>
                  <td className="py-2 px-3 text-gray-400">{item.plc_code || '-'}</td>
                  <td className="py-2 px-3 text-center">
                    <span
                      className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                        item.use_yn === 'Y'
                          ? 'bg-green-900/30 text-green-300 border border-green-700'
                          : 'bg-gray-700 text-gray-400 border border-gray-600'
                      }`}
                    >
                      {item.use_yn || '-'}
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
