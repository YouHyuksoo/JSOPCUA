'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { getProcess, updateProcess } from '@/lib/api/processes';
import { getMachines } from '@/lib/api/machines';
import { ProcessFormData } from '@/lib/validators/process';
import { Process } from '@/lib/types/process';
import { Machine } from '@/lib/types/machine';
import ProcessForm from '@/components/forms/ProcessForm';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { ArrowLeft, Network, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function EditProcessPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [process, setProcess] = useState<Process | null>(null);
  const [machines, setMachines] = useState<Machine[]>([]);
  const [loading, setLoading] = useState(true);
  const id = parseInt(params.id);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [processData, machinesData] = await Promise.all([
          getProcess(id),
          getMachines(1, 100)
        ]);
        setProcess(processData);
        setMachines(machinesData.items);
      } catch (error) {
        toast.error('데이터 조회 실패');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  const handleSubmit = async (data: ProcessFormData) => {
    try {
      await updateProcess(id, data);
      toast.success('공정이 수정되었습니다');
      router.push('/processes');
    } catch (error) {
      toast.error('공정 수정 실패');
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

  if (!process) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <p className="text-gray-400 text-lg mb-4">공정을 찾을 수 없습니다</p>
        <Link href="/processes">
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
        <Link href="/processes">
          <Button variant="outline" size="sm" className="bg-gray-800 border-gray-700 hover:bg-gray-700">
            <ArrowLeft className="h-4 w-4 mr-2" />
            뒤로
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <Network className="h-8 w-8" />
            공정 수정
          </h1>
          <p className="text-gray-400 mt-1">{process.process_name} ({process.process_code})</p>
        </div>
      </div>

      <Card className="bg-gray-900 border-gray-800 max-w-2xl">
        <CardHeader>
          <CardTitle className="text-white">공정 정보</CardTitle>
        </CardHeader>
        <CardContent>
          <ProcessForm defaultValues={process} machines={machines} onSubmit={handleSubmit} onCancel={handleCancel} />
        </CardContent>
      </Card>
    </div>
  );
}
