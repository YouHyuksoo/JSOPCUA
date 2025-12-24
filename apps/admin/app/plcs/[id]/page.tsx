'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { updatePLC } from '@/lib/api/plcs';
import { PLCFormData } from '@/lib/validators/plc';
import { PLC } from '@/lib/types/plc';
import PLCForm from '@/components/forms/PLCForm';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { ArrowLeft, Server, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import apiClient from '@/lib/api/client';

export default function EditPLCPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [plc, setPLC] = useState<PLC | null>(null);
  const [loading, setLoading] = useState(true);
  const id = parseInt(params.id);

  useEffect(() => {
    apiClient.get<PLC>(`/plc-connections/${id}`)
      .then((plcRes) => {
        setPLC(plcRes.data);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, [id]);

  const handleSubmit = async (data: PLCFormData) => {
    try {
      await updatePLC(id, data);
      toast.success('PLC가 수정되었습니다');
      router.push('/plcs');
    } catch (error) {
      toast.error('PLC 수정 실패');
    }
  };

  const handleCancel = () => {
    router.push('/plcs');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (!plc) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <p className="text-gray-400 text-lg mb-4">PLC를 찾을 수 없습니다</p>
        <Link href="/plcs">
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
        <Link href="/plcs">
          <Button variant="outline" size="sm" className="bg-gray-800 border-gray-700 hover:bg-gray-700">
            <ArrowLeft className="h-4 w-4 mr-2" />
            뒤로
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <Server className="h-8 w-8" />
            PLC 수정
          </h1>
          <p className="text-gray-400 mt-1">{plc.plc_name} ({plc.plc_code})</p>
        </div>
      </div>

      <Card className="bg-gray-900 border-gray-800 max-w-5xl mx-auto">
        <CardHeader>
          <CardTitle className="text-white">PLC 정보</CardTitle>
        </CardHeader>
        <CardContent>
          <PLCForm defaultValues={plc} onSubmit={handleSubmit} onCancel={handleCancel} />
        </CardContent>
      </Card>
    </div>
  );
}
