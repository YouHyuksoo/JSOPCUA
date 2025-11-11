'use client';

import { Equipment, EquipmentColorType } from '@/lib/types/equipment';
import { cn } from '@/lib/utils';

interface EquipmentStatusBoxProps {
  equipment: Equipment;
  className?: string;
}

const colorClasses: Record<EquipmentColorType, string> = {
  green: 'equipment-status-green text-white',
  yellow: 'equipment-status-yellow text-gray-900',
  red: 'equipment-status-red text-white',
  purple: 'equipment-status-purple text-white',
  gray: 'equipment-status-gray text-white'
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
        'transition-colors duration-300',
        'min-w-[120px] min-h-[80px]',
        colorClass,
        className
      )}
    >
      <div className="text-sm font-bold text-center mb-1 line-clamp-2">
        {equipment.equipment_name}
      </div>
      <div className="text-xs font-medium">
        {statusLabel}
      </div>
    </div>
  );
}
