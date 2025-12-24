'use client';

import { useRouter } from 'next/navigation';
import { createLine } from '@/lib/api/lines';
import { LineFormData } from '@/lib/validators/line';
import LineForm from '@/components/forms/LineForm';
import Nav from '@/components/nav';
import { toast } from 'sonner';

export default function NewLinePage() {
  const router = useRouter();

  const handleSubmit = async (data: LineFormData) => {
    try {
      await createLine(data);
      toast.success('라인이 생성되었습니다');
      router.push('/lines');
    } catch (error) {
      toast.error('라인 생성 실패');
    }
  };

  const handleCancel = () => {
    router.push('/lines');
  };

  return (
    <div>
      <Nav />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">새 라인 생성</h1>
        <div className="bg-white rounded-lg shadow p-6 max-w-2xl">
          <LineForm onSubmit={handleSubmit} onCancel={handleCancel} />
        </div>
      </div>
    </div>
  );
}
