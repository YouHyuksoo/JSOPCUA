/**
 * Polling Engine API Client
 *
 * TypeScript client for polling engine REST API
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface GroupStatus {
  group_id: number;
  group_name: string;
  mode: 'FIXED' | 'HANDSHAKE';
  state: 'running' | 'stopped' | 'stopping' | 'error';
  last_poll_time: string | null;
  total_polls: number;
  success_count: number;
  error_count: number;
  success_rate: number;
  avg_poll_time_ms: number;
  consecutive_failures: number;
  last_error: string | null;
  next_retry_in: number | null;
}

export interface QueueStatus {
  queue_size: number;
  queue_maxsize: number;
  queue_is_full: boolean;
}

export interface EngineStatus {
  groups: GroupStatus[];
  queue: QueueStatus;
  timestamp: string;
}

export interface TriggerResponse {
  success: boolean;
  group_name: string;
  mode: string;
  message: string;
  tag_count?: number;
}

export interface PreStartCheckResponse {
  can_start: boolean;
  reason: string;
  message: string;
  group_name: string;
  plc_code: string;
  plc_name?: string;
  plc_ip?: string;
  plc_port?: number;
  tag_count: number;
  interval_ms?: number;
  plc_status: 'connected' | 'connection_failed' | 'inactive' | 'unknown';
  error_detail?: string;
}

class PollingApi {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Get complete engine status
   */
  async getEngineStatus(): Promise<EngineStatus> {
    const response = await fetch(`${this.baseUrl}/api/polling/status`);
    if (!response.ok) {
      throw new Error(`Failed to get engine status: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get status of specific group
   */
  async getGroupStatus(groupName: string): Promise<GroupStatus> {
    const response = await fetch(`${this.baseUrl}/api/polling/groups/${groupName}/status`);
    if (!response.ok) {
      throw new Error(`Failed to get group status: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Pre-start check for polling group
   */
  async preStartCheck(groupId: number): Promise<PreStartCheckResponse> {
    const response = await fetch(`${this.baseUrl}/api/polling-groups/${groupId}/pre-start-check`);
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Failed to check group: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Start a polling group
   */
  async startGroup(groupName: string): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/polling/groups/${groupName}/start`, {
      method: 'POST',
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Failed to start group: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Stop a polling group
   */
  async stopGroup(groupName: string, timeout: number = 5.0): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/polling/groups/${groupName}/stop?timeout=${timeout}`, {
      method: 'POST',
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Failed to stop group: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Trigger HANDSHAKE mode polling
   */
  async triggerHandshake(groupName: string): Promise<TriggerResponse> {
    const response = await fetch(`${this.baseUrl}/api/polling/groups/${groupName}/trigger`, {
      method: 'POST',
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Failed to trigger poll: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Start all polling groups
   */
  async startAll(): Promise<{ success: boolean; message: string; running_count: number }> {
    const response = await fetch(`${this.baseUrl}/api/polling/start-all`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Failed to start all groups: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Stop all polling groups
   */
  async stopAll(timeout: number = 5.0): Promise<{ success: boolean; message: string; stopped_count: number }> {
    const response = await fetch(`${this.baseUrl}/api/polling/stop-all?timeout=${timeout}`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Failed to stop all groups: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get queue status
   */
  async getQueueStatus(): Promise<QueueStatus> {
    const response = await fetch(`${this.baseUrl}/api/polling/queue/status`);
    if (!response.ok) {
      throw new Error(`Failed to get queue status: ${response.statusText}`);
    }
    return response.json();
  }
}

export const pollingApi = new PollingApi();
