import apiClient from './client';

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

export interface TagForMonitor {
  tag_id: number;
  tag_address: string;
  tag_name: string;
  machine_code: string | null;
  plc_code: string | null;
  tag_type: string;
  unit: string | null;
  description: string | null;
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
export const getEquipmentPositions = async (layoutName: string = 'default') => {
  const response = await apiClient.get<EquipmentPositionsResponse>(
    '/monitor/equipment-positions',
    {
      params: { layout_name: layoutName }
    }
  );
  return response.data;
};

/**
 * Save equipment positions to database
 */
export const saveEquipmentPositions = async (update: EquipmentPositionUpdate) => {
  const response = await apiClient.post<{ message: string; layout_name: string; count: number }>(
    '/monitor/equipment-positions',
    update
  );
  return response.data;
};

/**
 * Get tags list for monitor layout assignment
 */
export const getTagsForMonitor = async (machineCode?: string, plcCode?: string) => {
  const params: Record<string, string> = {};
  if (machineCode) params.machine_code = machineCode;
  if (plcCode) params.plc_code = plcCode;
  
  const response = await apiClient.get<{ tags: TagForMonitor[] }>(
    '/monitor/tags',
    { params }
  );
  return response.data.tags;
};

