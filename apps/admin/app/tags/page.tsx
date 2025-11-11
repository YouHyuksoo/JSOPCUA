'use client';

import { useEffect, useState } from 'react';
import { getTags, deleteTag } from '@/lib/api/tags';
import { Tag } from '@/lib/types/tag';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import DeleteDialog from '@/components/DeleteDialog';
import { toast } from 'sonner';

export default function TagsPage() {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteId, setDeleteId] = useState<number | null>(null);

  const fetchTags = async () => {
    try {
      const data = await getTags();
      setTags(data.items);
    } catch (error) {
      toast.error('태그 조회 실패');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTags();
  }, []);

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await deleteTag(deleteId);
      toast.success('태그가 삭제되었습니다');
      setDeleteId(null);
      fetchTags();
    } catch (error) {
      toast.error('태그 삭제 실패');
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
          <h1 className="text-3xl font-bold text-gray-100">태그 관리</h1>
          <div className="space-x-2">
            <Link href="/tags/upload">
              <Button variant="outline" className="bg-gray-800 border-gray-700 hover:bg-gray-700">CSV 업로드</Button>
            </Link>
            <Link href="/tags/new">
              <Button className="bg-blue-600 hover:bg-blue-700">새 태그</Button>
            </Link>
          </div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-800">
            <thead className="bg-gray-800">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">이름</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">주소</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">데이터 타입</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">PLC ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">작업</th>
              </tr>
            </thead>
            <tbody className="bg-gray-900 divide-y divide-gray-800">
              {tags.map((tag) => (
                <tr key={tag.id} className="hover:bg-gray-800/50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{tag.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-100">{tag.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{tag.address}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{tag.data_type}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{tag.plc_id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                    <Link href={`/tags/${tag.id}`}>
                      <Button size="sm" variant="outline" className="bg-gray-800 border-gray-700 hover:bg-gray-700">편집</Button>
                    </Link>
                    <Button size="sm" variant="destructive" className="bg-red-500/10 text-red-500 hover:bg-red-500/20" onClick={() => setDeleteId(tag.id)}>
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
