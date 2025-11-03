import apiClient from './client';
import { PLC, CreatePLCRequest, PLCTestResponse } from '@/lib/types/plc';
import { PaginatedResponse } from '@/lib/types/common';

export const getPLCs = async (page = 1, limit = 20) => {
  const response = await apiClient.get<PaginatedResponse<PLC>>('/plc_connections', { params: { page, limit } });
  return response.data;
};

export const createPLC = async (data: CreatePLCRequest) => {
  const response = await apiClient.post<PLC>('/plc_connections', data);
  return response.data;
};

export const updatePLC = async (id: number, data: CreatePLCRequest) => {
  const response = await apiClient.put<PLC>(`/plc_connections/${id}`, data);
  return response.data;
};

export const deletePLC = async (id: number) => {
  await apiClient.delete(`/plc_connections/${id}`);
};

export const testPLCConnection = async (id: number) => {
  const response = await apiClient.post<PLCTestResponse>(`/plc_connections/${id}/test`);
  return response.data;
};
