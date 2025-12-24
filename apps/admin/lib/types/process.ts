// Process (공정) 타입 정의
// 백엔드 API: /api/processes

export interface Process {
  id: number;
  machine_id: number;
  process_sequence: number;
  process_code: string;
  process_name: string;
  equipment_type: string | null;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateProcessRequest {
  machine_id: number;
  process_sequence: number;
  process_code: string;
  process_name: string;
  equipment_type?: string | null;
  enabled?: boolean;
}

export interface UpdateProcessRequest {
  process_sequence?: number;
  process_name?: string;
  equipment_type?: string | null;
  enabled?: boolean;
}

export interface ProcessFormData {
  machine_id: number;
  process_sequence: number;
  process_code: string;
  process_name: string;
  equipment_type?: string;
  enabled: boolean;
}
