'use client';

import { useEffect, useState } from 'react';
import { getPollingGroups, startPollingGroup, stopPollingGroup } from '@/lib/api/polling-groups';
import { PollingGroup } from '@/lib/types/polling-group';
import Nav from '@/components/nav';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

export default function PollingGroupsPage() {
  const [groups, setGroups] = useState<PollingGroup[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchGroups = async () => {
    try {
      const data = await getPollingGroups();
      setGroups(data.items);
    } catch (error) {
      toast.error('폴링 그룹 조회 실패');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGroups();
  }, []);

  const handleStart = async (id: number) => {
    try {
      await startPollingGroup(id);
      toast.success('폴링 시작됨');
      fetchGroups();
    } catch (error) {
      toast.error('폴링 시작 실패');
    }
  };

  const handleStop = async (id: number) => {
    try {
      await stopPollingGroup(id);
      toast.success('폴링 중지됨');
      fetchGroups();
    } catch (error) {
      toast.error('폴링 중지 실패');
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <Nav />
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">폴링 그룹</h1>
          <Link href="/polling-groups/new">
            <Button>새 폴링 그룹</Button>
          </Link>
        </div>
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">이름</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">주기(ms)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">상태</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">작업</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {groups.map((group) => (
                <tr key={group.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{group.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{group.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{group.polling_interval_ms}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded ${
                      group.status === 'running' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {group.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                    {group.status === 'running' ? (
                      <Button size="sm" variant="destructive" onClick={() => handleStop(group.id)}>중지</Button>
                    ) : (
                      <Button size="sm" onClick={() => handleStart(group.id)}>시작</Button>
                    )}
                    <Link href={`/polling-groups/${group.id}`}>
                      <Button size="sm" variant="outline">편집</Button>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
