'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { createPLC } from '@/lib/api/plcs';
import { getProcesses } from '@/lib/api/processes';
import { PLCFormData } from '@/lib/validators/plc';
import { Process } from '@/lib/types/process';
import PLCForm from '@/components/forms/PLCForm';
import Nav from '@/components/nav';
import { toast } from 'sonner';

export default function NewPLCPage() {
  const router = useRouter();
  const [processes, setProcesses] = useState<Process[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getProcesses(1, 100).then((data) => {
      setProcesses(data.items);
      setLoading(false);
    });
  }, []);

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

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <Nav />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">새 PLC 생성</h1>
        <div className="bg-white rounded-lg shadow p-6 max-w-2xl">
          <PLCForm processes={processes} onSubmit={handleSubmit} onCancel={handleCancel} />
        </div>
      </div>
    </div>
  );
}
