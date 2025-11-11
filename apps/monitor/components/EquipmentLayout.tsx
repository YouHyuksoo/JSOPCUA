'use client';

import { Equipment } from '@/lib/types/equipment';
import { EquipmentStatusBox } from './EquipmentStatusBox';
import Image from 'next/image';

interface EquipmentLayoutProps {
  equipment: Equipment[];
}

export function EquipmentLayout({ equipment }: EquipmentLayoutProps) {
  return (
    <div className="relative bg-gray-800 rounded-lg p-4">
      <h2 className="text-lg font-bold mb-4">설비 상태 모니터링 (17개 설비)</h2>

      {/* Background image (if available) */}
      <div className="relative min-h-[400px]">
        {/* Equipment layout grid */}
        <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
          {equipment.length === 0 ? (
            <div className="col-span-full text-center text-gray-400 py-8">
              설비 데이터를 불러오는 중...
            </div>
          ) : (
            equipment.map((eq) => (
              <EquipmentStatusBox
                key={eq.equipment_code}
                equipment={eq}
              />
            ))
          )}
        </div>

        {equipment.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="animate-pulse text-gray-500">
              <svg
                className="w-12 h-12 mx-auto mb-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              <p>WebSocket 연결 중...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
