import apiClient from './client';
import { Workstage, CreateWorkstageRequest } from '@/lib/types/workstage';
import { PaginatedResponse } from '@/lib/types/common';

export const getWorkstages = async (page = 1, limit = 20, machine_code?: string) => {
  const params: any = { page, limit };
  if (machine_code) {
    params.machine_code = machine_code;
  }
  const response = await apiClient.get<PaginatedResponse<Workstage>>('/workstages', { params });
  return response.data;
};

export const getWorkstage = async (id: number) => {
  const response = await apiClient.get<Workstage>(`/workstages/${id}`);
  return response.data;
};

export const createWorkstage = async (data: CreateWorkstageRequest) => {
  const response = await apiClient.post<Workstage>('/workstages', data);
  return response.data;
};

export const updateWorkstage = async (id: number, data: CreateWorkstageRequest) => {
  const response = await apiClient.put<Workstage>(`/workstages/${id}`, data);
  return response.data;
};

export const deleteWorkstage = async (id: number) => {
  await apiClient.delete(`/workstages/${id}`);
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
  total_oracle_workstages: number;
  created: number;
  updated: number;
  skipped: number;
  errors: number;
  error_details: string[];
}

export const getOracleConnectionInfo = async () => {
  const response = await apiClient.get<OracleConnectionInfo>('/workstages/oracle-connection-info');
  return response.data;
};

export const syncWorkstagesFromOracle = async () => {
  const response = await apiClient.post<SyncFromOracleResponse>('/workstages/sync-from-oracle');
  return response.data;
};
