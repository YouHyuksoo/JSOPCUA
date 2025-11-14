export interface Tag {
  id: number;
  plc_id: number;
  plc_code?: string | null;  // PLC code from plc_connections
  process_id: number;
  tag_address: string;
  tag_name: string;
  tag_division: string;
  tag_category?: string | null;
  data_type: string;
  unit?: string | null;
  scale: number;
  machine_code?: string | null;
  polling_group_id?: number | null;
  enabled: boolean;
  created_at: string;
  updated_at: string;
  // Legacy fields for compatibility
  tag_id?: string;
}

export interface CreateTagRequest {
  plc_id: number;
  process_id: number;
  tag_address: string;
  tag_name: string;
  tag_division?: string;
  data_type: string;
  unit?: string;
  scale?: number;
  machine_code?: string;
  polling_group_id?: number;
  enabled?: boolean;
}

export interface CSVUploadResponse {
  success_count: number;
  fail_count: number;
  errors: Array<{
    row: number;
    field: string;
    message: string;
  }>;
}
