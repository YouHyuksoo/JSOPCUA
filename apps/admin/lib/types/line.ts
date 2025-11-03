export interface Line {
  id: number;
  name: string;
  code: string;
  created_at: string;
  updated_at: string;
}

export interface CreateLineRequest {
  name: string;
  code: string;
}
