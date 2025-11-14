import apiClient from './client';
import { Tag, CreateTagRequest, CSVUploadResponse } from '@/lib/types/tag';
import { PaginatedResponse } from '@/lib/types/common';

export const getTags = async (page = 1, limit = 20, tag_category?: string, is_active?: boolean) => {
  const params: any = { page, limit };
  if (tag_category) {
    params.tag_category = tag_category;
  }
  if (is_active !== undefined) {
    params.is_active = is_active;
  }
  const response = await apiClient.get<PaginatedResponse<Tag>>('/tags', { params });
  return response.data;
};

export const getTagCategories = async () => {
  const response = await apiClient.get<{ categories: string[] }>('/tags/tag-categories');
  return response.data;
};

export const getTag = async (id: number) => {
  const response = await apiClient.get<Tag>(`/tags/${id}`);
  return response.data;
};

export const createTag = async (data: CreateTagRequest) => {
  const response = await apiClient.post<Tag>('/tags', data);
  return response.data;
};

export const updateTag = async (id: number, data: CreateTagRequest) => {
  const response = await apiClient.put<Tag>(`/tags/${id}`, data);
  return response.data;
};

export const deleteTag = async (id: number) => {
  await apiClient.delete(`/tags/${id}`);
};

export const uploadCSV = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await apiClient.post<CSVUploadResponse>('/tags/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
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
  total_oracle_tags: number;
  created: number;
  updated: number;
  skipped: number;
  errors: number;
  error_details: string[];
}

export const getOracleConnectionInfo = async () => {
  const response = await apiClient.get<OracleConnectionInfo>('/tags/oracle-connection-info');
  return response.data;
};

export const syncTagsFromOracle = async () => {
  const response = await apiClient.post<SyncFromOracleResponse>('/tags/sync-from-oracle');
  return response.data;
};
