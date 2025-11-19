import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import { Equipment, EquipmentColorType } from "./types/equipment"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Maps equipment status and tags to display color
 * Gray: No connection
 * Purple: Error detected
 * Red: Stopped
 * Yellow: Idle
 * Green: Running
 */
export function getEquipmentColor(equipment: Equipment): EquipmentColorType {
  if (!equipment.tags.connection) return 'gray';
  if (equipment.tags.error_tag === 1) return 'purple';
  if (equipment.status === 'stopped') return 'red';
  if (equipment.status === 'idle') return 'yellow';
  if (equipment.status === 'running') return 'green';
  return 'gray';
}

/**
 * Format timestamp to HH:MM format
 */
export function formatTime(date: Date): string {
  return new Date(date).toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  });
}
