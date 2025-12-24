'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { getPollingGroup, getPollingGroupTags, updatePollingGroup } from '@/lib/api/polling-groups';
import { getTags } from '@/lib/api/tags';
import { PollingGroupFormData } from '@/lib/validators/polling-group';
import { PollingGroup } from '@/lib/types/polling-group';
import { Tag } from '@/lib/types/tag';
import PollingGroupForm from '@/components/forms/PollingGroupForm';
import { toast } from 'sonner';

export default function EditPollingGroupPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [pollingGroup, setPollingGroup] = useState<PollingGroup | null>(null);
  const [tags, setTags] = useState<Tag[]>([]);
  const [initialTagIds, setInitialTagIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const id = parseInt(params.id);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [groupData, allTagsData, groupTagsData] = await Promise.all([
          getPollingGroup(id),
          getTags(1, 10000, undefined, undefined, true), // is_active=true인 태그만
          getPollingGroupTags(id)
        ]);
        console.log('Polling Group Data:', groupData);
        setPollingGroup(groupData);
        setTags(allTagsData.items);
        setInitialTagIds(groupTagsData.map(tag => tag.id));
      } catch (error) {
        console.error('데이터 조회 실패:', error);
        toast.error(`데이터 조회 실패: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
        setPollingGroup(null);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  const handleSubmit = async (data: PollingGroupFormData) => {
    try {
      // Convert form data to API request format
      await updatePollingGroup(id, {
        name: data.name,
        plc_code: pollingGroup?.plc_code ?? '',
        workstage_code: pollingGroup?.workstage_code ?? undefined,
        polling_interval: data.polling_interval_ms,
        group_category: data.group_category,
        is_active: pollingGroup?.is_active ?? true,
        tag_ids: data.tag_ids,
      });
      toast.success('폴링 그룹이 수정되었습니다');
      router.push('/polling-groups');
    } catch (error) {
      toast.error('폴링 그룹 수정 실패');
    }
  };

  const handleCancel = () => {
    router.push('/polling-groups');
  };

  if (loading) return (
    <div className="flex items-center justify-center h-full">
      <div className="text-xl text-gray-300">Loading...</div>
    </div>
  );

  if (!pollingGroup) return (
    <div className="flex items-center justify-center h-full">
      <div className="text-xl text-gray-300">폴링 그룹을 찾을 수 없습니다</div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">폴링 그룹 수정</h1>
        <p className="text-gray-400">{pollingGroup.name}</p>
      </div>
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
        <PollingGroupForm
          defaultValues={pollingGroup}
          tags={tags}
          initialTagIds={initialTagIds}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
        />
      </div>
    </div>
  );
}
