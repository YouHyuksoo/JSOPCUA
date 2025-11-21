'use client';

import { useState, useEffect } from 'react';
import {
  getOracleConnectionStatus,
  getOperations,
  getDatatagLogs,
  getDataSummary,
  OracleConnectionStatus,
  OperationRecord,
  DatatagLogRecord,
  DataSummary,
} from '@/lib/api/oracle-data';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import {
  Database,
  RefreshCw,
  Search,
  Loader2,
  CheckCircle2,
  XCircle,
  Clock,
  Activity,
  AlertTriangle,
} from 'lucide-react';

export default function OracleDataPage() {
  // Connection status
  const [connectionStatus, setConnectionStatus] = useState<OracleConnectionStatus | null>(null);
  const [checkingConnection, setCheckingConnection] = useState(false);

  // Summary
  const [summary, setSummary] = useState<DataSummary | null>(null);
  const [loadingSummary, setLoadingSummary] = useState(false);

  // Operations data
  const [operations, setOperations] = useState<OperationRecord[]>([]);
  const [loadingOperations, setLoadingOperations] = useState(false);
  const [operationFilter, setOperationFilter] = useState('');

  // Datatag logs data
  const [datatagLogs, setDatatagLogs] = useState<DatatagLogRecord[]>([]);
  const [loadingDatatagLogs, setLoadingDatatagLogs] = useState(false);
  const [datatagNameFilter, setDatatagNameFilter] = useState('');
  const [datatagTypeFilter, setDatatagTypeFilter] = useState<string>('all');

  // Common settings
  const [hours, setHours] = useState<number>(24);
  const [limit, setLimit] = useState<number>(100);

  // Check Oracle connection
  const checkConnection = async () => {
    setCheckingConnection(true);
    try {
      const status = await getOracleConnectionStatus();
      setConnectionStatus(status);
      if (status.connected) {
        toast.success('Oracle 연결 성공');
      } else {
        toast.error(`Oracle 연결 실패: ${status.message}`);
      }
    } catch (error: any) {
      toast.error('Oracle 연결 확인 실패');
      setConnectionStatus(null);
    } finally {
      setCheckingConnection(false);
    }
  };

  // Load summary
  const loadSummary = async () => {
    setLoadingSummary(true);
    try {
      const data = await getDataSummary(hours);
      setSummary(data);
    } catch (error: any) {
      toast.error('요약 데이터 조회 실패');
    } finally {
      setLoadingSummary(false);
    }
  };

  // Load XSCADA_OPERATION data
  const loadOperations = async () => {
    setLoadingOperations(true);
    try {
      const data = await getOperations({
        limit,
        hours,
        name_filter: operationFilter || undefined,
      });
      if (data.success) {
        setOperations(data.items);
      } else {
        toast.error(data.message || 'OPERATION 조회 실패');
      }
    } catch (error: any) {
      toast.error('OPERATION 데이터 조회 실패');
    } finally {
      setLoadingOperations(false);
    }
  };

  // Load XSCADA_DATATAG_LOG data
  const loadDatatagLogs = async () => {
    setLoadingDatatagLogs(true);
    try {
      const data = await getDatatagLogs({
        limit,
        hours,
        datatag_name_filter: datatagNameFilter || undefined,
        datatag_type_filter: datatagTypeFilter !== 'all' ? datatagTypeFilter : undefined,
      });
      if (data.success) {
        setDatatagLogs(data.items);
      } else {
        toast.error(data.message || 'DATATAG_LOG 조회 실패');
      }
    } catch (error: any) {
      toast.error('DATATAG_LOG 데이터 조회 실패');
    } finally {
      setLoadingDatatagLogs(false);
    }
  };

  // Initial load
  useEffect(() => {
    checkConnection();
    loadSummary();
  }, []);

  // Format datetime
  const formatDateTime = (isoString: string) => {
    if (!isoString) return '-';
    try {
      return new Date(isoString).toLocaleString('ko-KR');
    } catch {
      return isoString;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <Database className="h-8 w-8" />
            Oracle 데이터 조회
          </h1>
          <p className="text-gray-400 mt-1">XSCADA_OPERATION, XSCADA_DATATAG_LOG 테이블 데이터 조회</p>
        </div>
      </div>

      {/* Connection Status Card */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-white flex items-center gap-2">
                Oracle 연결 상태
              </CardTitle>
              <CardDescription className="text-gray-400">
                데이터베이스 연결 정보
              </CardDescription>
            </div>
            <Button
              onClick={checkConnection}
              disabled={checkingConnection}
              variant="outline"
              className="bg-gray-800 border-gray-700 hover:bg-gray-700 text-white"
            >
              {checkingConnection ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4 mr-2" />
              )}
              연결 확인
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {connectionStatus ? (
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                {connectionStatus.connected ? (
                  <CheckCircle2 className="h-5 w-5 text-green-400" />
                ) : (
                  <XCircle className="h-5 w-5 text-red-400" />
                )}
                <span className={connectionStatus.connected ? 'text-green-400' : 'text-red-400'}>
                  {connectionStatus.connected ? '연결됨' : '연결 실패'}
                </span>
              </div>
              <div className="text-gray-400">
                <span className="text-gray-500">Host: </span>
                <span className="text-cyan-400 font-mono">{connectionStatus.host}:{connectionStatus.port}</span>
              </div>
              <div className="text-gray-400">
                <span className="text-gray-500">Service: </span>
                <span className="text-cyan-400 font-mono">{connectionStatus.service_name}</span>
              </div>
              {connectionStatus.message && !connectionStatus.connected && (
                <div className="text-red-400 text-sm">{connectionStatus.message}</div>
              )}
            </div>
          ) : (
            <div className="text-gray-500">연결 상태를 확인해주세요</div>
          )}
        </CardContent>
      </Card>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">XSCADA_OPERATION</p>
                <p className="text-2xl font-bold text-white">
                  {loadingSummary ? '-' : (summary?.xscada_operation.count || 0).toLocaleString()}
                </p>
              </div>
              <Activity className="h-8 w-8 text-blue-400" />
            </div>
            <p className="text-gray-500 text-xs mt-2">최근 {hours}시간</p>
          </CardContent>
        </Card>

        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">XSCADA_DATATAG_LOG</p>
                <p className="text-2xl font-bold text-white">
                  {loadingSummary ? '-' : (summary?.xscada_datatag_log.total_count || 0).toLocaleString()}
                </p>
              </div>
              <AlertTriangle className="h-8 w-8 text-yellow-400" />
            </div>
            <p className="text-gray-500 text-xs mt-2">최근 {hours}시간</p>
          </CardContent>
        </Card>

        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">조회 범위</p>
                <p className="text-2xl font-bold text-white">{hours}시간</p>
              </div>
              <Clock className="h-8 w-8 text-green-400" />
            </div>
            <div className="flex gap-2 mt-2">
              {[1, 6, 24, 48, 168].map((h) => (
                <button
                  key={h}
                  onClick={() => {
                    setHours(h);
                    setTimeout(() => loadSummary(), 100);
                  }}
                  className={`px-2 py-1 text-xs rounded ${
                    hours === h
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  {h}h
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Data Tabs */}
      <Tabs defaultValue="operations" className="w-full">
        <TabsList className="bg-gray-800 border-gray-700">
          <TabsTrigger value="operations" className="data-[state=active]:bg-gray-700">
            XSCADA_OPERATION
          </TabsTrigger>
          <TabsTrigger value="datatag-logs" className="data-[state=active]:bg-gray-700">
            XSCADA_DATATAG_LOG
          </TabsTrigger>
        </TabsList>

        {/* XSCADA_OPERATION Tab */}
        <TabsContent value="operations">
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-white">XSCADA_OPERATION 데이터</CardTitle>
                <div className="flex items-center gap-2">
                  <div className="relative w-64">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="NAME 검색..."
                      value={operationFilter}
                      onChange={(e) => setOperationFilter(e.target.value)}
                      className="pl-10 bg-gray-800 border-gray-700 text-white"
                    />
                  </div>
                  <Select value={String(limit)} onValueChange={(v) => setLimit(Number(v))}>
                    <SelectTrigger className="w-24 bg-gray-800 border-gray-700 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-800 border-gray-700">
                      <SelectItem value="50">50</SelectItem>
                      <SelectItem value="100">100</SelectItem>
                      <SelectItem value="200">200</SelectItem>
                      <SelectItem value="500">500</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button
                    onClick={loadOperations}
                    disabled={loadingOperations || !connectionStatus?.connected}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    {loadingOperations ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Search className="h-4 w-4" />
                    )}
                    <span className="ml-2">조회</span>
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="rounded-lg border border-gray-800 overflow-hidden">
                <Table>
                  <TableHeader className="bg-gray-800">
                    <TableRow className="hover:bg-gray-800">
                      <TableHead className="text-gray-400">TIME</TableHead>
                      <TableHead className="text-gray-400">NAME</TableHead>
                      <TableHead className="text-gray-400">VALUE</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {operations.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={3} className="text-center text-gray-500 py-8">
                          {loadingOperations ? '조회 중...' : '데이터가 없습니다. 조회 버튼을 클릭하세요.'}
                        </TableCell>
                      </TableRow>
                    ) : (
                      operations.map((row, idx) => (
                        <TableRow key={idx} className="border-gray-800 hover:bg-gray-800/50">
                          <TableCell className="text-gray-300 font-mono text-sm">
                            {formatDateTime(row.time)}
                          </TableCell>
                          <TableCell className="text-cyan-400 font-mono text-sm">{row.name}</TableCell>
                          <TableCell className="text-white">{row.value || '-'}</TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
              <div className="mt-2 text-sm text-gray-500 text-right">
                조회 결과: {operations.length}건
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* XSCADA_DATATAG_LOG Tab */}
        <TabsContent value="datatag-logs">
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-white">XSCADA_DATATAG_LOG 데이터</CardTitle>
                <div className="flex items-center gap-2">
                  <div className="relative w-48">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="DATATAG_NAME..."
                      value={datatagNameFilter}
                      onChange={(e) => setDatatagNameFilter(e.target.value)}
                      className="pl-10 bg-gray-800 border-gray-700 text-white"
                    />
                  </div>
                  <Select value={datatagTypeFilter} onValueChange={setDatatagTypeFilter}>
                    <SelectTrigger className="w-32 bg-gray-800 border-gray-700 text-white">
                      <SelectValue placeholder="타입" />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-800 border-gray-700">
                      <SelectItem value="all">전체</SelectItem>
                      <SelectItem value="STATE">STATE</SelectItem>
                      <SelectItem value="ALARM">ALARM</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={String(limit)} onValueChange={(v) => setLimit(Number(v))}>
                    <SelectTrigger className="w-24 bg-gray-800 border-gray-700 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-800 border-gray-700">
                      <SelectItem value="50">50</SelectItem>
                      <SelectItem value="100">100</SelectItem>
                      <SelectItem value="200">200</SelectItem>
                      <SelectItem value="500">500</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button
                    onClick={loadDatatagLogs}
                    disabled={loadingDatatagLogs || !connectionStatus?.connected}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    {loadingDatatagLogs ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Search className="h-4 w-4" />
                    )}
                    <span className="ml-2">조회</span>
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="rounded-lg border border-gray-800 overflow-hidden">
                <Table>
                  <TableHeader className="bg-gray-800">
                    <TableRow className="hover:bg-gray-800">
                      <TableHead className="text-gray-400">ID</TableHead>
                      <TableHead className="text-gray-400">CTIME</TableHead>
                      <TableHead className="text-gray-400">DATATAG_NAME</TableHead>
                      <TableHead className="text-gray-400">TYPE</TableHead>
                      <TableHead className="text-gray-400">VALUE_STR</TableHead>
                      <TableHead className="text-gray-400">VALUE_NUM</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {datatagLogs.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} className="text-center text-gray-500 py-8">
                          {loadingDatatagLogs ? '조회 중...' : '데이터가 없습니다. 조회 버튼을 클릭하세요.'}
                        </TableCell>
                      </TableRow>
                    ) : (
                      datatagLogs.map((row) => (
                        <TableRow key={row.id} className="border-gray-800 hover:bg-gray-800/50">
                          <TableCell className="text-gray-400 font-mono text-sm">{row.id}</TableCell>
                          <TableCell className="text-gray-300 font-mono text-sm">
                            {formatDateTime(row.ctime)}
                          </TableCell>
                          <TableCell className="text-cyan-400 font-mono text-sm">{row.datatag_name}</TableCell>
                          <TableCell>
                            {row.datatag_type && (
                              <span
                                className={`px-2 py-1 rounded text-xs ${
                                  row.datatag_type === 'STATE'
                                    ? 'bg-blue-500/20 text-blue-400'
                                    : row.datatag_type === 'ALARM'
                                    ? 'bg-red-500/20 text-red-400'
                                    : 'bg-gray-500/20 text-gray-400'
                                }`}
                              >
                                {row.datatag_type}
                              </span>
                            )}
                          </TableCell>
                          <TableCell className="text-white text-sm">{row.value_str || '-'}</TableCell>
                          <TableCell className="text-yellow-400 font-mono text-sm">
                            {row.value_num !== null ? row.value_num : '-'}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
              <div className="mt-2 text-sm text-gray-500 text-right">
                조회 결과: {datatagLogs.length}건
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
