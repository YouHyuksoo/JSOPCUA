import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

export interface EquipmentPosition {
  process_code: string;
  position_x: number;
  position_y: number;
  width?: number;
  height?: number;
  z_index?: number;
  // PLC 태그 매핑 필드
  tag_id?: number | null;
  tag_address?: string | null;
  plc_code?: string | null;
  machine_code?: string | null;
}

export interface EquipmentPositionsResponse {
  layout_name: string;
  positions: Record<string, EquipmentPosition>;
}

export interface EquipmentPositionUpdate {
  layout_name: string;
  positions: EquipmentPosition[];
}

/**
 * Get equipment positions from database
 */
export async function getEquipmentPositions(
  layoutName: string = 'default'
): Promise<EquipmentPositionsResponse> {
  const response = await apiClient.get<EquipmentPositionsResponse>(
    '/api/monitor/equipment-positions',
    {
      params: { layout_name: layoutName }
    }
  );
  return response.data;
}

/**
 * Save equipment positions to database
 */
export async function saveEquipmentPositions(
  update: EquipmentPositionUpdate
): Promise<{ message: string; layout_name: string; count: number }> {
  const response = await apiClient.post(
    '/api/monitor/equipment-positions',
    update
  );
  return response.data;
}

