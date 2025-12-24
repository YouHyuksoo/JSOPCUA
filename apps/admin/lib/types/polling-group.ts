export interface PollingGroup {
  id: number;
  name: string;
  plc_code: string;
  line_code?: string | null;
  machine_code?: string | null;
  workstage_code?: string | null;
  mode: "FIXED" | "HANDSHAKE";
  polling_interval: number;
  group_category?: string | null;
  trigger_bit_address?: string | null;
  trigger_bit_offset?: number;
  auto_reset_trigger?: boolean;
  priority?: string | null;
  description?: string | null;
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
  plc_code: string;
  workstage_code?: string;
  polling_interval: number;
  /** 동작구분: OPERATION(동작), STATE(상태), ALARM(알람) */
  group_category?: string;
  description?: string;
  is_active: boolean;
  tag_ids: number[];
}

export interface PollingControlResponse {
  success: boolean;
  message: string;
  new_status: string;
}
