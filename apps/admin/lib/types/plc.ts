export interface PLC {
  id: number;
  name: string;
  ip_address: string;
  port: number;
  plc_type: string;
  protocol: string;
  process_id: number;
  process_name?: string;
  is_connected: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreatePLCRequest {
  name: string;
  ip_address: string;
  port: number;
  plc_type: string;
  protocol: string;
  process_id: number;
}

export interface PLCTestResponse {
  success: boolean;
  message: string;
  response_time_ms?: number;
}
