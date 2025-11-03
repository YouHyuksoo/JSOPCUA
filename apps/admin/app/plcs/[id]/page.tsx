'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { updatePLC } from '@/lib/api/plcs';
import { getProcesses } from '@/lib/api/processes';
import { PLCFormData } from '@/lib/validators/plc';
import { PLC } from '@/lib/types/plc';
import { Process } from '@/lib/types/process';
import PLCForm from '@/components/forms/PLCForm';
import Nav from '@/components/nav';
import { toast } from 'sonner';
import apiClient from '@/lib/api/client';

export default function EditPLCPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [plc, setPLC] = useState<PLC | null>(null);
  const [processes, setProcesses] = useState<Process[]>([]);
  const [loading, setLoading] = useState(true);
  const id = parseInt(params.id);

  useEffect(() => {
    Promise.all([
      apiClient.get<PLC>(`/plc_connections/${id}`),
      getProcesses(1, 100)
    ]).then(([plcRes, processesData]) => {
      setPLC(plcRes.data);
      setProcesses(processesData.items);
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

  if (loading) return <div>Loading...</div>;
  if (!plc) return <div>Not found</div>;

  return (
    <div>
      <Nav />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">PLC 수정</h1>
        <div className="bg-white rounded-lg shadow p-6 max-w-2xl">
          <PLCForm defaultValues={plc} processes={processes} onSubmit={handleSubmit} onCancel={handleCancel} />
        </div>
      </div>
    </div>
  );
}
