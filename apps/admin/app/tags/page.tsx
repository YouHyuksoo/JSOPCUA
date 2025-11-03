'use client';

import { useEffect, useState } from 'react';
import { getTags, deleteTag } from '@/lib/api/tags';
import { Tag } from '@/lib/types/tag';
import Nav from '@/components/nav';
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

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <Nav />
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">태그 관리</h1>
          <div className="space-x-2">
            <Link href="/tags/upload">
              <Button variant="outline">CSV 업로드</Button>
            </Link>
            <Link href="/tags/new">
              <Button>새 태그</Button>
            </Link>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">이름</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">주소</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">데이터 타입</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">PLC ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">작업</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tags.map((tag) => (
                <tr key={tag.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{tag.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{tag.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{tag.address}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{tag.data_type}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{tag.plc_id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                    <Link href={`/tags/${tag.id}`}>
                      <Button size="sm" variant="outline">편집</Button>
                    </Link>
                    <Button size="sm" variant="destructive" onClick={() => setDeleteId(tag.id)}>
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
