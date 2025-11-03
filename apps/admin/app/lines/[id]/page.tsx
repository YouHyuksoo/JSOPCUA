'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { updateLine } from '@/lib/api/lines';
import { LineFormData } from '@/lib/validators/line';
import { Line } from '@/lib/types/line';
import LineForm from '@/components/forms/LineForm';
import Nav from '@/components/nav';
import { toast } from 'sonner';
import apiClient from '@/lib/api/client';

export default function EditLinePage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [line, setLine] = useState<Line | null>(null);
  const [loading, setLoading] = useState(true);
  const id = parseInt(params.id);

  useEffect(() => {
    apiClient.get<Line>(`/lines/${id}`).then((res) => {
      setLine(res.data);
      setLoading(false);
    });
  }, [id]);

  const handleSubmit = async (data: LineFormData) => {
    try {
      await updateLine(id, data);
      toast.success('라인이 수정되었습니다');
      router.push('/lines');
    } catch (error) {
      toast.error('라인 수정 실패');
    }
  };

  const handleCancel = () => {
    router.push('/lines');
  };

  if (loading) return <div>Loading...</div>;
  if (!line) return <div>Not found</div>;

  return (
    <div>
      <Nav />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">라인 수정</h1>
        <div className="bg-white rounded-lg shadow p-6 max-w-2xl">
          <LineForm defaultValues={line} onSubmit={handleSubmit} onCancel={handleCancel} />
        </div>
      </div>
    </div>
  );
}
