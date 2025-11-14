'use client';

import { useRouter } from 'next/navigation';
import { createPLC } from '@/lib/api/plcs';
import { PLCFormData } from '@/lib/validators/plc';
import PLCForm from '@/components/forms/PLCForm';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { ArrowLeft, Server } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function NewPLCPage() {
  const router = useRouter();

  const handleSubmit = async (data: PLCFormData) => {
    try {
      await createPLC(data);
      toast.success('PLC가 생성되었습니다');
      router.push('/plcs');
    } catch (error) {
      toast.error('PLC 생성 실패');
    }
  };

  const handleCancel = () => {
    router.push('/plcs');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/plcs">
          <Button variant="outline" size="sm" className="bg-gray-800 border-gray-700 hover:bg-gray-700">
            <ArrowLeft className="h-4 w-4 mr-2" />
            뒤로
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <Server className="h-8 w-8" />
            새 PLC 추가
          </h1>
          <p className="text-gray-400 mt-1">새로운 PLC를 등록합니다</p>
        </div>
      </div>

      <Card className="bg-gray-900 border-gray-800 w-full">
        <CardHeader>
          <CardTitle className="text-white">PLC 정보</CardTitle>
        </CardHeader>
        <CardContent>
          <PLCForm onSubmit={handleSubmit} onCancel={handleCancel} />
        </CardContent>
      </Card>
    </div>
  );
}
