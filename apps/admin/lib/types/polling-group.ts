export interface PollingGroup {
  id: number;
  name: string;
  polling_interval: number;
  is_active: boolean;
  status: "stopped" | "running" | "error";
  last_poll_time?: string;
  success_rate?: number;
  tag_count: number;
  created_at: string;
  updated_at: string;
}

export interface CreatePollingGroupRequest {
  name: string;
  polling_interval: number;
  is_active: boolean;
  tag_ids: number[];
}

export interface PollingControlResponse {
  success: boolean;
  message: string;
  new_status: string;
}
