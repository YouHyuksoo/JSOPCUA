'use client';

/**
 * Polling Engine Management Page (WebSocket version)
 *
 * Real-time monitoring using WebSocket for live updates
 */

import { useState, useEffect } from 'react';
import { pollingApi } from '@/lib/api/pollingApi';
import { usePollingWebSocket } from '@/lib/hooks/usePollingWebSocket';
import { useToast } from '@/hooks/use-toast';
// import QueueMonitor from '../polling/components/QueueMonitor';
// import PollingChart from '../polling/components/PollingChart';

export default function PollingWebSocketPage() {
  const { status: engineStatus, isConnected, error: wsError, reconnect } = usePollingWebSocket();
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [monitoringActive, setMonitoringActive] = useState(true);
  const [groupTagCounts, setGroupTagCounts] = useState<Record<number, number>>({});
  const [groupPlcStatus, setGroupPlcStatus] = useState<Record<number, 'connected' | 'connection_failed' | 'inactive' | 'unknown'>>({});
  const { toast } = useToast();

  // Load tag counts for all groups when engine status is available
  useEffect(() => {
    if (!engineStatus?.groups) return;

    const loadTagCounts = async () => {
      const groupIds = engineStatus.groups.map(g => g.group_id);

      for (const group of engineStatus.groups) {
        // Skip if already loaded
        if (groupTagCounts[group.group_id] !== undefined) continue;

        try {
          const checkResult = await pollingApi.preStartCheck(group.group_id);
          setGroupTagCounts(prev => ({ ...prev, [group.group_id]: checkResult.tag_count }));
          setGroupPlcStatus(prev => ({ ...prev, [group.group_id]: checkResult.plc_status }));
        } catch (err) {
          console.error(`Failed to load tag count for ${group.group_name}:`, err);
          setGroupPlcStatus(prev => ({ ...prev, [group.group_id]: 'unknown' }));
        }
      }
    };

    loadTagCounts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [engineStatus?.groups?.length]); // Only re-run when group count changes

  // Start group
  const handleStartGroup = async (groupName: string) => {
    setActionLoading(groupName);
    setApiError(null);

    // 그룹 정보 찾기
    if (!engineStatus?.groups) {
      toast({
        title: "오류",
        description: "폴링 엔진 상태를 가져올 수 없습니다.",
        variant: "destructive",
      });
      setActionLoading(null);
      return;
    }

    const group = engineStatus.groups.find(g => g.group_name === groupName);
    if (!group) {
      toast({
        title: "오류",
        description: "폴링 그룹을 찾을 수 없습니다.",
        variant: "destructive",
      });
      setActionLoading(null);
      return;
    }

    try {
      // 1단계: 사전 체크 (PLC 연결, 태그 개수 등)
      toast({
        title: "사전 체크 중...",
        description: `PLC 연결 상태와 태그를 확인하고 있습니다.`,
      });

      const checkResult = await pollingApi.preStartCheck(group.group_id);

      // 태그 개수 저장
      setGroupTagCounts(prev => ({ ...prev, [group.group_id]: checkResult.tag_count }));

      // 시작 불가능한 경우
      if (!checkResult.can_start) {
        let errorMessage = checkResult.message;

        // 상세 정보 추가
        if (checkResult.reason === 'NO_TAGS') {
          errorMessage += '\n\n폴링 그룹에 활성 태그를 추가해주세요.';
        } else if (checkResult.reason === 'PLC_CONNECTION_FAILED') {
          errorMessage += `\n\nPLC 정보: ${checkResult.plc_ip}:${checkResult.plc_port}`;
          if (checkResult.error_detail) {
            errorMessage += `\n오류 상세: ${checkResult.error_detail}`;
          }
        } else if (checkResult.reason === 'PLC_INACTIVE') {
          errorMessage += '\n\nPLC 연결 설정에서 PLC를 활성화해주세요.';
        }

        toast({
          title: "폴링 시작 불가",
          description: errorMessage,
          variant: "destructive",
        });
        setActionLoading(null);
        return;
      }

      // 시작 가능 - 정보 표시
      toast({
        title: "사전 체크 완료 ✓",
        description: `PLC: ${checkResult.plc_ip}:${checkResult.plc_port} | 태그: ${checkResult.tag_count}개`,
      });

      // 2단계: 실제 폴링 시작
      toast({
        title: "폴링 시작 중...",
        description: `${groupName} 폴링 그룹을 시작하고 있습니다.`,
      });

      await pollingApi.startGroup(groupName);

      // 성공 메시지
      toast({
        title: "폴링 시작 완료",
        description: `${groupName} 폴링 그룹이 시작되었습니다. (태그 ${checkResult.tag_count}개, 주기 ${checkResult.interval_ms}ms)`,
        variant: "default",
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to start group';
      setApiError(message);

      // 오류 메시지
      toast({
        title: "폴링 시작 실패",
        description: message,
        variant: "destructive",
      });
    } finally {
      setActionLoading(null);
    }
  };

  // Stop group
  const handleStopGroup = async (groupName: string) => {
    setActionLoading(groupName);
    setApiError(null);

    toast({
      title: "폴링 중지 중...",
      description: `${groupName} 폴링 그룹을 중지하고 있습니다.`,
    });

    try {
      await pollingApi.stopGroup(groupName);

      toast({
        title: "폴링 중지 완료",
        description: `${groupName} 폴링 그룹이 중지되었습니다.`,
        variant: "default",
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to stop group';
      setApiError(message);

      toast({
        title: "폴링 중지 실패",
        description: message,
        variant: "destructive",
      });
    } finally {
      setActionLoading(null);
    }
  };

  // Trigger HANDSHAKE
  const handleTrigger = async (groupName: string) => {
    setActionLoading(groupName);
    setApiError(null);

    toast({
      title: "폴링 트리거 중...",
      description: `${groupName} 수동 폴링을 실행하고 있습니다.`,
    });

    try {
      const result = await pollingApi.triggerHandshake(groupName);
      if (result.success) {
        toast({
          title: "폴링 트리거 완료",
          description: `${result.tag_count}개의 태그가 폴링되었습니다.`,
          variant: "default",
        });
      } else {
        toast({
          title: "폴링 트리거 실패",
          description: result.message,
          variant: "destructive",
        });
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to trigger poll';
      setApiError(message);

      toast({
        title: "폴링 트리거 오류",
        description: message,
        variant: "destructive",
      });
    } finally {
      setActionLoading(null);
    }
  };

  // Start all
  const handleStartAll = async () => {
    setActionLoading('all');
    setApiError(null);

    // 진행 상태 메시지 표시
    toast({
      title: "전체 폴링 시작 중...",
      description: "모든 폴링 그룹을 시작하고 있습니다.",
    });

    try {
      const result = await pollingApi.startAll();

      // 성공 메시지
      toast({
        title: "전체 폴링 시작 완료",
        description: `${result.running_count}개의 폴링 그룹이 시작되었습니다. 모든 오류 내역이 초기화되었습니다.`,
        variant: "default",
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to start all';
      setApiError(message);

      // 오류 메시지
      toast({
        title: "전체 폴링 시작 실패",
        description: message,
        variant: "destructive",
      });
    } finally {
      setActionLoading(null);
    }
  };

  // Stop all
  const handleStopAll = async () => {
    setActionLoading('all');
    setApiError(null);

    toast({
      title: "전체 폴링 중지 중...",
      description: "모든 폴링 그룹을 중지하고 있습니다.",
    });

    try {
      const result = await pollingApi.stopAll();

      toast({
        title: "전체 폴링 중지 완료",
        description: `${result.stopped_count}개의 폴링 그룹이 중지되었습니다.`,
        variant: "default",
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to stop all';
      setApiError(message);

      toast({
        title: "전체 폴링 중지 실패",
        description: message,
        variant: "destructive",
      });
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
        <div>
          <h1 className="text-3xl font-bold mb-2 text-gray-100">폴링 모니터링</h1>
          <p className="text-gray-400">실시간 폴링 상태 모니터링 및 제어</p>
        </div>
      </div>

      {(wsError || apiError) && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded mb-6">
          <strong>Error:</strong> {wsError || apiError}
        </div>
      )}

      {!engineStatus && !wsError && (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-xl text-gray-300">폴링 엔진에 연결 중...</div>
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

          {/* Control Panel - Combined */}
          <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-800/30 rounded-lg p-6 mb-6">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-8">
                {/* Monitoring Control */}
                <div className="flex items-center gap-4">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-100">모니터링 제어</h2>
                    <p className="text-xs text-gray-400">실시간 업데이트 표시</p>
                  </div>
                  <div className="flex items-center gap-3">
                    {/* WebSocket Status */}
                    <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-900/50 rounded border border-gray-700">
                      <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                      <span className="text-xs text-gray-300">
                        {isConnected ? 'WS 연결됨' : 'WS 끊김'}
                      </span>
                      {!isConnected && (
                        <button
                          onClick={reconnect}
                          className="ml-1 text-xs text-blue-400 hover:text-blue-300 underline"
                        >
                          재연결
                        </button>
                      )}
                    </div>
                    {/* Monitoring Status */}
                    <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-900/50 rounded border border-gray-700">
                      <div className={`w-2 h-2 rounded-full ${monitoringActive ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`} />
                      <span className="text-xs text-gray-300">
                        {monitoringActive ? '모니터링 활성' : '모니터링 비활성'}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => setMonitoringActive(!monitoringActive)}
                    className={`px-4 py-2 rounded font-medium transition-colors text-sm ${
                      monitoringActive
                        ? 'bg-yellow-600 hover:bg-yellow-700 text-white'
                        : 'bg-green-600 hover:bg-green-700 text-white'
                    }`}
                  >
                    {monitoringActive ? '일시정지' : '시작'}
                  </button>
                </div>

                {/* Divider */}
                <div className="h-12 w-px bg-gray-700"></div>

                {/* Polling Engine Control */}
                <div className="flex items-center gap-4">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-100">폴링 엔진 일괄 제어</h2>
                    <p className="text-xs text-gray-400">모든 그룹 PLC 폴링 시작/중지</p>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button
                  onClick={handleStartAll}
                  disabled={actionLoading === 'all'}
                  className="bg-green-600 text-white px-5 py-2 rounded hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed flex items-center gap-2 text-sm"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {actionLoading === 'all' ? '처리 중...' : '전체 시작'}
                </button>
                <button
                  onClick={handleStopAll}
                  disabled={actionLoading === 'all'}
                  className="bg-red-600 text-white px-5 py-2 rounded hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed flex items-center gap-2 text-sm"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                  </svg>
                  {actionLoading === 'all' ? '처리 중...' : '전체 중지'}
                </button>
              </div>
            </div>
          </div>

          {/* Polling Groups */}
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h2 className="text-xl font-semibold text-gray-100 mb-1">폴링 그룹 개별 제어</h2>
                <p className="text-sm text-gray-400">각 폴링 그룹의 실시간 상태 및 개별 제어</p>
              </div>
            </div>

            {engineStatus.groups.length === 0 && (
              <div className="text-center text-gray-500 py-8">
                설정된 폴링 그룹이 없습니다
              </div>
            )}

            <div className="space-y-4">
              {engineStatus.groups.map((group) => (
                <div
                  key={group.group_name}
                  className={`border rounded-lg p-4 transition-all ${
                    monitoringActive
                      ? 'border-gray-800 bg-gray-950'
                      : 'border-gray-800/50 bg-gray-950/50 opacity-60'
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-semibold text-gray-100">{group.group_name}</h3>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getModeBadgeClass(group.mode)}`}>
                        {group.mode}
                      </span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStateBadgeClass(group.state)}`}>
                        {group.state === 'running' ? '실행 중' : group.state === 'stopped' ? '중지됨' : group.state}
                      </span>
                      {groupTagCounts[group.group_id] !== undefined && (
                        <span className="px-2 py-1 rounded text-xs font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                          태그 {groupTagCounts[group.group_id]}개
                        </span>
                      )}
                      {groupPlcStatus[group.group_id] === 'connection_failed' && (
                        <span className="px-2 py-1 rounded text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20 flex items-center gap-1">
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                          PLC 연결 실패
                        </span>
                      )}
                      {groupPlcStatus[group.group_id] === 'inactive' && (
                        <span className="px-2 py-1 rounded text-xs font-medium bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
                          PLC 비활성
                        </span>
                      )}
                    </div>
                    <div className="flex gap-2">
                      {group.state === 'stopped' && (
                        <button
                          onClick={() => handleStartGroup(group.group_name)}
                          disabled={actionLoading === group.group_name}
                          className="bg-green-600 text-white px-4 py-1 rounded text-sm hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed flex items-center gap-1"
                        >
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                          </svg>
                          시작
                        </button>
                      )}
                      {group.state === 'running' && (
                        <button
                          onClick={() => handleStopGroup(group.group_name)}
                          disabled={actionLoading === group.group_name}
                          className="bg-red-600 text-white px-4 py-1 rounded text-sm hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed flex items-center gap-1"
                        >
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                          중지
                        </button>
                      )}
                      {group.mode === 'HANDSHAKE' && group.state === 'running' && (
                        <button
                          onClick={() => handleTrigger(group.group_name)}
                          disabled={actionLoading === group.group_name}
                          className="bg-purple-600 text-white px-4 py-1 rounded text-sm hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed"
                        >
                          수동 트리거
                        </button>
                      )}
                    </div>
                  </div>

                  {monitoringActive && (
                    <>
                      <div className="grid grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-400">총 폴링:</span>
                          <span className="ml-2 font-medium text-gray-200">{group.total_polls}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">성공:</span>
                          <span className="ml-2 font-medium text-green-400">{group.success_count}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">실패:</span>
                          <span className="ml-2 font-medium text-red-400">{group.error_count}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">성공률:</span>
                          <span className="ml-2 font-medium text-gray-200">
                            {group.success_rate !== undefined ? `${group.success_rate}%` : 'N/A'}
                          </span>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 text-sm mt-2">
                        <div>
                          <span className="text-gray-400">평균 시간:</span>
                          <span className="ml-2 font-medium text-gray-200">{group.avg_poll_time_ms.toFixed(2)}ms</span>
                        </div>
                        {group.consecutive_failures > 0 && (
                          <div>
                            <span className="text-gray-400">연속 실패:</span>
                            <span className="ml-2 font-medium text-orange-400">{group.consecutive_failures}</span>
                          </div>
                        )}
                      </div>

                      {group.last_poll_time && (
                        <div className="mt-2 text-sm text-gray-400">
                          마지막 폴링: {new Date(group.last_poll_time).toLocaleString('ko-KR')}
                        </div>
                      )}

                      {group.last_error && (
                        <div className="mt-3 p-4 bg-red-500/10 border-l-4 border-red-500 rounded-r">
                          <div className="flex items-start gap-2">
                            <svg className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <div className="flex-1">
                              <div className="text-sm font-semibold text-red-400 mb-1.5">마지막 오류</div>
                              <div className="text-sm text-red-300 leading-relaxed font-mono bg-red-950/30 px-2 py-1.5 rounded">
                                {group.last_error}
                              </div>
                              {group.next_retry_in !== undefined && group.next_retry_in > 0 && (
                                <div className="flex items-center gap-2 mt-2 text-xs text-red-300/80">
                                  <svg className="w-3.5 h-3.5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                  </svg>
                                  <span className="font-medium">{group.next_retry_in.toFixed(1)}초 후 재시도</span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Last Updated */}
          {monitoringActive && (
            <div className="mt-4 text-sm text-gray-500 text-right">
              마지막 업데이트: {new Date(engineStatus.timestamp).toLocaleTimeString('ko-KR')}
            </div>
          )}
        </>
      )}
    </div>
  );
}
