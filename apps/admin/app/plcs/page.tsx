'use client';

import { useEffect, useState } from 'react';
import { getPLCs, deletePLC, testPLCConnection } from '@/lib/api/plcs';
import { PLC } from '@/lib/types/plc';
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

  if (loading) return (
    <div className="flex items-center justify-center h-full">
      <div className="text-xl text-gray-300">Loading...</div>
    </div>
  );

  return (
    <div>
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-100">PLC 관리</h1>
          <Link href="/plcs/new">
            <Button className="bg-blue-600 hover:bg-blue-700">새 PLC</Button>
          </Link>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-800">
            <thead className="bg-gray-800">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">이름</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">IP 주소</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">포트</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">프로토콜</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">작업</th>
              </tr>
            </thead>
            <tbody className="bg-gray-900 divide-y divide-gray-800">
              {plcs.map((plc) => (
                <tr key={plc.id} className="hover:bg-gray-800/50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{plc.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-100">{plc.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{plc.ip_address}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{plc.port}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{plc.protocol}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                    <Button
                      size="sm"
                      variant="secondary"
                      className="bg-purple-600 hover:bg-purple-700"
                      onClick={() => handleTest(plc.id)}
                      disabled={testing === plc.id}
                    >
                      {testing === plc.id ? '테스트 중...' : '연결 테스트'}
                    </Button>
                    <Link href={`/plcs/${plc.id}`}>
                      <Button size="sm" variant="outline" className="bg-gray-800 border-gray-700 hover:bg-gray-700">편집</Button>
                    </Link>
                    <Button size="sm" variant="destructive" className="bg-red-500/10 text-red-500 hover:bg-red-500/20" onClick={() => setDeleteId(plc.id)}>
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
