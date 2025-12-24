'use client';

import { Equipment, EquipmentColorType } from '@/lib/types/equipment';
import { cn } from '@/lib/utils';

interface EquipmentStatusBoxProps {
  equipment: Equipment;
  className?: string;
}

const colorClasses: Record<EquipmentColorType, string> = {
  green: 'bg-green-500/70 border-green-600 text-white backdrop-blur-sm',
  yellow: 'bg-yellow-500/70 border-yellow-600 text-gray-900 backdrop-blur-sm',
  red: 'bg-red-500/70 border-red-600 text-white backdrop-blur-sm',
  purple: 'bg-purple-500/70 border-purple-600 text-white backdrop-blur-sm',
  gray: 'bg-gray-500/70 border-gray-600 text-white backdrop-blur-sm'
};

const statusLabels: Record<EquipmentColorType, string> = {
  green: '가동',
  yellow: '비가동',
  red: '정지',
  purple: '설비이상',
  gray: '접속이상'
};

export function EquipmentStatusBox({ equipment, className }: EquipmentStatusBoxProps) {
  const colorClass = colorClasses[equipment.color];
  const statusLabel = statusLabels[equipment.color];

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center',
        'border-2 rounded-md p-2',
        'transition-all duration-300',
        'min-w-[120px] min-h-[80px]',
        'shadow-lg',
        colorClass,
        className
      )}
    >
      <div className="text-sm font-bold text-center mb-1 line-clamp-2 drop-shadow-md">
        {equipment.equipment_name}
      </div>
      <div className="text-xs font-medium drop-shadow-md">
        {statusLabel}
      </div>
    </div>
  );
}
