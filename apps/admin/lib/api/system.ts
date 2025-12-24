const API_BASE = 'http://localhost:8000';

export interface SystemStatus {
  status: 'stopped' | 'starting' | 'running' | 'stopping' | 'unavailable' | 'error';
  started_at?: string;
  uptime_seconds?: number;
  polling_groups_loaded: number;
  polling_groups_running: number;
}

export async function getSystemStatus(): Promise<SystemStatus> {
  const response = await fetch(`${API_BASE}/api/system/status`);
  if (!response.ok) {
    throw new Error('Failed to fetch system status');
  }
  return response.json();
}

export async function startSystem(): Promise<{ success: boolean; message: string; status: string }> {
  const response = await fetch(`${API_BASE}/api/system/start`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error('Failed to start system');
  }
  return response.json();
}

export async function stopSystem(): Promise<{ success: boolean; message: string; status: string }> {
  const response = await fetch(`${API_BASE}/api/system/stop`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error('Failed to stop system');
  }
  return response.json();
}

export async function restartSystem(): Promise<{ success: boolean; message: string; status: string }> {
  const response = await fetch(`${API_BASE}/api/system/restart`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error('Failed to restart system');
  }
  return response.json();
}

// Environment Configuration Management
export interface EnvConfig {
  [key: string]: string;
}

export interface EnvConfigUpdate {
  // Database
  DATABASE_PATH?: string;

  // API Server
  API_HOST?: string;
  API_PORT?: number;
  API_RELOAD?: boolean;

  // CORS
  CORS_ORIGINS?: string;

  // Logging
  LOG_LEVEL?: string;
  LOG_DIR?: string;

  // Polling Engine
  MAX_POLLING_GROUPS?: number;
  DATA_QUEUE_SIZE?: number;

  // PLC Connection Pool
  POOL_SIZE_PER_PLC?: number;
  CONNECTION_TIMEOUT?: number;
  READ_TIMEOUT?: number;

  // Oracle Database
  ORACLE_HOST?: string;
  ORACLE_PORT?: number;
  ORACLE_SERVICE_NAME?: string;
  ORACLE_USERNAME?: string;
  ORACLE_PASSWORD?: string;
  ORACLE_POOL_MIN?: number;
  ORACLE_POOL_MAX?: number;

  // Buffer Configuration
  BUFFER_MAX_SIZE?: number;
  BUFFER_BATCH_SIZE?: number;
  BUFFER_WRITE_INTERVAL?: number;
}

export async function getEnvConfig(): Promise<EnvConfig> {
  const response = await fetch(`${API_BASE}/api/system/env-config`);
  if (!response.ok) {
    throw new Error('Failed to fetch environment configuration');
  }
  return response.json();
}

export async function updateEnvConfig(
  config: EnvConfigUpdate
): Promise<{ success: boolean; message: string; config: EnvConfig }> {
  const response = await fetch(`${API_BASE}/api/system/env-config`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(config),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update environment configuration');
  }
  return response.json();
}

export interface OracleConnectionTestResponse {
  success: boolean;
  message: string;
  connection_info?: {
    host: string;
    port: string;
    service_name: string;
    username: string;
    dsn: string;
  };
  error_details?: string;
}

export async function testOracleConnection(): Promise<OracleConnectionTestResponse> {
  const response = await fetch(`${API_BASE}/api/system/test-oracle-connection`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to test Oracle connection');
  }
  return response.json();
}
