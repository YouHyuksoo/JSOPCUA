'use client';

import { useEffect, useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Loader2, Database, Server, User, Hash, AlertCircle } from 'lucide-react';

export interface OracleConnectionInfo {
  host: string;
  port: number;
  service_name: string;
  username: string;
  password: string;
  pool_min: number;
  pool_max: number;
  dsn: string;
}

interface OracleSyncDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  syncing?: boolean;
  title?: string;
  description?: string;
  fetchConnectionInfo: () => Promise<OracleConnectionInfo>;
}

export default function OracleSyncDialog({
  open,
  onOpenChange,
  onConfirm,
  syncing = false,
  title = 'Oracle 데이터베이스 동기화',
  description = '아래 Oracle DB에서 데이터를 가져옵니다',
  fetchConnectionInfo,
}: OracleSyncDialogProps) {
  const [connectionInfo, setConnectionInfo] = useState<OracleConnectionInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      loadConnectionInfo();
    }
  }, [open]);

  const loadConnectionInfo = async () => {
    setLoading(true);
    setError(null);
    try {
      const info = await fetchConnectionInfo();
      setConnectionInfo(info);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Oracle 접속 정보를 가져오지 못했습니다');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = () => {
    onConfirm();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] bg-gray-900 border-gray-800">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <Database className="h-5 w-5 text-blue-400" />
            {title}
          </DialogTitle>
          <DialogDescription className="text-gray-400">
            {description}
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
            </div>
          ) : error ? (
            <div className="flex items-center gap-2 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
              <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0" />
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          ) : connectionInfo ? (
            <div className="space-y-3">
              <div className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-3 text-sm">
                <div className="flex items-center gap-2 text-gray-400">
                  <Server className="h-4 w-4" />
                  <span>호스트</span>
                </div>
                <div className="text-white font-mono">{connectionInfo.host}</div>

                <div className="flex items-center gap-2 text-gray-400">
                  <Hash className="h-4 w-4" />
                  <span>포트</span>
                </div>
                <div className="text-white font-mono">{connectionInfo.port}</div>

                <div className="flex items-center gap-2 text-gray-400">
                  <Database className="h-4 w-4" />
                  <span>서비스명</span>
                </div>
                <div className="text-white font-mono">{connectionInfo.service_name}</div>

                <div className="flex items-center gap-2 text-gray-400">
                  <User className="h-4 w-4" />
                  <span>사용자</span>
                </div>
                <div className="text-white font-mono">{connectionInfo.username}</div>
              </div>

              <div className="pt-3 border-t border-gray-800">
                <div className="text-xs text-gray-500">연결 문자열</div>
                <div className="text-sm text-gray-300 font-mono mt-1 bg-gray-800/50 p-2 rounded">
                  {connectionInfo.dsn}
                </div>
              </div>

              <div className="pt-2">
                <p className="text-xs text-gray-400">
                  • ICOM_MACHINE_MASTER 테이블에서 USE_YN='Y'인 설비를 가져옵니다
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  • 기존 설비는 업데이트되고, 새로운 설비는 생성됩니다
                </p>
              </div>
            </div>
          ) : null}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={syncing}
            className="bg-gray-800 border-gray-700 hover:bg-gray-700 text-white"
          >
            취소
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={syncing || loading || !!error}
            className="bg-green-600 hover:bg-green-700"
          >
            {syncing ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                동기화 중...
              </>
            ) : (
              '동기화 시작'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
