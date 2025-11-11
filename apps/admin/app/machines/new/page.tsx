'use client';

import { useRouter } from 'next/navigation';
import { createMachine } from '@/lib/api/machines';
import { MachineFormData } from '@/lib/validators/machine';
import MachineForm from '@/components/forms/MachineForm';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { ArrowLeft, Settings } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function NewMachinePage() {
  const router = useRouter();

  const handleSubmit = async (data: MachineFormData) => {
    try {
      await createMachine(data);
      toast.success('설비가 생성되었습니다');
      router.push('/machines');
    } catch (error) {
      toast.error('설비 생성 실패');
    }
  };

  const handleCancel = () => {
    router.push('/machines');
  };

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
            새 설비 추가
          </h1>
          <p className="text-gray-400 mt-1">새로운 생산 설비를 등록합니다</p>
        </div>
      </div>

      <Card className="bg-gray-900 border-gray-800 max-w-2xl">
        <CardHeader>
          <CardTitle className="text-white">설비 정보</CardTitle>
        </CardHeader>
        <CardContent>
          <MachineForm onSubmit={handleSubmit} onCancel={handleCancel} />
        </CardContent>
      </Card>
    </div>
  );
}
