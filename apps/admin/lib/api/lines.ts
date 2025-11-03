import apiClient from './client';
import { Line, CreateLineRequest } from '@/lib/types/line';
import { PaginatedResponse } from '@/lib/types/common';

export const getLines = async (page = 1, limit = 20) => {
  const response = await apiClient.get<PaginatedResponse<Line>>('/lines', { params: { page, limit } });
  return response.data;
};

export const createLine = async (data: CreateLineRequest) => {
  const response = await apiClient.post<Line>('/lines', data);
  return response.data;
};

export const updateLine = async (id: number, data: CreateLineRequest) => {
  const response = await apiClient.put<Line>(`/lines/${id}`, data);
  return response.data;
};

export const deleteLine = async (id: number) => {
  await apiClient.delete(`/lines/${id}`);
};
