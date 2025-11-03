'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { updatePollingGroup } from '@/lib/api/polling-groups';
import { getTags } from '@/lib/api/tags';
import { PollingGroupFormData } from '@/lib/validators/polling-group';
import { PollingGroup } from '@/lib/types/polling-group';
import { Tag } from '@/lib/types/tag';
import PollingGroupForm from '@/components/forms/PollingGroupForm';
import Nav from '@/components/nav';
import { toast } from 'sonner';
import apiClient from '@/lib/api/client';

export default function EditPollingGroupPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [pollingGroup, setPollingGroup] = useState<PollingGroup | null>(null);
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const id = parseInt(params.id);

  useEffect(() => {
    Promise.all([
      apiClient.get<PollingGroup>(`/polling/groups/${id}`),
      getTags(1, 100)
    ]).then(([groupRes, tagsData]) => {
      setPollingGroup(groupRes.data);
      setTags(tagsData.items);
      setLoading(false);
    });
  }, [id]);

  const handleSubmit = async (data: PollingGroupFormData) => {
    try {
      await updatePollingGroup(id, data);
      toast.success('폴링 그룹이 수정되었습니다');
      router.push('/polling-groups');
    } catch (error) {
      toast.error('폴링 그룹 수정 실패');
    }
  };

  const handleCancel = () => {
    router.push('/polling-groups');
  };

  if (loading) return <div>Loading...</div>;
  if (!pollingGroup) return <div>Not found</div>;

  return (
    <div>
      <Nav />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">폴링 그룹 수정</h1>
        <div className="bg-white rounded-lg shadow p-6 max-w-2xl">
          <PollingGroupForm defaultValues={pollingGroup} tags={tags} onSubmit={handleSubmit} onCancel={handleCancel} />
        </div>
      </div>
    </div>
  );
}
