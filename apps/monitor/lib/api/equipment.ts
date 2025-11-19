import axios from 'axios';
import { EquipmentListItem } from '../types/equipment';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

interface EquipmentListResponse {
  equipment: EquipmentListItem[];
  total_count: number;
  page: number;
  page_size: number;
}

/**
 * Get equipment list from Oracle DB
 */
export async function getEquipmentList(
  page: number = 1,
  pageSize: number = 50,
  useYn?: string
): Promise<EquipmentListResponse> {
  const params: any = {
    page,
    page_size: pageSize
  };
  
  if (useYn) {
    params.use_yn = useYn;
  }
  
  const response = await apiClient.get<EquipmentListResponse>('/api/monitor/equipment', {
    params
  });
  return response.data;
}

