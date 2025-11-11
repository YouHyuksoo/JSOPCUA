'use client';

import { useEffect, useState } from 'react';
import { getPollingGroups, startPollingGroup, stopPollingGroup } from '@/lib/api/polling-groups';
import { PollingGroup } from '@/lib/types/polling-group';
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

  if (loading) return (
    <div className="flex items-center justify-center h-full">
      <div className="text-xl text-gray-300">Loading...</div>
    </div>
  );

  return (
    <div>
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-100">폴링 그룹</h1>
          <Link href="/polling-groups/new">
            <Button className="bg-blue-600 hover:bg-blue-700">새 폴링 그룹</Button>
          </Link>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-800">
            <thead className="bg-gray-800">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">이름</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">주기(ms)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">상태</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">작업</th>
              </tr>
            </thead>
            <tbody className="bg-gray-900 divide-y divide-gray-800">
              {groups.map((group) => (
                <tr key={group.id} className="hover:bg-gray-800/50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{group.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-100">{group.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{group.polling_interval_ms}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded border ${
                      group.status === 'running'
                        ? 'bg-green-500/10 text-green-400 border-green-500/20'
                        : 'bg-gray-500/10 text-gray-400 border-gray-500/20'
                    }`}>
                      {group.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                    {group.status === 'running' ? (
                      <Button size="sm" variant="destructive" className="bg-red-500/10 text-red-500 hover:bg-red-500/20" onClick={() => handleStop(group.id)}>중지</Button>
                    ) : (
                      <Button size="sm" className="bg-green-600 hover:bg-green-700" onClick={() => handleStart(group.id)}>시작</Button>
                    )}
                    <Link href={`/polling-groups/${group.id}`}>
                      <Button size="sm" variant="outline" className="bg-gray-800 border-gray-700 hover:bg-gray-700">편집</Button>
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
