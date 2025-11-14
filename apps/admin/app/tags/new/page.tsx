'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { createTag } from '@/lib/api/tags';
import { getPLCs } from '@/lib/api/plcs';
import { TagFormData } from '@/lib/validators/tag';
import { PLC } from '@/lib/types/plc';
import TagForm from '@/components/forms/TagForm';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { Tag as TagIcon, Loader2, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

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
      // Convert form data to API request format
      await createTag({
        plc_id: data.plc_id,
        process_id: 0,
        tag_address: data.address,
        tag_name: data.name,
        tag_division: data.description || '',
        tag_category: data.category || '',
        data_type: data.data_type,
        enabled: data.enabled,
      });
      toast.success('태그가 생성되었습니다');
      router.push('/tags');
    } catch (error) {
      toast.error('태그 생성 실패');
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
            새 태그 추가
          </h1>
          <p className="text-gray-400 mt-1">새로운 PLC 태그를 등록합니다</p>
        </div>
      </div>

      <Card className="bg-gray-900 border-gray-800 max-w-3xl">
        <CardHeader>
          <CardTitle className="text-white">태그 정보</CardTitle>
        </CardHeader>
        <CardContent>
          <TagForm plcs={plcs} onSubmit={handleSubmit} onCancel={handleCancel} />
        </CardContent>
      </Card>
    </div>
  );
}
