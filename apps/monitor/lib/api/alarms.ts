import axios from 'axios';
import { AlarmStatistics, Alarm } from '../types/alarm';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

interface AlarmStatisticsResponse {
  equipment: AlarmStatistics[];
  last_updated: string;
}

interface RecentAlarmsResponse {
  alarms: Alarm[];
}

/**
 * Get alarm statistics for all equipment
 */
export async function getAlarmStatistics(): Promise<AlarmStatisticsResponse> {
  const response = await apiClient.get<AlarmStatisticsResponse>('/api/alarms/statistics');
  return response.data;
}

/**
 * Get recent alarms
 */
export async function getRecentAlarms(limit: number = 5): Promise<RecentAlarmsResponse> {
  const response = await apiClient.get<RecentAlarmsResponse>('/api/alarms/recent', {
    params: { limit }
  });
  return response.data;
}

/**
 * Check alarm API health
 */
export async function checkAlarmHealth(): Promise<{ status: string; oracle_connection: string }> {
  const response = await apiClient.get('/api/alarms/health');
  return response.data;
}
