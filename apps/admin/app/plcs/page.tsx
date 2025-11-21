'use client';

import { useEffect, useState } from 'react';
import { getPLCs, deletePLC, testPLCConnection, syncPLCsFromOracle, getOracleConnectionInfo } from '@/lib/api/plcs';
import { PLC } from '@/lib/types/plc';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import DeleteDialog from '@/components/DeleteDialog';
import OracleSyncDialog from '@/components/OracleSyncDialog';
import { toast } from 'sonner';
import { RefreshCw, Plus } from 'lucide-react';

export default function PLCsPage() {
  const [plcs, setPLCs] = useState<PLC[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [testing, setTesting] = useState<number | null>(null);
  const [showOracleSync, setShowOracleSync] = useState(false);

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
      if (result.status === 'success') {
        const testInfo = [
          `응답시간: ${result.response_time_ms}ms`,
          result.test_value_d100 !== null && result.test_value_d100 !== undefined ? `D100: ${result.test_value_d100}` : null,
          result.test_value_w100 !== null && result.test_value_w100 !== undefined ? `W100+W101: ${result.test_value_w100}` : null,
          result.test_value_m100 !== null && result.test_value_m100 !== undefined ? `M100: ${result.test_value_m100}` : null,
        ].filter(Boolean).join(' | ');

        toast.success(`연결 성공\n${testInfo}`);
      } else {
        toast.error(`연결 실패: ${result.error || '알 수 없는 오류'}`);
      }
    } catch (error: any) {
      toast.error(`연결 테스트 실패: ${error.message}`);
    } finally {
      setTesting(null);
    }
  };

  const handleSyncFromOracle = async () => {
    try {
      const result = await syncPLCsFromOracle();

      if (result.success) {
        const message = `Oracle 동기화 완료\n생성: ${result.created}개, 업데이트: ${result.updated}개`;
        toast.success(message);
        fetchPLCs(); // Reload PLCs
      } else {
        toast.error('Oracle 동기화 실패');
      }

      setShowOracleSync(false);
    } catch (error: any) {
      toast.error('Oracle 동기화 실패: ' + error.message);
      setShowOracleSync(false);
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
          <div className="flex gap-2">
            <Button
              onClick={() => setShowOracleSync(true)}
              variant="outline"
              className="bg-gray-800 border-gray-700 hover:bg-gray-700 text-white"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Oracle에서 동기화
            </Button>
            <Link href="/plcs/new">
              <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                <Plus className="h-4 w-4 mr-2" />
                새 PLC 추가
              </Button>
            </Link>
          </div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-800">
            <thead className="bg-gray-800">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">PLC 코드</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">이름</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">SPEC</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">타입</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">IP 주소</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">포트</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">프로토콜</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">네트워크번호</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">국번</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">타임아웃</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">상태</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">작업</th>
              </tr>
            </thead>
            <tbody className="bg-gray-900 divide-y divide-gray-800">
              {plcs.map((plc) => (
                <tr key={plc.id} className="hover:bg-gray-800/50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{plc.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-400">{plc.plc_code}</td>
                  <td className="px-6 py-4 text-sm font-medium text-gray-100">{plc.plc_name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{plc.plc_spec || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{plc.plc_type || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{plc.ip_address}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{plc.port}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{plc.protocol}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300 text-center">{plc.network_no}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300 text-center">{plc.station_no}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300 text-center">{plc.connection_timeout}초</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      plc.is_active
                        ? 'bg-green-500/20 text-green-400'
                        : 'bg-red-500/20 text-red-400'
                    }`}>
                      {plc.is_active ? '활성' : '비활성'}
                    </span>
                  </td>
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
      <OracleSyncDialog
        open={showOracleSync}
        onOpenChange={setShowOracleSync}
        onConfirm={handleSyncFromOracle}
        title="PLC Oracle 동기화"
        description="Oracle ICOM_PLC_MASTER 테이블에서 PLC 정보를 가져와 SQLite plc_connections 테이블과 동기화합니다."
        fetchConnectionInfo={getOracleConnectionInfo}
      />
    </div>
  );
}
