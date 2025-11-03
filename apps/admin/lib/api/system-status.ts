import apiClient from './client';
import { DashboardData } from '@/lib/types/system-status';

export const getDashboardData = async () => {
  const response = await apiClient.get<DashboardData>('/system/status');
  return response.data;
};
