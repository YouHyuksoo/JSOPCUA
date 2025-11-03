'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { createTag } from '@/lib/api/tags';
import { getPLCs } from '@/lib/api/plcs';
import { TagFormData } from '@/lib/validators/tag';
import { PLC } from '@/lib/types/plc';
import TagForm from '@/components/forms/TagForm';
import Nav from '@/components/nav';
import { toast } from 'sonner';

export default function NewTagPage() {
  const router = useRouter();
  const [plcs, setPLCs] = useState<PLC[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPLCs(1, 100).then((data) => {
      setPLCs(data.items);
      setLoading(false);
    });
  }, []);

  const handleSubmit = async (data: TagFormData) => {
    try {
      await createTag(data);
      toast.success('태그가 생성되었습니다');
      router.push('/tags');
    } catch (error) {
      toast.error('태그 생성 실패');
    }
  };

  const handleCancel = () => {
    router.push('/tags');
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <Nav />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">새 태그 생성</h1>
        <div className="bg-white rounded-lg shadow p-6 max-w-2xl">
          <TagForm plcs={plcs} onSubmit={handleSubmit} onCancel={handleCancel} />
        </div>
      </div>
    </div>
  );
}
