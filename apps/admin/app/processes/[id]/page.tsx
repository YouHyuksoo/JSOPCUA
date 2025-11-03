'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { updateProcess } from '@/lib/api/processes';
import { getLines } from '@/lib/api/lines';
import { ProcessFormData } from '@/lib/validators/process';
import { Process } from '@/lib/types/process';
import { Line } from '@/lib/types/line';
import ProcessForm from '@/components/forms/ProcessForm';
import Nav from '@/components/nav';
import { toast } from 'sonner';
import apiClient from '@/lib/api/client';

export default function EditProcessPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [process, setProcess] = useState<Process | null>(null);
  const [lines, setLines] = useState<Line[]>([]);
  const [loading, setLoading] = useState(true);
  const id = parseInt(params.id);

  useEffect(() => {
    Promise.all([
      apiClient.get<Process>(`/processes/${id}`),
      getLines(1, 100)
    ]).then(([processRes, linesData]) => {
      setProcess(processRes.data);
      setLines(linesData.items);
      setLoading(false);
    });
  }, [id]);

  const handleSubmit = async (data: ProcessFormData) => {
    try {
      await updateProcess(id, data);
      toast.success('공정이 수정되었습니다');
      router.push('/processes');
    } catch (error) {
      toast.error('공정 수정 실패');
    }
  };

  const handleCancel = () => {
    router.push('/processes');
  };

  if (loading) return <div>Loading...</div>;
  if (!process) return <div>Not found</div>;

  return (
    <div>
      <Nav />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">공정 수정</h1>
        <div className="bg-white rounded-lg shadow p-6 max-w-2xl">
          <ProcessForm defaultValues={process} lines={lines} onSubmit={handleSubmit} onCancel={handleCancel} />
        </div>
      </div>
    </div>
  );
}
