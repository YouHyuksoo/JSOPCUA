'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { updateTag } from '@/lib/api/tags';
import { getPLCs } from '@/lib/api/plcs';
import { TagFormData } from '@/lib/validators/tag';
import { Tag } from '@/lib/types/tag';
import { PLC } from '@/lib/types/plc';
import TagForm from '@/components/forms/TagForm';
import Nav from '@/components/nav';
import { toast } from 'sonner';
import apiClient from '@/lib/api/client';

export default function EditTagPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [tag, setTag] = useState<Tag | null>(null);
  const [plcs, setPLCs] = useState<PLC[]>([]);
  const [loading, setLoading] = useState(true);
  const id = parseInt(params.id);

  useEffect(() => {
    Promise.all([
      apiClient.get<Tag>(`/tags/${id}`),
      getPLCs(1, 100)
    ]).then(([tagRes, plcsData]) => {
      setTag(tagRes.data);
      setPLCs(plcsData.items);
      setLoading(false);
    });
  }, [id]);

  const handleSubmit = async (data: TagFormData) => {
    try {
      await updateTag(id, data);
      toast.success('태그가 수정되었습니다');
      router.push('/tags');
    } catch (error) {
      toast.error('태그 수정 실패');
    }
  };

  const handleCancel = () => {
    router.push('/tags');
  };

  if (loading) return <div>Loading...</div>;
  if (!tag) return <div>Not found</div>;

  return (
    <div>
      <Nav />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">태그 수정</h1>
        <div className="bg-white rounded-lg shadow p-6 max-w-2xl">
          <TagForm defaultValues={tag} plcs={plcs} onSubmit={handleSubmit} onCancel={handleCancel} />
        </div>
      </div>
    </div>
  );
}
