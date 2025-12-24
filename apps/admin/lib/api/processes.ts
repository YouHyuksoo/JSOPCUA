import apiClient from './client';
import { Process, CreateProcessRequest } from '@/lib/types/process';
import { PaginatedResponse } from '@/lib/types/common';

export const getProcesses = async (page = 1, limit = 20, machine_code?: string) => {
  const params: any = { page, limit };
  if (machine_code) {
    params.machine_code = machine_code;
  }
  const response = await apiClient.get<PaginatedResponse<Process>>('/processes', { params });
  return response.data;
};

export const getProcess = async (id: number) => {
  const response = await apiClient.get<Process>(`/processes/${id}`);
  return response.data;
};

export const createProcess = async (data: CreateProcessRequest) => {
  const response = await apiClient.post<Process>('/processes', data);
  return response.data;
};

export const updateProcess = async (id: number, data: CreateProcessRequest) => {
  const response = await apiClient.put<Process>(`/processes/${id}`, data);
  return response.data;
};

export const deleteProcess = async (id: number) => {
  await apiClient.delete(`/processes/${id}`);
};

// Oracle Synchronization
export interface OracleConnectionInfo {
  host: string;
  port: number;
  service_name: string;
  username: string;
  password: string; // masked
  pool_min: number;
  pool_max: number;
  dsn: string;
}

export interface SyncFromOracleResponse {
  success: boolean;
  total_oracle_processes: number;
  created: number;
  updated: number;
  skipped: number;
  errors: number;
  error_details: string[];
}

export const getOracleConnectionInfo = async () => {
  const response = await apiClient.get<OracleConnectionInfo>('/processes/oracle-connection-info');
  return response.data;
};

export const syncProcessesFromOracle = async () => {
  const response = await apiClient.post<SyncFromOracleResponse>('/processes/sync-from-oracle');
  return response.data;
};
