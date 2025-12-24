// Equipment status and WebSocket message types for real-time monitoring

export type EquipmentStatusType = 'running' | 'idle' | 'stopped' | 'error' | 'disconnected';
export type EquipmentColorType = 'green' | 'yellow' | 'red' | 'purple' | 'gray';

// Oracle DB에서 조회한 설비 목록 항목
export interface EquipmentListItem {
  machine_code: string;
  machine_name: string;
  machine_type?: string | null;
  line_code?: string | null;
  plc_code?: string | null;
  use_yn?: string | null;
}

export interface TagValues {
  status_tag: number;
  error_tag: number;
  connection: boolean;
}

export interface Equipment {
  equipment_code: string;
  equipment_name: string;
  status: EquipmentStatusType;
  color: EquipmentColorType;
  tags: TagValues;
  last_updated: Date;
  position?: EquipmentPosition; // 위치 정보 (옵션)
}

// 설비 박스 위치 정보
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

export interface WebSocketMessage {
  type: 'equipment_status' | 'connection_status';
  timestamp: Date;
  equipment: Equipment[];
}

export interface ConnectionStatusMessage {
  type: 'connection_status';
  timestamp: Date;
  status: 'connected' | 'disconnected' | 'reconnecting';
  message: string;
}
