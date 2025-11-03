import apiClient from './client';
import { LogQueryResponse, LogQueryParams } from '@/lib/types/log';

export const getLogs = async (params: LogQueryParams) => {
  const { log_type, ...queryParams } = params;
  const response = await apiClient.get<LogQueryResponse>(`/logs/${log_type}`, { params: queryParams });
  return response.data;
};

export const downloadLogs = async (params: LogQueryParams) => {
  const { log_type, ...queryParams } = params;
  const response = await apiClient.get(`/logs/${log_type}/download`, { 
    params: queryParams,
    responseType: 'blob'
  });
  return response.data;
};
