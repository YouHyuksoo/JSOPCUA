export interface Process {
  id: number;
  name: string;
  code: string;
  line_id: number;
  line_name?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateProcessRequest {
  name: string;
  code: string;
  line_id: number;
}
