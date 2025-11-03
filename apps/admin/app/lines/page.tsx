'use client';

import { useEffect, useState } from 'react';
import { getLines, deleteLine } from '@/lib/api/lines';
import { Line } from '@/lib/types/line';
import Nav from '@/components/nav';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import DeleteDialog from '@/components/DeleteDialog';
import { toast } from 'sonner';

export default function LinesPage() {
  const [lines, setLines] = useState<Line[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteId, setDeleteId] = useState<number | null>(null);

  const fetchLines = async () => {
    try {
      const data = await getLines();
      setLines(data.items);
    } catch (error) {
      toast.error('라인 조회 실패');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLines();
  }, []);

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await deleteLine(deleteId);
      toast.success('라인이 삭제되었습니다');
      setDeleteId(null);
      fetchLines();
    } catch (error) {
      toast.error('라인 삭제 실패');
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <Nav />
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">라인 관리</h1>
          <Link href="/lines/new">
            <Button>새 라인</Button>
          </Link>
        </div>
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">이름</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">코드</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">생성일</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">작업</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {lines.map((line) => (
                <tr key={line.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{line.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{line.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{line.code}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(line.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                    <Link href={`/lines/${line.id}`}>
                      <Button size="sm" variant="outline">편집</Button>
                    </Link>
                    <Button size="sm" variant="destructive" onClick={() => setDeleteId(line.id)}>
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
