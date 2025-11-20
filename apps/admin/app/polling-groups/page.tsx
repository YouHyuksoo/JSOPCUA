'use client';

import { useEffect, useState } from 'react';
import { getPollingGroups, deletePollingGroup } from '@/lib/api/polling-groups';
import { PollingGroup } from '@/lib/types/polling-group';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import DeleteDialog from '@/components/DeleteDialog';
import { toast } from 'sonner';

export default function PollingGroupsPage() {
  const [groups, setGroups] = useState<PollingGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteId, setDeleteId] = useState<number | null>(null);

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

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await deletePollingGroup(deleteId);
      toast.success('폴링 그룹이 삭제되었습니다');
      setDeleteId(null);
      fetchGroups();
    } catch (error) {
      toast.error('폴링 그룹 삭제 실패');
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">태그 수</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">작업</th>
              </tr>
            </thead>
            <tbody className="bg-gray-900 divide-y divide-gray-800">
              {groups.map((group) => (
                <tr key={group.id} className="hover:bg-gray-800/50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{group.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-100">{group.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{group.polling_interval} ms</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    <span className="inline-flex items-center gap-1">
                      <span className="text-blue-400 font-medium">{group.tag_count}</span>
                      <span className="text-gray-500">개</span>
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                    <Link href={`/polling-groups/${group.id}`}>
                      <Button size="sm" variant="outline" className="bg-gray-800 border-gray-700 hover:bg-gray-700">편집</Button>
                    </Link>
                    <Button size="sm" variant="destructive" className="bg-red-500/10 text-red-500 hover:bg-red-500/20" onClick={() => setDeleteId(group.id)}>
                      삭제
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <DeleteDialog
        open={deleteId !== null}
        onOpenChange={(open) => !open && setDeleteId(null)}
        onConfirm={handleDelete}
      />
    </div>
  );
}
