import apiClient from './client';

// Types
export interface OperationRecord {
  time: string;
  name: string;
  value: string | null;
}

export interface DatatagLogRecord {
  id: number;
  ctime: string;
  otime: string | null;
  datatag_name: string;
  datatag_type: string | null;
  value_str: string | null;
  value_num: number | null;
  value_raw: string | null;
}

export interface OperationResponse {
  success: boolean;
  total_count: number;
  items: OperationRecord[];
  message?: string;
}

export interface DatatagLogResponse {
  success: boolean;
  total_count: number;
  items: DatatagLogRecord[];
  message?: string;
}

export interface OracleConnectionStatus {
  connected: boolean;
  host: string;
  port: number;
  service_name: string;
  message?: string;
}

export interface DataSummary {
  success: boolean;
  hours: number;
  time_range: {
    from: string;
    to: string;
  };
  xscada_operation: {
    count: number;
  };
  xscada_datatag_log: {
    total_count: number;
    by_type: Record<string, number>;
  };
  message?: string;
}

// API Functions
export const getOracleConnectionStatus = async (): Promise<OracleConnectionStatus> => {
  const response = await apiClient.get<OracleConnectionStatus>('/oracle-data/connection-status');
  return response.data;
};

export const getOperations = async (params?: {
  limit?: number;
  name_filter?: string;
  hours?: number;
}): Promise<OperationResponse> => {
  const response = await apiClient.get<OperationResponse>('/oracle-data/operations', { params });
  return response.data;
};

export const getDatatagLogs = async (params?: {
  limit?: number;
  datatag_name_filter?: string;
  datatag_type_filter?: string;
  hours?: number;
}): Promise<DatatagLogResponse> => {
  const response = await apiClient.get<DatatagLogResponse>('/oracle-data/datatag-logs', { params });
  return response.data;
};

export const getDataSummary = async (hours?: number): Promise<DataSummary> => {
  const response = await apiClient.get<DataSummary>('/oracle-data/summary', {
    params: hours ? { hours } : undefined,
  });
  return response.data;
};
