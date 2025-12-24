'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { createPollingGroup } from '@/lib/api/polling-groups';
import { getTags } from '@/lib/api/tags';
import { PollingGroupFormData } from '@/lib/validators/polling-group';
import { Tag } from '@/lib/types/tag';
import PollingGroupForm from '@/components/forms/PollingGroupForm';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { Layers, Loader2, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function NewPollingGroupPage() {
  const router = useRouter();
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // is_active=true인 태그만 가져오기 (limit=10000)
    getTags(1, 10000, undefined, undefined, true).then((data) => {
      setTags(data.items);
      setLoading(false);
    });
  }, []);

  const handleSubmit = async (data: PollingGroupFormData) => {
    try {
      // 선택된 태그들로부터 PLC 코드 추출
      const selectedTags = tags.filter(tag => data.tag_ids.includes(tag.id));
      const plcCodes = new Set(selectedTags.map(tag => tag.plc_code).filter(Boolean));

      if (plcCodes.size === 0) {
        toast.error('선택된 태그에 PLC 코드가 없습니다');
        return;
      }

      if (plcCodes.size > 1) {
        toast.error('선택된 태그들이 서로 다른 PLC에 속해 있습니다. 같은 PLC의 태그만 선택해주세요.');
        return;
      }

      const plc_code = Array.from(plcCodes)[0] as string;

      // Convert form data to API request format
      await createPollingGroup({
        name: data.name,
        plc_code: plc_code,
        polling_interval: data.polling_interval_ms,
        group_category: data.group_category,
        is_active: true,
        tag_ids: data.tag_ids,
      });
      toast.success('폴링 그룹이 생성되었습니다');
      router.push('/polling-groups');
    } catch (error) {
      toast.error('폴링 그룹 생성 실패');
    }
  };

  const handleCancel = () => {
    router.push('/polling-groups');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/polling-groups">
          <Button variant="outline" size="sm" className="bg-gray-800 border-gray-700 hover:bg-gray-700">
            <ArrowLeft className="h-4 w-4 mr-2" />
            뒤로
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <Layers className="h-8 w-8" />
            새 폴링 그룹 생성
          </h1>
          <p className="text-gray-400 mt-1">새로운 폴링 그룹을 등록합니다</p>
        </div>
      </div>

      <PollingGroupForm tags={tags} onSubmit={handleSubmit} onCancel={handleCancel} />
    </div>
  );
}
