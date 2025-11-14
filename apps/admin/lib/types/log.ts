export interface LogEntry {
  timestamp: string;
  level: "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL";
  message: string;
  stack_trace?: string;
}

export type LogType = "scada" | "error" | "communication" | "performance" | "plc" | "polling" | "oracle_writer";

export interface LogQueryParams {
  log_type: LogType;
  page?: number;
  page_size?: number;
  start_time?: string;
  end_time?: string;
  levels?: string[];
  search?: string;
}

export interface LogQueryResponse {
  logs: LogEntry[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  log_type: string;
}
