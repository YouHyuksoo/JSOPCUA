export interface Tag {
  id: number;
  name: string;
  device_address: string;
  data_type: string;
  polling_interval: number;
  unit?: string;
  description?: string;
  plc_id: number;
  plc_name?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateTagRequest {
  name: string;
  device_address: string;
  data_type: string;
  polling_interval: number;
  unit?: string;
  description?: string;
  plc_id: number;
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
