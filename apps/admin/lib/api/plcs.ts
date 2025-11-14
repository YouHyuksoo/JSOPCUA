import apiClient from './client';
import { PLC, CreatePLCRequest, PLCTestResponse } from '@/lib/types/plc';
import { PaginatedResponse } from '@/lib/types/common';

export const getPLCs = async (page = 1, limit = 20) => {
  const response = await apiClient.get<PaginatedResponse<PLC>>('/plc-connections', { params: { page, limit } });
  return response.data;
};

export const createPLC = async (data: CreatePLCRequest) => {
  const response = await apiClient.post<PLC>('/plc-connections', data);
  return response.data;
};

export const updatePLC = async (id: number, data: CreatePLCRequest) => {
  const response = await apiClient.put<PLC>(`/plc-connections/${id}`, data);
  return response.data;
};

export const deletePLC = async (id: number) => {
  await apiClient.delete(`/plc-connections/${id}`);
};

export const testPLCConnection = async (id: number) => {
  const response = await apiClient.post<PLCTestResponse>(`/plc-connections/${id}/test`);
  return response.data;
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
  total_oracle_plcs: number;
  created: number;
  updated: number;
  skipped: number;
  errors: number;
  error_details: string[];
}

export const getOracleConnectionInfo = async () => {
  const response = await apiClient.get<OracleConnectionInfo>('/plc-connections/oracle-connection-info');
  return response.data;
};

export const syncPLCsFromOracle = async () => {
  const response = await apiClient.post<SyncFromOracleResponse>('/plc-connections/sync-from-oracle');
  return response.data;
};
