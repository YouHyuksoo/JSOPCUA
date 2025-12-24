// Machine (설비) 타입 정의
// 백엔드 API: /api/machines

export interface Machine {
  id: number;
  machine_code: string;
  machine_name: string;
  location: string | null;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateMachineRequest {
  machine_code: string;
  machine_name: string;
  location?: string | null;
  enabled?: boolean;
}

export interface UpdateMachineRequest {
  machine_name?: string;
  location?: string | null;
  enabled?: boolean;
}

export interface MachineFormData {
  machine_code: string;
  machine_name: string;
  location?: string;
  enabled: boolean;
}
