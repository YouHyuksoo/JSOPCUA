'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { getTag, updateTag } from '@/lib/api/tags';
import { getPLCs } from '@/lib/api/plcs';
import { TagFormData } from '@/lib/validators/tag';
import { Tag } from '@/lib/types/tag';
import { PLC } from '@/lib/types/plc';
import TagForm from '@/components/forms/TagForm';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { ArrowLeft, Tag as TagIcon, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function EditTagPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [tag, setTag] = useState<Tag | null>(null);
  const [plcs, setPLCs] = useState<PLC[]>([]);
  const [loading, setLoading] = useState(true);
  const id = parseInt(params.id);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [tagData, plcsData] = await Promise.all([
          getTag(id),
          getPLCs(1, 100)
        ]);
        setTag(tagData);
        setPLCs(plcsData.items);
      } catch (error) {
        toast.error('데이터 조회 실패');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  const handleSubmit = async (data: TagFormData) => {
    try {
      // Convert form data to API request format
      await updateTag(id, {
        plc_id: data.plc_id,
        process_id: tag?.process_id ?? 0,
        tag_address: data.address,
        tag_name: data.name,
        tag_division: data.description || '',
        data_type: data.data_type,
        enabled: tag?.enabled ?? true,
      });
      toast.success('태그가 수정되었습니다');
      router.push('/tags');
    } catch (error) {
      toast.error('태그 수정 실패');
    }
  };

  const handleCancel = () => {
    router.push('/tags');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (!tag) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <p className="text-gray-400 text-lg mb-4">태그를 찾을 수 없습니다</p>
        <Link href="/tags">
          <Button variant="outline" className="bg-gray-800 border-gray-700 hover:bg-gray-700">
            <ArrowLeft className="h-4 w-4 mr-2" />
            목록으로 돌아가기
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/tags">
          <Button variant="outline" size="sm" className="bg-gray-800 border-gray-700 hover:bg-gray-700">
            <ArrowLeft className="h-4 w-4 mr-2" />
            뒤로
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <TagIcon className="h-8 w-8" />
            태그 수정
          </h1>
          <p className="text-gray-400 mt-1">{tag.tag_name} ({tag.tag_address})</p>
        </div>
      </div>

      <Card className="bg-gray-900 border-gray-800 max-w-2xl">
        <CardHeader>
          <CardTitle className="text-white">태그 정보</CardTitle>
        </CardHeader>
        <CardContent>
          <TagForm defaultValues={tag} plcs={plcs} onSubmit={handleSubmit} onCancel={handleCancel} />
        </CardContent>
      </Card>
    </div>
  );
}
