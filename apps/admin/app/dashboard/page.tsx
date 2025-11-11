'use client';

import { useEffect, useState } from 'react';
import { getDashboardData } from '@/lib/api/system-status';
import { DashboardData } from '@/lib/types/system-status';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { SystemControlPanel } from '@/components/system-control-panel';
import {
  Activity,
  Cpu,
  Database,
  HardDrive,
  PlayCircle,
  Server,
  TrendingUp,
  Loader2
} from 'lucide-react';

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await getDashboardData();
        setData(result);
      } catch (error) {
        console.error('Failed to fetch dashboard data', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="flex flex-col items-center gap-2">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
          <p className="text-sm text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-lg text-gray-400">No data available</p>
        </div>
      </div>
    );
  }

  const stats = data ? [
    {
      title: 'CPU Usage',
      value: `${data.cpu_usage.toFixed(1)}%`,
      icon: Cpu,
      color: data.cpu_usage > 80 ? 'text-red-500' : 'text-blue-500',
      bgColor: data.cpu_usage > 80 ? 'bg-red-500/10' : 'bg-blue-500/10',
    },
    {
      title: 'Memory Usage',
      value: `${data.memory_usage.toFixed(1)}%`,
      icon: Database,
      color: data.memory_usage > 80 ? 'text-red-500' : 'text-green-500',
      bgColor: data.memory_usage > 80 ? 'bg-red-500/10' : 'bg-green-500/10',
    },
    {
      title: 'Disk Usage',
      value: `${data.disk_usage.toFixed(1)}%`,
      icon: HardDrive,
      color: data.disk_usage > 80 ? 'text-red-500' : 'text-purple-500',
      bgColor: data.disk_usage > 80 ? 'bg-red-500/10' : 'bg-purple-500/10',
    },
    {
      title: 'PLC Connections',
      value: `${data.plc_status.connected} / ${data.plc_status.total}`,
      icon: Server,
      color: data.plc_status.connected === data.plc_status.total ? 'text-green-500' : 'text-yellow-500',
      bgColor: data.plc_status.connected === data.plc_status.total ? 'bg-green-500/10' : 'bg-yellow-500/10',
      subtitle: `${data.plc_status.connected} connected`,
    },
    {
      title: 'Polling Groups',
      value: `${data.polling_groups.running} / ${data.polling_groups.total}`,
      icon: PlayCircle,
      color: 'text-cyan-500',
      bgColor: 'bg-cyan-500/10',
      subtitle: `${data.polling_groups.running} running`,
    },
    {
      title: 'Buffer Status',
      value: `${data.buffer_status.utilization_percent.toFixed(1)}%`,
      icon: TrendingUp,
      color: data.buffer_status.utilization_percent > 80 ? 'text-red-500' : 'text-indigo-500',
      bgColor: data.buffer_status.utilization_percent > 80 ? 'bg-red-500/10' : 'bg-indigo-500/10',
      subtitle: `${data.buffer_status.current_size} / ${data.buffer_status.max_size} items`,
    },
  ] : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">System Dashboard</h1>
        <p className="text-gray-400">Real-time monitoring of SCADA system performance</p>
      </div>

      {/* System Control Panel */}
      <SystemControlPanel />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index} className="bg-gray-900 border-gray-800 hover:border-gray-700 transition-colors">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-gray-400">
                  {stat.title}
                </CardTitle>
                <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`h-5 w-5 ${stat.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className={`text-3xl font-bold ${stat.color}`}>
                  {stat.value}
                </div>
                {stat.subtitle && (
                  <p className="text-xs text-gray-500 mt-2">{stat.subtitle}</p>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Additional Info Card */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <Activity className="h-5 w-5 text-green-500" />
            System Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="flex items-center justify-between p-3 rounded-lg bg-gray-800">
              <span className="text-gray-400">Total PLCs</span>
              <span className="font-semibold text-white">{data.plc_status.total}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-gray-800">
              <span className="text-gray-400">Active Groups</span>
              <span className="font-semibold text-white">{data.polling_groups.running}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-gray-800">
              <span className="text-gray-400">Buffer Size</span>
              <span className="font-semibold text-white">{data.buffer_status.current_size}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
