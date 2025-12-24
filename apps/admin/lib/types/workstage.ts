// Workstage (공정) 타입 정의
// 백엔드 API: /api/workstages

export interface Workstage {
  id: number;
  machine_code: string | null;
  workstage_sequence: number;
  workstage_code: string;
  workstage_name: string;
  equipment_type: string | null;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateWorkstageRequest {
  machine_code?: string | null;
  workstage_sequence: number;
  workstage_code: string;
  workstage_name: string;
  equipment_type?: string | null;
  enabled?: boolean;
}

export interface UpdateWorkstageRequest {
  workstage_sequence?: number;
  workstage_name?: string;
  equipment_type?: string | null;
  enabled?: boolean;
}

export interface WorkstageFormData {
  machine_code?: string;
  workstage_sequence: number;
  workstage_code: string;
  workstage_name: string;
  equipment_type?: string;
  enabled: boolean;
}
