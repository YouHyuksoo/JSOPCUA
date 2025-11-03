export interface SystemStatus {
  cpu_percent: number;
  memory_used_gb: number;
  memory_total_gb: number;
  memory_percent: number;
  disk_used_gb: number;
  disk_total_gb: number;
  disk_percent: number;
  timestamp: string;
}

export interface PLCStatus {
  plc_id: number;
  plc_name: string;
  is_online: boolean;
  last_seen?: string;
}

export interface BufferStatus {
  current_size: number;
  max_size: number;
  utilization_percent: number;
  overflow_count: number;
  last_overflow_time?: string;
}

export interface OracleWriterStatus {
  success_count: number;
  fail_count: number;
  success_rate_percent: number;
  backup_file_count: number;
}

export interface DashboardData {
  system: SystemStatus;
  plc_status: PLCStatus[];
  active_polling_groups: number;
  total_polling_groups: number;
  buffer: BufferStatus;
  oracle_writer: OracleWriterStatus;
}
