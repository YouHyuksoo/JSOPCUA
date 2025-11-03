'use client';

import { useEffect, useState } from 'react';
import { getProcesses, deleteProcess } from '@/lib/api/processes';
import { Process } from '@/lib/types/process';
import Nav from '@/components/nav';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import DeleteDialog from '@/components/DeleteDialog';
import { toast } from 'sonner';

export default function ProcessesPage() {
  const [processes, setProcesses] = useState<Process[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteId, setDeleteId] = useState<number | null>(null);

  const fetchProcesses = async () => {
    try {
      const data = await getProcesses();
      setProcesses(data.items);
    } catch (error) {
      toast.error('공정 조회 실패');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProcesses();
  }, []);

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await deleteProcess(deleteId);
      toast.success('공정이 삭제되었습니다');
      setDeleteId(null);
      fetchProcesses();
    } catch (error) {
      toast.error('공정 삭제 실패');
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <Nav />
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">공정 관리</h1>
          <Link href="/processes/new">
            <Button>새 공정</Button>
          </Link>
        </div>
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">이름</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">코드</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">라인 ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">작업</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {processes.map((process) => (
                <tr key={process.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{process.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{process.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{process.code}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{process.line_id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                    <Link href={`/processes/${process.id}`}>
                      <Button size="sm" variant="outline">편집</Button>
                    </Link>
                    <Button size="sm" variant="destructive" onClick={() => setDeleteId(process.id)}>
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
