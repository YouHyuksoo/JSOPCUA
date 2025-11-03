'use client';

import { useEffect, useState } from 'react';
import { getDashboardData } from '@/lib/api/system-status';
import { DashboardData } from '@/lib/types/system-status';
import Nav from '@/components/nav';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

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

  if (loading) return <div>Loading...</div>;
  if (!data) return <div>No data</div>;

  return (
    <div>
      <Nav />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">시스템 대시보드</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>CPU 사용량</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{data.cpu_usage.toFixed(1)}%</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>메모리 사용량</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{data.memory_usage.toFixed(1)}%</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>디스크 사용량</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{data.disk_usage.toFixed(1)}%</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>PLC 연결 상태</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-lg">
                <span className="text-green-600 font-bold">{data.plc_status.connected}</span> / {data.plc_status.total}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>폴링 그룹</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-lg">
                실행 중: <span className="font-bold">{data.polling_groups.running}</span> / {data.polling_groups.total}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>버퍼 상태</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-lg">
                크기: <span className="font-bold">{data.buffer_status.current_size}</span> / {data.buffer_status.max_size}
              </div>
              <div className="text-sm text-gray-500 mt-2">
                사용률: {data.buffer_status.utilization_percent.toFixed(1)}%
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
