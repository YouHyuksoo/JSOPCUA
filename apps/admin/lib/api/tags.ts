import apiClient from './client';
import { Tag, CreateTagRequest, CSVUploadResponse } from '@/lib/types/tag';
import { PaginatedResponse } from '@/lib/types/common';

export const getTags = async (page = 1, limit = 20) => {
  const response = await apiClient.get<PaginatedResponse<Tag>>('/tags', { params: { page, limit } });
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
