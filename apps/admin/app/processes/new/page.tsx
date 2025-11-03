'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { createProcess } from '@/lib/api/processes';
import { getLines } from '@/lib/api/lines';
import { ProcessFormData } from '@/lib/validators/process';
import { Line } from '@/lib/types/line';
import ProcessForm from '@/components/forms/ProcessForm';
import Nav from '@/components/nav';
import { toast } from 'sonner';

export default function NewProcessPage() {
  const router = useRouter();
  const [lines, setLines] = useState<Line[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getLines(1, 100).then((data) => {
      setLines(data.items);
      setLoading(false);
    });
  }, []);

  const handleSubmit = async (data: ProcessFormData) => {
    try {
      await createProcess(data);
      toast.success('공정이 생성되었습니다');
      router.push('/processes');
    } catch (error) {
      toast.error('공정 생성 실패');
    }
  };

  const handleCancel = () => {
    router.push('/processes');
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <Nav />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">새 공정 생성</h1>
        <div className="bg-white rounded-lg shadow p-6 max-w-2xl">
          <ProcessForm lines={lines} onSubmit={handleSubmit} onCancel={handleCancel} />
        </div>
      </div>
    </div>
  );
}
