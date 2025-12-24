'use client';

import { useEffect, useState } from 'react';
import { getTags, deleteTag, syncTagsFromOracle, getOracleConnectionInfo, getTagCategories, getMachineCodes } from '@/lib/api/tags';
import { Tag } from '@/lib/types/tag';
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
import { Plus, Search, Edit, Trash2, Loader2, Tag as TagIcon, RefreshCw, Filter, Upload } from 'lucide-react';

export default function TagsPage() {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [syncDialogOpen, setSyncDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedMachineCode, setSelectedMachineCode] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [categories, setCategories] = useState<string[]>([]);
  const [machineCodes, setMachineCodes] = useState<string[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const itemsPerPage = 20;

  const fetchCategories = async () => {
    try {
      const data = await getTagCategories();
      setCategories(data.categories);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  const fetchMachineCodes = async () => {
    try {
      const data = await getMachineCodes();
      setMachineCodes(data.machine_codes);
    } catch (error) {
      console.error('Failed to fetch machine codes:', error);
    }
  };

  const fetchTags = async (page = 1) => {
    setLoading(true);
    try {
      const validPage = Math.max(1, Number(page) || 1);
      const category = selectedCategory !== 'all' ? selectedCategory : undefined;
      const machineCode = selectedMachineCode !== 'all' ? selectedMachineCode : undefined;
      const data = await getTags(validPage, itemsPerPage, category, machineCode);
      setTags(data.items);
      setTotalPages(data.total_pages || 1);
      setTotalItems(data.total_count || 0);
      setCurrentPage(data.current_page || 1);
    } catch (error) {
      toast.error('태그 목록 조회 실패');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
    fetchMachineCodes();
  }, []);

  useEffect(() => {
    fetchTags(currentPage);
  }, [currentPage, selectedCategory, selectedMachineCode]);

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await deleteTag(deleteId);
      toast.success('태그가 삭제되었습니다');
      setDeleteId(null);
      fetchTags(currentPage);
    } catch (error) {
      toast.error('태그 삭제 실패');
    }
  };

  const handleSyncFromOracle = async () => {
    setSyncing(true);
    try {
      const result = await syncTagsFromOracle();

      if (result.success) {
        toast.success(
          `Oracle 동기화 완료\n` +
          `총 ${result.total_oracle_tags}개 중 ` +
          `${result.created}개 생성, ${result.updated}개 업데이트`,
          { duration: 5000 }
        );

        if (result.errors > 0) {
          toast.warning(
            `${result.errors}개 오류 발생\n${result.error_details.join('\n')}`,
            { duration: 8000 }
          );
        }

        // Refresh categories and tags, go to first page
        fetchCategories();
        setCurrentPage(1);
        fetchTags(1);

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

  // Filter tags based on search term and status (client-side filtering for current page)
  const filteredTags = tags.filter((tag) => {
    // Status filter
    if (statusFilter === 'active' && !tag.enabled) return false;
    if (statusFilter === 'inactive' && tag.enabled) return false;

    // Search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      return (
        (tag.tag_name?.toLowerCase() || '').includes(searchLower) ||
        (tag.tag_address?.toLowerCase() || '').includes(searchLower) ||
        (tag.tag_category?.toLowerCase() || '').includes(searchLower) ||
        (tag.data_type?.toLowerCase() || '').includes(searchLower)
      );
    }

    return true;
  });

  const getDataTypeBadge = (dataType: string) => {
    const type = dataType.toLowerCase();
    if (type === 'boolean' || type === 'bool' || type === 'bit') {
      return <span className="px-2 py-1 rounded bg-purple-500/20 text-purple-400 text-xs font-mono">{dataType}</span>;
    } else if (type === 'int' || type === 'word' || type === 'dword') {
      return <span className="px-2 py-1 rounded bg-blue-500/20 text-blue-400 text-xs font-mono">{dataType}</span>;
    } else if (type === 'float' || type === 'real' || type === 'double') {
      return <span className="px-2 py-1 rounded bg-green-500/20 text-green-400 text-xs font-mono">{dataType}</span>;
    } else if (type === 'string' || type === 'char') {
      return <span className="px-2 py-1 rounded bg-yellow-500/20 text-yellow-400 text-xs font-mono">{dataType}</span>;
    } else {
      return <span className="px-2 py-1 rounded bg-gray-500/20 text-gray-400 text-xs font-mono">{dataType}</span>;
    }
  };

  if (loading && tags.length === 0) {
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
            <TagIcon className="h-8 w-8" />
            태그 관리
          </h1>
          <p className="text-gray-400 mt-1">PLC 태그를 관리합니다</p>
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
          <Link href="/tags/upload">
            <Button variant="outline" className="bg-gray-800 border-gray-700 hover:bg-gray-700 text-white">
              <Upload className="h-4 w-4 mr-2" />
              CSV 업로드
            </Button>
          </Link>
          <Link href="/tags/new">
            <Button className="bg-blue-600 hover:bg-blue-700 text-white">
              <Plus className="h-4 w-4 mr-2" />
              새 태그 추가
            </Button>
          </Link>
        </div>
      </div>

      <Card className="bg-gray-900 border-gray-800">
        <CardHeader>
          <div className="flex items-center justify-between gap-4">
            <CardTitle className="text-white">태그 목록 ({totalItems})</CardTitle>
            <div className="flex items-center gap-2">
              {/* Category Filter */}
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-gray-400" />
                <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                  <SelectTrigger className="w-36 bg-gray-800 border-gray-700 text-white">
                    <SelectValue placeholder="태그 타입" />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-800 border-gray-700">
                    <SelectItem value="all" className="text-white hover:bg-gray-700">
                      전체 타입
                    </SelectItem>
                    {categories.map((category) => (
                      <SelectItem
                        key={category}
                        value={category}
                        className="text-white hover:bg-gray-700"
                      >
                        {category}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              {/* Machine Code Filter */}
              <Select value={selectedMachineCode} onValueChange={setSelectedMachineCode}>
                <SelectTrigger className="w-40 bg-gray-800 border-gray-700 text-white">
                  <SelectValue placeholder="설비코드" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700 max-h-60">
                  <SelectItem value="all" className="text-white hover:bg-gray-700">
                    전체 설비
                  </SelectItem>
                  {machineCodes.map((code) => (
                    <SelectItem
                      key={code}
                      value={code}
                      className="text-white hover:bg-gray-700"
                    >
                      {code}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {/* Status Filter */}
              <div className="flex items-center gap-2">
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-40 bg-gray-800 border-gray-700 text-white">
                    <SelectValue placeholder="상태" />
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
                  placeholder="태그 검색..."
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
                  <TableHead className="text-gray-400">태그 주소</TableHead>
                  <TableHead className="text-gray-400">태그 이름</TableHead>
                  <TableHead className="text-gray-400">태그 타입</TableHead>
                  <TableHead className="text-gray-400">데이터 타입</TableHead>
                  <TableHead className="text-gray-400">설비코드</TableHead>
                  <TableHead className="text-gray-400">PLC 코드</TableHead>
                  <TableHead className="text-gray-400">상태</TableHead>
                  <TableHead className="text-gray-400 text-right">작업</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredTags.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center text-gray-500 py-8">
                      태그가 없습니다
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredTags.map((tag) => (
                    <TableRow
                      key={tag.id}
                      className="border-gray-800 hover:bg-gray-800/50"
                    >
                      <TableCell className="font-medium text-white">{tag.id}</TableCell>
                      <TableCell className="text-gray-300">
                        <span className="px-2 py-1 bg-cyan-500/10 text-cyan-400 rounded text-xs font-mono">
                          {tag.tag_address}
                        </span>
                      </TableCell>
                      <TableCell className="text-white font-semibold">{tag.tag_name}</TableCell>
                      <TableCell className="text-gray-400">{tag.tag_category || '-'}</TableCell>
                      <TableCell>{getDataTypeBadge(tag.data_type)}</TableCell>
                      <TableCell className="text-gray-300">
                        {tag.machine_code ? (
                          <span className="px-2 py-1 bg-orange-500/10 text-orange-400 rounded text-xs font-mono">
                            {tag.machine_code}
                          </span>
                        ) : (
                          <span className="text-gray-500">-</span>
                        )}
                      </TableCell>
                      <TableCell className="text-gray-300">
                        {tag.plc_code ? (
                          <span className="px-2 py-1 bg-indigo-500/10 text-indigo-400 rounded text-xs font-mono">
                            {tag.plc_code}
                          </span>
                        ) : (
                          <span className="text-gray-500">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {tag.enabled ? (
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
                        <Link href={`/tags/${tag.id}`}>
                          <Button size="sm" variant="outline" className="bg-gray-800 border-gray-700 hover:bg-gray-700">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </Link>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => setDeleteId(tag.id)}
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
        title="태그 Oracle 동기화"
        description="Oracle ICOM_PLC_TAG_MASTER 테이블에서 태그 정보를 가져와 동기화합니다."
        fetchConnectionInfo={getOracleConnectionInfo}
      />
    </div>
  );
}
