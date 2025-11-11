'use client';

/**
 * Polling Engine Management Page (WebSocket version)
 *
 * Real-time monitoring using WebSocket for live updates
 */

import { useState } from 'react';
import { pollingApi } from '@/lib/api/pollingApi';
import { usePollingWebSocket } from '@/lib/hooks/usePollingWebSocket';
// import QueueMonitor from '../polling/components/QueueMonitor';
// import PollingChart from '../polling/components/PollingChart';

export default function PollingWebSocketPage() {
  const { status: engineStatus, isConnected, error: wsError, reconnect } = usePollingWebSocket();
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);

  // Start group
  const handleStartGroup = async (groupName: string) => {
    setActionLoading(groupName);
    setApiError(null);
    try {
      await pollingApi.startGroup(groupName);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to start group';
      setApiError(message);
      alert(message);
    } finally {
      setActionLoading(null);
    }
  };

  // Stop group
  const handleStopGroup = async (groupName: string) => {
    setActionLoading(groupName);
    setApiError(null);
    try {
      await pollingApi.stopGroup(groupName);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to stop group';
      setApiError(message);
      alert(message);
    } finally {
      setActionLoading(null);
    }
  };

  // Trigger HANDSHAKE
  const handleTrigger = async (groupName: string) => {
    setActionLoading(groupName);
    setApiError(null);
    try {
      const result = await pollingApi.triggerHandshake(groupName);
      if (result.success) {
        alert(`Poll triggered: ${result.tag_count} tags`);
      } else {
        alert(result.message);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to trigger poll';
      setApiError(message);
      alert(message);
    } finally {
      setActionLoading(null);
    }
  };

  // Start all
  const handleStartAll = async () => {
    setActionLoading('all');
    setApiError(null);
    try {
      const result = await pollingApi.startAll();
      alert(`Started ${result.running_count} groups`);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to start all';
      setApiError(message);
      alert(message);
    } finally {
      setActionLoading(null);
    }
  };

  // Stop all
  const handleStopAll = async () => {
    setActionLoading('all');
    setApiError(null);
    try {
      const result = await pollingApi.stopAll();
      alert(`Stopped ${result.stopped_count} groups`);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to stop all';
      setApiError(message);
      alert(message);
    } finally {
      setActionLoading(null);
    }
  };

  // Get state badge color
  const getStateBadgeClass = (state: string) => {
    switch (state) {
      case 'running': return 'bg-green-500/10 text-green-400 border border-green-500/20';
      case 'stopped': return 'bg-gray-500/10 text-gray-400 border border-gray-500/20';
      case 'stopping': return 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20';
      case 'error': return 'bg-red-500/10 text-red-400 border border-red-500/20';
      default: return 'bg-gray-500/10 text-gray-400 border border-gray-500/20';
    }
  };

  // Get mode badge color
  const getModeBadgeClass = (mode: string) => {
    return mode === 'FIXED' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'bg-purple-500/10 text-purple-400 border border-purple-500/20';
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold mb-2 text-gray-100">Polling Engine Management (WebSocket)</h1>
            <p className="text-gray-400">Real-time monitoring via WebSocket</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-gray-400">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            {!isConnected && (
              <button
                onClick={reconnect}
                className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700"
              >
                Reconnect
              </button>
            )}
          </div>
        </div>
      </div>

      {(wsError || apiError) && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded mb-6">
          <strong>Error:</strong> {wsError || apiError}
        </div>
      )}

      {!engineStatus && !wsError && (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-xl text-gray-300">Connecting to polling engine...</div>
        </div>
      )}

      {engineStatus && (
        <>
          {/* Queue Monitor - TODO: Implement QueueMonitor component */}
          {/* <div className="mb-6">
            <QueueMonitor queue={engineStatus.queue} />
          </div> */}

          {/* Performance Chart - TODO: Implement PollingChart component */}
          {/* {engineStatus.groups.length > 0 && (
            <div className="mb-6">
              <PollingChart groups={engineStatus.groups} />
            </div>
          )} */}

          {/* Control Buttons */}
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-100">Global Controls</h2>
            <div className="flex gap-4">
              <button
                onClick={handleStartAll}
                disabled={actionLoading === 'all'}
                className="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed"
              >
                {actionLoading === 'all' ? 'Processing...' : 'Start All Groups'}
              </button>
              <button
                onClick={handleStopAll}
                disabled={actionLoading === 'all'}
                className="bg-red-600 text-white px-6 py-2 rounded hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed"
              >
                {actionLoading === 'all' ? 'Processing...' : 'Stop All Groups'}
              </button>
            </div>
          </div>

          {/* Polling Groups */}
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-100">Polling Groups</h2>

            {engineStatus.groups.length === 0 && (
              <div className="text-center text-gray-500 py-8">
                No polling groups configured
              </div>
            )}

            <div className="space-y-4">
              {engineStatus.groups.map((group) => (
                <div key={group.group_name} className="border border-gray-800 bg-gray-950 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-semibold text-gray-100">{group.group_name}</h3>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getModeBadgeClass(group.mode)}`}>
                        {group.mode}
                      </span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStateBadgeClass(group.state)}`}>
                        {group.state}
                      </span>
                    </div>
                    <div className="flex gap-2">
                      {group.state === 'stopped' && (
                        <button
                          onClick={() => handleStartGroup(group.group_name)}
                          disabled={actionLoading === group.group_name}
                          className="bg-green-600 text-white px-4 py-1 rounded text-sm hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed"
                        >
                          Start
                        </button>
                      )}
                      {group.state === 'running' && (
                        <button
                          onClick={() => handleStopGroup(group.group_name)}
                          disabled={actionLoading === group.group_name}
                          className="bg-red-600 text-white px-4 py-1 rounded text-sm hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed"
                        >
                          Stop
                        </button>
                      )}
                      {group.mode === 'HANDSHAKE' && group.state === 'running' && (
                        <button
                          onClick={() => handleTrigger(group.group_name)}
                          disabled={actionLoading === group.group_name}
                          className="bg-purple-600 text-white px-4 py-1 rounded text-sm hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed"
                        >
                          Trigger Poll
                        </button>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-400">Total Polls:</span>
                      <span className="ml-2 font-medium text-gray-200">{group.total_polls}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Success:</span>
                      <span className="ml-2 font-medium text-green-400">{group.success_count}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Errors:</span>
                      <span className="ml-2 font-medium text-red-400">{group.error_count}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Avg Time:</span>
                      <span className="ml-2 font-medium text-gray-200">{group.avg_poll_time_ms.toFixed(2)}ms</span>
                    </div>
                  </div>

                  {group.last_poll_time && (
                    <div className="mt-2 text-sm text-gray-400">
                      Last poll: {new Date(group.last_poll_time).toLocaleString()}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Last Updated */}
          <div className="mt-4 text-sm text-gray-500 text-right">
            Last updated: {new Date(engineStatus.timestamp).toLocaleTimeString()}
          </div>
        </>
      )}
    </div>
  );
}
