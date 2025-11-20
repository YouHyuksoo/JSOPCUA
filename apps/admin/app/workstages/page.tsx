'use client';

import { useEffect, useState } from 'react';
import { getWorkstages, deleteWorkstage, syncWorkstagesFromOracle, getOracleConnectionInfo } from '@/lib/api/workstages';
import { Workstage } from '@/lib/types/workstage';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import DeleteDialog from '@/components/DeleteDialog';
import OracleSyncDialog from '@/components/OracleSyncDialog';
import TablePagination from '@/components/TablePagination';
import { toast } from 'sonner';
import { Plus, Search, Edit, Trash2, Loader2, Factory, RefreshCw, Filter } from 'lucide-react';

export default function WorkstagesPage() {
  const [workstages, setWorkstages] = useState<Workstage[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [syncDialogOpen, setSyncDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const itemsPerPage = 20;

  const fetchWorkstages = async (page = 1) => {
    setLoading(true);
    try {
      const data = await getWorkstages(page, itemsPerPage);
      setWorkstages(data.items);
      setTotalPages(data.total_pages);
      setTotalItems(data.total_count);
      setCurrentPage(data.current_page);
    } catch (error) {
      toast.error('공정 목록 조회 실패');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkstages(currentPage);
  }, [currentPage]);

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await deleteWorkstage(deleteId);
      toast.success('공정이 삭제되었습니다');
      setDeleteId(null);
      fetchWorkstages(currentPage);
    } catch (error) {
      toast.error('공정 삭제 실패');
    }
  };

  const handleSyncFromOracle = async () => {
    setSyncing(true);
    try {
      const result = await syncWorkstagesFromOracle();

      if (result.success) {
        toast.success(
          `Oracle 동기화 완료\n` +
          `총 ${result.total_oracle_workstages}개 중 ` +
          `${result.created}개 생성, ${result.updated}개 업데이트`,
          { duration: 5000 }
        );

        if (result.errors > 0) {
          toast.warning(
            `${result.errors}개 오류 발생\n${result.error_details.join('\n')}`,
            { duration: 8000 }
          );
        }

        // Refresh workstage list and go to first page
        setCurrentPage(1);
        fetchWorkstages(1);

        // Close dialog
        setSyncDialogOpen(false);
      } else {
        toast.error('Oracle 동기화 실패');
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || 'Oracle 동기화 중 오류 발생';
      toast.error(errorMsg, { duration: 8000 });
    } finally {
      setSyncing(false);
    }
  };

  // Filter workstages based on search term and status (client-side filtering for current page)
  const filteredWorkstages = workstages.filter((workstage) => {
    // Status filter
    if (statusFilter === 'active' && !workstage.enabled) return false;
    if (statusFilter === 'inactive' && workstage.enabled) return false;

    // Search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      return (
        (workstage.workstage_name?.toLowerCase() || '').includes(searchLower) ||
        (workstage.workstage_code?.toLowerCase() || '').includes(searchLower) ||
        (workstage.equipment_type?.toLowerCase() || '').includes(searchLower)
      );
    }

    return true;
  });

  if (loading && workstages.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <Factory className="h-8 w-8" />
            공정 관리
          </h1>
          <p className="text-gray-400 mt-1">생산 공정을 관리합니다</p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={() => setSyncDialogOpen(true)}
            disabled={syncing}
            variant="outline"
            className="bg-gray-800 border-gray-700 hover:bg-gray-700 text-white"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Oracle에서 동기화
          </Button>
          <Link href="/workstages/new">
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="h-4 w-4 mr-2" />
              새 공정 추가
            </Button>
          </Link>
        </div>
      </div>

      <Card className="bg-gray-900 border-gray-800">
        <CardHeader>
          <div className="flex items-center justify-between gap-4">
            <CardTitle className="text-white">공정 목록 ({totalItems})</CardTitle>
            <div className="flex items-center gap-2">
              {/* Status Filter */}
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-gray-400" />
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-40 bg-gray-800 border-gray-700 text-white">
                    <SelectValue placeholder="상태 선택" />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-800 border-gray-700">
                    <SelectItem value="all" className="text-white hover:bg-gray-700">
                      전체 상태
                    </SelectItem>
                    <SelectItem value="active" className="text-white hover:bg-gray-700">
                      활성
                    </SelectItem>
                    <SelectItem value="inactive" className="text-white hover:bg-gray-700">
                      비활성
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
              {/* Search */}
              <div className="relative w-64">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="공정 검색..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-gray-800 border-gray-700 text-white"
                />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border border-gray-800 overflow-hidden">
            <Table>
              <TableHeader className="bg-gray-800">
                <TableRow className="hover:bg-gray-800">
                  <TableHead className="text-gray-400">ID</TableHead>
                  <TableHead className="text-gray-400">공정 이름</TableHead>
                  <TableHead className="text-gray-400">공정 코드</TableHead>
                  <TableHead className="text-gray-400">설비 코드</TableHead>
                  <TableHead className="text-gray-400">설비 유형</TableHead>
                  <TableHead className="text-gray-400">순서</TableHead>
                  <TableHead className="text-gray-400">상태</TableHead>
                  <TableHead className="text-gray-400 text-right">작업</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredWorkstages.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center text-gray-500 py-8">
                      공정이 없습니다
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredWorkstages.map((workstage) => (
                    <TableRow
                      key={workstage.id}
                      className="border-gray-800 hover:bg-gray-800/50"
                    >
                      <TableCell className="font-medium text-white">{workstage.id}</TableCell>
                      <TableCell className="text-white font-semibold">{workstage.workstage_name}</TableCell>
                      <TableCell className="text-gray-300">
                        <span className="px-2 py-1 bg-purple-500/10 text-purple-400 rounded text-xs font-mono">
                          {workstage.workstage_code}
                        </span>
                      </TableCell>
                      <TableCell className="text-gray-300">
                        <span className="px-2 py-1 bg-blue-500/10 text-blue-400 rounded text-xs font-mono">
                          {workstage.machine_code || '-'}
                        </span>
                      </TableCell>
                      <TableCell className="text-gray-400">{workstage.equipment_type || '-'}</TableCell>
                      <TableCell className="text-gray-400">{workstage.workstage_sequence}</TableCell>
                      <TableCell>
                        {workstage.enabled ? (
                          <span className="px-2 py-1 bg-green-500/10 text-green-400 rounded text-xs">
                            활성
                          </span>
                        ) : (
                          <span className="px-2 py-1 bg-gray-500/10 text-gray-400 rounded text-xs">
                            비활성
                          </span>
                        )}
                      </TableCell>
                      <TableCell className="text-right space-x-2">
                        <Link href={`/workstages/${workstage.id}`}>
                          <Button size="sm" variant="outline" className="bg-gray-800 border-gray-700 hover:bg-gray-700">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </Link>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => setDeleteId(workstage.id)}
                          className="bg-red-500/10 text-red-500 hover:bg-red-500/20"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
          <TablePagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={totalItems}
            itemsPerPage={itemsPerPage}
            onPageChange={(page) => setCurrentPage(page)}
          />
        </CardContent>
      </Card>

      <DeleteDialog
        open={deleteId !== null}
        onOpenChange={(open) => !open && setDeleteId(null)}
        onConfirm={handleDelete}
      />

      <OracleSyncDialog
        open={syncDialogOpen}
        onOpenChange={setSyncDialogOpen}
        onConfirm={handleSyncFromOracle}
        syncing={syncing}
        title="공정 Oracle 동기화"
        description="Oracle ICOM_WORKSTAGE_MASTER 테이블에서 공정 정보를 가져와 동기화합니다."
        fetchConnectionInfo={getOracleConnectionInfo}
      />
    </div>
  );
}
