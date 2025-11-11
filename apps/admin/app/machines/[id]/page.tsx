'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { getMachine, updateMachine } from '@/lib/api/machines';
import { MachineFormData } from '@/lib/validators/machine';
import { Machine } from '@/lib/types/machine';
import MachineForm from '@/components/forms/MachineForm';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { ArrowLeft, Settings, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function EditMachinePage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [machine, setMachine] = useState<Machine | null>(null);
  const [loading, setLoading] = useState(true);
  const id = parseInt(params.id);

  useEffect(() => {
    const fetchMachine = async () => {
      try {
        const data = await getMachine(id);
        setMachine(data);
      } catch (error) {
        toast.error('설비 정보 조회 실패');
      } finally {
        setLoading(false);
      }
    };

    fetchMachine();
  }, [id]);

  const handleSubmit = async (data: MachineFormData) => {
    try {
      await updateMachine(id, data);
      toast.success('설비가 수정되었습니다');
      router.push('/machines');
    } catch (error) {
      toast.error('설비 수정 실패');
    }
  };

  const handleCancel = () => {
    router.push('/machines');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (!machine) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <p className="text-gray-400 text-lg mb-4">설비를 찾을 수 없습니다</p>
        <Link href="/machines">
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
        <Link href="/machines">
          <Button variant="outline" size="sm" className="bg-gray-800 border-gray-700 hover:bg-gray-700">
            <ArrowLeft className="h-4 w-4 mr-2" />
            뒤로
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <Settings className="h-8 w-8" />
            설비 수정
          </h1>
          <p className="text-gray-400 mt-1">{machine.machine_name} ({machine.machine_code})</p>
        </div>
      </div>

      <Card className="bg-gray-900 border-gray-800 max-w-2xl">
        <CardHeader>
          <CardTitle className="text-white">설비 정보</CardTitle>
        </CardHeader>
        <CardContent>
          <MachineForm defaultValues={machine} onSubmit={handleSubmit} onCancel={handleCancel} />
        </CardContent>
      </Card>
    </div>
  );
}
