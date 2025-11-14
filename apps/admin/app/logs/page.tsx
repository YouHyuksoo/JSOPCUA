'use client';

import { useState } from 'react';
import { getLogs } from '@/lib/api/logs';
import { LogEntry, LogType } from '@/lib/types/log';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';

export default function LogsPage() {
  const [logType, setLogType] = useState<LogType>('scada');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(false);

  // Pagination
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  // Filters
  const [search, setSearch] = useState('');
  const [levels, setLevels] = useState<string[]>([]);
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');

  const fetchLogs = async (pageNum: number = page) => {
    setLoading(true);
    try {
      const params: any = {
        log_type: logType,
        page: pageNum,
        page_size: pageSize,
      };

      if (search) params.search = search;
      if (levels.length > 0) params.levels = levels;
      if (startTime) params.start_time = startTime;
      if (endTime) params.end_time = endTime;

      const data = await getLogs(params);
      setLogs(data.logs);
      setTotalPages(data.total_pages);
      setTotal(data.total);
      setPage(pageNum);
    } catch (error) {
      toast.error('로그 조회 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleLevelToggle = (level: string) => {
    setLevels(prev =>
      prev.includes(level)
        ? prev.filter(l => l !== level)
        : [...prev, level]
    );
  };

  const resetFilters = () => {
    setSearch('');
    setLevels([]);
    setStartTime('');
    setEndTime('');
    setPage(1);
  };

  return (
    <div>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6 text-gray-100">로그 조회</h1>

        {/* 로그 파일 선택 */}
        <div className="mb-4 flex gap-4 items-center">
          <Select value={logType} onValueChange={(value) => { setLogType(value as LogType); setPage(1); }}>
            <SelectTrigger className="w-64 bg-gray-900 border-gray-800 text-gray-100">
              <SelectValue placeholder="로그 파일 선택" />
            </SelectTrigger>
            <SelectContent className="bg-gray-900 border-gray-800">
              <SelectItem value="scada" className="text-gray-100 hover:bg-gray-800">scada.log</SelectItem>
              <SelectItem value="error" className="text-gray-100 hover:bg-gray-800">error.log</SelectItem>
              <SelectItem value="communication" className="text-gray-100 hover:bg-gray-800">communication.log</SelectItem>
              <SelectItem value="performance" className="text-gray-100 hover:bg-gray-800">performance.log</SelectItem>
              <SelectItem value="plc" className="text-gray-100 hover:bg-gray-800">plc.log</SelectItem>
              <SelectItem value="polling" className="text-gray-100 hover:bg-gray-800">polling.log</SelectItem>
              <SelectItem value="oracle_writer" className="text-gray-100 hover:bg-gray-800">oracle_writer.log</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={() => fetchLogs(1)} disabled={loading} className="bg-blue-600 hover:bg-blue-700">
            {loading ? '로딩 중...' : '조회'}
          </Button>
        </div>

        {/* 필터 */}
        <div className="mb-4 p-4 bg-gray-900 border border-gray-800 rounded-lg">
          <h3 className="text-sm font-medium text-gray-300 mb-3">필터</h3>

          {/* 검색 */}
          <div className="mb-3">
            <label className="text-xs text-gray-400 block mb-1">메시지 검색</label>
            <Input
              type="text"
              placeholder="검색 키워드"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-gray-800 border-gray-700 text-gray-100"
            />
          </div>

          {/* 로그 레벨 */}
          <div className="mb-3">
            <label className="text-xs text-gray-400 block mb-1">로그 레벨</label>
            <div className="flex gap-2 flex-wrap">
              {['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'].map(level => (
                <Button
                  key={level}
                  size="sm"
                  variant={levels.includes(level) ? 'default' : 'outline'}
                  onClick={() => handleLevelToggle(level)}
                  className={levels.includes(level) ? 'bg-blue-600' : 'bg-gray-800 border-gray-700'}
                >
                  {level}
                </Button>
              ))}
            </div>
          </div>

          {/* 시간 범위 */}
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div>
              <label className="text-xs text-gray-400 block mb-1">시작 시간</label>
              <Input
                type="datetime-local"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className="bg-gray-800 border-gray-700 text-gray-100"
              />
            </div>
            <div>
              <label className="text-xs text-gray-400 block mb-1">종료 시간</label>
              <Input
                type="datetime-local"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                className="bg-gray-800 border-gray-700 text-gray-100"
              />
            </div>
          </div>

          <Button onClick={resetFilters} variant="outline" size="sm" className="bg-gray-800 border-gray-700">
            필터 초기화
          </Button>
        </div>

        {/* 페이지네이션 정보 */}
        {logs.length > 0 && (
          <div className="mb-4 text-sm text-gray-400">
            총 {total}개 중 {((page - 1) * pageSize) + 1}-{Math.min(page * pageSize, total)}번째 로그 (페이지 {page}/{totalPages})
          </div>
        )}

        {/* 로그 목록 */}
        <div className="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden mb-4">
          <div className="bg-gray-950 p-4 overflow-x-auto" style={{ maxHeight: '600px', overflowY: 'auto' }}>
            <pre className="text-sm text-gray-100 font-mono">
              {logs.length === 0 ? (
                <div className="text-gray-400">로그를 조회하려면 위에서 파일을 선택하고 조회 버튼을 클릭하세요.</div>
              ) : (
                logs.map((log, index) => (
                  <div key={index} className="mb-1 hover:bg-gray-800 px-2 py-1 rounded">
                    <span className="text-gray-500">{log.timestamp}</span>{' '}
                    <span className={
                      log.level === 'ERROR' ? 'text-red-400' :
                      log.level === 'WARNING' ? 'text-yellow-400' :
                      log.level === 'INFO' ? 'text-blue-400' :
                      log.level === 'CRITICAL' ? 'text-red-600 font-bold' :
                      'text-gray-300'
                    }>
                      [{log.level}]
                    </span>{' '}
                    <span className="text-gray-100">{log.message}</span>
                  </div>
                ))
              )}
            </pre>
          </div>
        </div>

        {/* 페이지네이션 */}
        {totalPages > 1 && (
          <div className="flex justify-center items-center gap-2">
            <Button
              onClick={() => fetchLogs(1)}
              disabled={page === 1 || loading}
              size="sm"
              variant="outline"
              className="bg-gray-900 border-gray-800"
            >
              처음
            </Button>
            <Button
              onClick={() => fetchLogs(page - 1)}
              disabled={page === 1 || loading}
              size="sm"
              variant="outline"
              className="bg-gray-900 border-gray-800"
            >
              이전
            </Button>

            {/* 페이지 번호 */}
            <div className="flex gap-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let pageNum;
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (page <= 3) {
                  pageNum = i + 1;
                } else if (page >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = page - 2 + i;
                }

                return (
                  <Button
                    key={pageNum}
                    onClick={() => fetchLogs(pageNum)}
                    disabled={loading}
                    size="sm"
                    variant={page === pageNum ? 'default' : 'outline'}
                    className={page === pageNum ? 'bg-blue-600' : 'bg-gray-900 border-gray-800'}
                  >
                    {pageNum}
                  </Button>
                );
              })}
            </div>

            <Button
              onClick={() => fetchLogs(page + 1)}
              disabled={page === totalPages || loading}
              size="sm"
              variant="outline"
              className="bg-gray-900 border-gray-800"
            >
              다음
            </Button>
            <Button
              onClick={() => fetchLogs(totalPages)}
              disabled={page === totalPages || loading}
              size="sm"
              variant="outline"
              className="bg-gray-900 border-gray-800"
            >
              마지막
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
