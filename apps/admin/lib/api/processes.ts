import apiClient from './client';
import { Process, CreateProcessRequest } from '@/lib/types/process';
import { PaginatedResponse } from '@/lib/types/common';

export const getProcesses = async (page = 1, limit = 20) => {
  const response = await apiClient.get<PaginatedResponse<Process>>('/processes', { params: { page, limit } });
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
