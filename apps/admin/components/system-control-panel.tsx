'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Play,
  Square,
  RotateCw,
  Power,
  Clock,
  Loader2,
  AlertCircle,
  CheckCircle2
} from 'lucide-react';
import { getSystemStatus, startSystem, stopSystem, restartSystem, SystemStatus } from '@/lib/api/system';
import { toast } from 'sonner';

export function SystemControlPanel() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchStatus = async () => {
    try {
      const data = await getSystemStatus();
      setStatus(data);
    } catch (error) {
      console.error('Failed to fetch system status', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const handleStart = async () => {
    setActionLoading(true);
    try {
      const result = await startSystem();
      toast.success(result.message);
      fetchStatus();
    } catch (error) {
      toast.error('Failed to start system');
    } finally {
      setActionLoading(false);
    }
  };

  const handleStop = async () => {
    setActionLoading(true);
    try {
      const result = await stopSystem();
      toast.success(result.message);
      fetchStatus();
    } catch (error) {
      toast.error('Failed to stop system');
    } finally {
      setActionLoading(false);
    }
  };

  const handleRestart = async () => {
    setActionLoading(true);
    try {
      const result = await restartSystem();
      toast.success(result.message);
      fetchStatus();
    } catch (error) {
      toast.error('Failed to restart system');
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusBadge = () => {
    if (!status) return null;

    const statusConfig = {
      running: { color: 'bg-green-500/10 text-green-500 border-green-500/20', icon: CheckCircle2, text: 'Running' },
      stopped: { color: 'bg-gray-500/10 text-gray-400 border-gray-500/20', icon: Square, text: 'Stopped' },
      starting: { color: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20', icon: Loader2, text: 'Starting...' },
      stopping: { color: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20', icon: Loader2, text: 'Stopping...' },
      unavailable: { color: 'bg-red-500/10 text-red-500 border-red-500/20', icon: AlertCircle, text: 'Unavailable' },
      error: { color: 'bg-red-500/10 text-red-500 border-red-500/20', icon: AlertCircle, text: 'Error' },
    };

    const config = statusConfig[status.status] || statusConfig.unavailable;
    const Icon = config.icon;

    return (
      <Badge className={`${config.color} flex items-center gap-1 px-3 py-1`}>
        <Icon className={`h-3 w-3 ${status.status === 'starting' || status.status === 'stopping' ? 'animate-spin' : ''}`} />
        {config.text}
      </Badge>
    );
  };

  const formatUptime = (seconds?: number) => {
    if (!seconds) return '-';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours}h ${minutes}m ${secs}s`;
  };

  if (loading) {
    return (
      <Card className="bg-gray-900 border-gray-800">
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-blue-500" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-gray-900 border-gray-800">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-white">
            <Power className="h-5 w-5 text-blue-500" />
            System Control
          </CardTitle>
          {getStatusBadge()}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* System Info */}
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="flex flex-col gap-1">
            <span className="text-gray-400">Status</span>
            <span className="font-semibold text-white capitalize">{status?.status || 'Unknown'}</span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-gray-400">Groups Loaded</span>
            <span className="font-semibold text-white">{status?.polling_groups_loaded || 0}</span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-gray-400">Groups Running</span>
            <span className="font-semibold text-white">{status?.polling_groups_running || 0}</span>
          </div>
        </div>

        {status?.status === 'running' && status.uptime_seconds !== undefined && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
            <Clock className="h-4 w-4 text-blue-400" />
            <span className="text-sm text-blue-400">Uptime: {formatUptime(status.uptime_seconds)}</span>
          </div>
        )}

        {/* Control Buttons */}
        <div className="flex gap-2">
          <Button
            onClick={handleStart}
            disabled={actionLoading || status?.status === 'running'}
            className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-700"
          >
            {actionLoading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Play className="h-4 w-4 mr-2" />
            )}
            Start
          </Button>

          <Button
            onClick={handleStop}
            disabled={actionLoading || status?.status === 'stopped'}
            variant="destructive"
            className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-700"
          >
            {actionLoading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Square className="h-4 w-4 mr-2" />
            )}
            Stop
          </Button>

          <Button
            onClick={handleRestart}
            disabled={actionLoading || status?.status === 'stopped'}
            variant="outline"
            className="flex-1 bg-gray-800 border-gray-700 hover:bg-gray-700 disabled:bg-gray-800"
          >
            {actionLoading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <RotateCw className="h-4 w-4 mr-2" />
            )}
            Restart
          </Button>
        </div>

        {/* Warning Message */}
        {status?.status === 'stopped' && (
          <div className="flex items-start gap-2 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
            <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm text-yellow-500 font-medium">System is stopped</p>
              <p className="text-xs text-yellow-600 mt-1">
                Configure PLCs and polling groups, then click Start to begin data collection.
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
