import apiClient from './client';
import { PollingGroup, CreatePollingGroupRequest, PollingControlResponse } from '@/lib/types/polling-group';
import { PaginatedResponse } from '@/lib/types/common';

export const getPollingGroups = async (page = 1, limit = 20) => {
  const response = await apiClient.get<PaginatedResponse<PollingGroup>>('/polling/groups', { params: { page, limit } });
  return response.data;
};

export const createPollingGroup = async (data: CreatePollingGroupRequest) => {
  const response = await apiClient.post<PollingGroup>('/polling/groups', data);
  return response.data;
};

export const updatePollingGroup = async (id: number, data: CreatePollingGroupRequest) => {
  const response = await apiClient.put<PollingGroup>(`/polling/groups/${id}`, data);
  return response.data;
};

export const deletePollingGroup = async (id: number) => {
  await apiClient.delete(`/polling/groups/${id}`);
};

export const startPollingGroup = async (id: number) => {
  const response = await apiClient.post<PollingControlResponse>(`/polling/groups/${id}/start`);
  return response.data;
};

export const stopPollingGroup = async (id: number) => {
  const response = await apiClient.post<PollingControlResponse>(`/polling/groups/${id}/stop`);
  return response.data;
};

export const restartPollingGroup = async (id: number) => {
  const response = await apiClient.post<PollingControlResponse>(`/polling/groups/${id}/restart`);
  return response.data;
};
