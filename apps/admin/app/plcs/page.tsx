'use client';

import { useEffect, useState } from 'react';
import { getPLCs, deletePLC, testPLCConnection } from '@/lib/api/plcs';
import { PLC } from '@/lib/types/plc';
import Nav from '@/components/nav';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import DeleteDialog from '@/components/DeleteDialog';
import { toast } from 'sonner';

export default function PLCsPage() {
  const [plcs, setPLCs] = useState<PLC[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [testing, setTesting] = useState<number | null>(null);

  const fetchPLCs = async () => {
    try {
      const data = await getPLCs();
      setPLCs(data.items);
    } catch (error) {
      toast.error('PLC 조회 실패');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPLCs();
  }, []);

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await deletePLC(deleteId);
      toast.success('PLC가 삭제되었습니다');
      setDeleteId(null);
      fetchPLCs();
    } catch (error) {
      toast.error('PLC 삭제 실패');
    }
  };

  const handleTest = async (id: number) => {
    setTesting(id);
    try {
      const result = await testPLCConnection(id);
      if (result.success) {
        toast.success('연결 성공');
      } else {
        toast.error(`연결 실패: ${result.message}`);
      }
    } catch (error) {
      toast.error('연결 테스트 실패');
    } finally {
      setTesting(null);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <Nav />
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">PLC 관리</h1>
          <Link href="/plcs/new">
            <Button>새 PLC</Button>
          </Link>
        </div>
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">이름</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP 주소</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">포트</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">프로토콜</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">작업</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {plcs.map((plc) => (
                <tr key={plc.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{plc.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{plc.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{plc.ip_address}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{plc.port}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{plc.protocol}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => handleTest(plc.id)}
                      disabled={testing === plc.id}
                    >
                      {testing === plc.id ? '테스트 중...' : '연결 테스트'}
                    </Button>
                    <Link href={`/plcs/${plc.id}`}>
                      <Button size="sm" variant="outline">편집</Button>
                    </Link>
                    <Button size="sm" variant="destructive" onClick={() => setDeleteId(plc.id)}>
                      삭제
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <DeleteDialog
        open={deleteId !== null}
        onOpenChange={(open) => !open && setDeleteId(null)}
        onConfirm={handleDelete}
      />
    </div>
  );
}
