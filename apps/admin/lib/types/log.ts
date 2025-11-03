export interface LogEntry {
  timestamp: string;
  level: "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL";
  message: string;
  stack_trace?: string;
}

export interface LogQueryParams {
  log_type: "scada" | "error" | "communication" | "performance";
  start_time?: string;
  end_time?: string;
  levels?: string[];
  search?: string;
  page: number;
  limit: number;
}

export interface LogQueryResponse {
  items: LogEntry[];
  total: number;
  page: number;
  limit: number;
}
