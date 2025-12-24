import apiClient from './client';
import { Machine, CreateMachineRequest, UpdateMachineRequest } from '@/lib/types/machine';
import { PaginatedResponse } from '@/lib/types/common';

export const getMachines = async (page = 1, limit = 20) => {
  const response = await apiClient.get<PaginatedResponse<Machine>>('/machines', { params: { page, limit } });
  return response.data;
};

export const getMachine = async (id: number) => {
  const response = await apiClient.get<Machine>(`/machines/${id}`);
  return response.data;
};

export const createMachine = async (data: CreateMachineRequest) => {
  const response = await apiClient.post<Machine>('/machines', data);
  return response.data;
};

export const updateMachine = async (id: number, data: UpdateMachineRequest) => {
  const response = await apiClient.put<Machine>(`/machines/${id}`, data);
  return response.data;
};

export const deleteMachine = async (id: number) => {
  await apiClient.delete(`/machines/${id}`);
};

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
  total_oracle_machines: number;
  created: number;
  updated: number;
  skipped: number;
  errors: number;
  error_details: string[];
}

export const getOracleConnectionInfo = async () => {
  const response = await apiClient.get<OracleConnectionInfo>('/machines/oracle-connection-info');
  return response.data;
};

export const syncMachinesFromOracle = async () => {
  const response = await apiClient.post<SyncFromOracleResponse>('/machines/sync-from-oracle');
  return response.data;
};
