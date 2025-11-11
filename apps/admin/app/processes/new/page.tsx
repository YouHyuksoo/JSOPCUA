'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { createProcess } from '@/lib/api/processes';
import { getMachines } from '@/lib/api/machines';
import { ProcessFormData } from '@/lib/validators/process';
import { Machine } from '@/lib/types/machine';
import ProcessForm from '@/components/forms/ProcessForm';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { ArrowLeft, Network, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function NewProcessPage() {
  const router = useRouter();
  const [machines, setMachines] = useState<Machine[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMachines = async () => {
      try {
        const data = await getMachines(1, 100);
        setMachines(data.items);
      } catch (error) {
        toast.error('설비 목록 조회 실패');
      } finally {
        setLoading(false);
      }
    };

    fetchMachines();
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
        <Link href="/processes">
          <Button variant="outline" size="sm" className="bg-gray-800 border-gray-700 hover:bg-gray-700">
            <ArrowLeft className="h-4 w-4 mr-2" />
            뒤로
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <Network className="h-8 w-8" />
            새 공정 추가
          </h1>
          <p className="text-gray-400 mt-1">새로운 공정을 등록합니다</p>
        </div>
      </div>

      <Card className="bg-gray-900 border-gray-800 max-w-2xl">
        <CardHeader>
          <CardTitle className="text-white">공정 정보</CardTitle>
        </CardHeader>
        <CardContent>
          <ProcessForm machines={machines} onSubmit={handleSubmit} onCancel={handleCancel} />
        </CardContent>
      </Card>
    </div>
  );
}
