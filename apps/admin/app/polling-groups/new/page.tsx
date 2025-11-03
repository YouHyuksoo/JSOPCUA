'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { createPollingGroup } from '@/lib/api/polling-groups';
import { getTags } from '@/lib/api/tags';
import { PollingGroupFormData } from '@/lib/validators/polling-group';
import { Tag } from '@/lib/types/tag';
import PollingGroupForm from '@/components/forms/PollingGroupForm';
import Nav from '@/components/nav';
import { toast } from 'sonner';

export default function NewPollingGroupPage() {
  const router = useRouter();
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTags(1, 100).then((data) => {
      setTags(data.items);
      setLoading(false);
    });
  }, []);

  const handleSubmit = async (data: PollingGroupFormData) => {
    try {
      await createPollingGroup(data);
      toast.success('폴링 그룹이 생성되었습니다');
      router.push('/polling-groups');
    } catch (error) {
      toast.error('폴링 그룹 생성 실패');
    }
  };

  const handleCancel = () => {
    router.push('/polling-groups');
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <Nav />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">새 폴링 그룹 생성</h1>
        <div className="bg-white rounded-lg shadow p-6 max-w-2xl">
          <PollingGroupForm tags={tags} onSubmit={handleSubmit} onCancel={handleCancel} />
        </div>
      </div>
    </div>
  );
}
