'use client';

import { useEffect, useState } from 'react';
import { getEnvConfig, updateEnvConfig, testOracleConnection, type EnvConfig } from '@/lib/api/system';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Settings, Save, Loader2, Database, Server, Cloud, AlertCircle, CheckCircle, XCircle, Eye, EyeOff } from 'lucide-react';

export default function SettingsPage() {
  const [config, setConfig] = useState<EnvConfig>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testingOracle, setTestingOracle] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const data = await getEnvConfig();
      setConfig(data);
    } catch (error: any) {
      toast.error('설정 조회 실패: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const result = await updateEnvConfig(config as any);
      toast.success('설정이 저장되었습니다\n재시작 후 적용됩니다', { duration: 5000 });
      setConfig(result.config);
    } catch (error: any) {
      toast.error('설정 저장 실패: ' + error.message);
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (key: string, value: string) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };

  const handleTestOracleConnection = async () => {
    setTestingOracle(true);
    try {
      const result = await testOracleConnection();
      if (result.success) {
        toast.success(
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="font-semibold">{result.message}</span>
            </div>
            {result.connection_info && (
              <div className="text-xs text-gray-300 space-y-1 ml-6">
                <div>Host: {result.connection_info.host}:{result.connection_info.port}</div>
                <div>Service: {result.connection_info.service_name}</div>
                <div>User: {result.connection_info.username}</div>
              </div>
            )}
          </div>,
          { duration: 5000 }
        );
      } else {
        toast.error(
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <XCircle className="h-4 w-4 text-red-500" />
              <span className="font-semibold">{result.message}</span>
            </div>
            {result.error_details && (
              <div className="text-xs text-gray-300 ml-6">{result.error_details}</div>
            )}
          </div>,
          { duration: 7000 }
        );
      }
    } catch (error: any) {
      toast.error('Oracle 연결 테스트 실패: ' + error.message);
    } finally {
      setTestingOracle(false);
    }
  };

  if (loading) {
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
            <Settings className="h-8 w-8" />
            시스템 설정
          </h1>
          <p className="text-gray-400 mt-1">환경 변수 (.env) 설정 관리</p>
        </div>
        <Button onClick={handleSave} disabled={saving} className="bg-blue-600 hover:bg-blue-700">
          {saving ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              저장 중...
            </>
          ) : (
            <>
              <Save className="h-4 w-4 mr-2" />
              저장
            </>
          )}
        </Button>
      </div>

      <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4 flex items-start gap-3">
        <AlertCircle className="h-5 w-5 text-yellow-400 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-yellow-200">
          <p className="font-semibold">주의사항</p>
          <p className="mt-1">설정 변경 후 백엔드 서버를 재시작해야 적용됩니다.</p>
        </div>
      </div>

      {/* Database Configuration */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Database className="h-5 w-5 text-blue-400" />
            데이터베이스 설정
          </CardTitle>
          <CardDescription>SQLite 데이터베이스 경로</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="DATABASE_PATH" className="text-gray-300">
              Database Path
            </Label>
            <Input
              id="DATABASE_PATH"
              value={config.DATABASE_PATH || ''}
              onChange={(e) => handleChange('DATABASE_PATH', e.target.value)}
              className="bg-gray-800 border-gray-700 text-white mt-1"
            />
          </div>
        </CardContent>
      </Card>

      {/* API Server Configuration */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Server className="h-5 w-5 text-green-400" />
            API 서버 설정
          </CardTitle>
          <CardDescription>FastAPI 서버 접속 정보</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="API_HOST" className="text-gray-300">
                Host
              </Label>
              <Input
                id="API_HOST"
                value={config.API_HOST || ''}
                onChange={(e) => handleChange('API_HOST', e.target.value)}
                className="bg-gray-800 border-gray-700 text-white mt-1"
              />
            </div>
            <div>
              <Label htmlFor="API_PORT" className="text-gray-300">
                Port
              </Label>
              <Input
                id="API_PORT"
                type="number"
                value={config.API_PORT || ''}
                onChange={(e) => handleChange('API_PORT', e.target.value)}
                className="bg-gray-800 border-gray-700 text-white mt-1"
              />
            </div>
          </div>
          <div>
            <Label htmlFor="CORS_ORIGINS" className="text-gray-300">
              CORS Origins (쉼표로 구분)
            </Label>
            <Input
              id="CORS_ORIGINS"
              value={config.CORS_ORIGINS || ''}
              onChange={(e) => handleChange('CORS_ORIGINS', e.target.value)}
              placeholder="http://localhost:3000,http://localhost:3001"
              className="bg-gray-800 border-gray-700 text-white mt-1"
            />
          </div>
        </CardContent>
      </Card>

      {/* Oracle Database Configuration */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Cloud className="h-5 w-5 text-orange-400" />
            Oracle 데이터베이스 설정
          </CardTitle>
          <CardDescription>Oracle DB 접속 정보</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="ORACLE_HOST" className="text-gray-300">
                Host
              </Label>
              <Input
                id="ORACLE_HOST"
                value={config.ORACLE_HOST || ''}
                onChange={(e) => handleChange('ORACLE_HOST', e.target.value)}
                className="bg-gray-800 border-gray-700 text-white mt-1"
              />
            </div>
            <div>
              <Label htmlFor="ORACLE_PORT" className="text-gray-300">
                Port
              </Label>
              <Input
                id="ORACLE_PORT"
                type="number"
                value={config.ORACLE_PORT || ''}
                onChange={(e) => handleChange('ORACLE_PORT', e.target.value)}
                className="bg-gray-800 border-gray-700 text-white mt-1"
              />
            </div>
          </div>
          <div>
            <Label htmlFor="ORACLE_SERVICE_NAME" className="text-gray-300">
              Service Name
            </Label>
            <Input
              id="ORACLE_SERVICE_NAME"
              value={config.ORACLE_SERVICE_NAME || ''}
              onChange={(e) => handleChange('ORACLE_SERVICE_NAME', e.target.value)}
              className="bg-gray-800 border-gray-700 text-white mt-1"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="ORACLE_USERNAME" className="text-gray-300">
                Username
              </Label>
              <Input
                id="ORACLE_USERNAME"
                value={config.ORACLE_USERNAME || ''}
                onChange={(e) => handleChange('ORACLE_USERNAME', e.target.value)}
                className="bg-gray-800 border-gray-700 text-white mt-1"
              />
            </div>
            <div>
              <Label htmlFor="ORACLE_PASSWORD" className="text-gray-300">
                Password <span className="text-xs text-yellow-500">(대소문자 구분)</span>
              </Label>
              <div className="relative mt-1">
                <Input
                  id="ORACLE_PASSWORD"
                  type={showPassword ? "text" : "password"}
                  value={config.ORACLE_PASSWORD === '***' ? '' : (config.ORACLE_PASSWORD || '')}
                  onChange={(e) => handleChange('ORACLE_PASSWORD', e.target.value)}
                  placeholder="비밀번호 입력 (기존 값 유지하려면 비워두세요)"
                  className="bg-gray-800 border-gray-700 text-white font-mono pr-10"
                  autoComplete="off"
                  spellCheck={false}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-200 transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="ORACLE_POOL_MIN" className="text-gray-300">
                Pool Min
              </Label>
              <Input
                id="ORACLE_POOL_MIN"
                type="number"
                value={config.ORACLE_POOL_MIN || ''}
                onChange={(e) => handleChange('ORACLE_POOL_MIN', e.target.value)}
                className="bg-gray-800 border-gray-700 text-white mt-1"
              />
            </div>
            <div>
              <Label htmlFor="ORACLE_POOL_MAX" className="text-gray-300">
                Pool Max
              </Label>
              <Input
                id="ORACLE_POOL_MAX"
                type="number"
                value={config.ORACLE_POOL_MAX || ''}
                onChange={(e) => handleChange('ORACLE_POOL_MAX', e.target.value)}
                className="bg-gray-800 border-gray-700 text-white mt-1"
              />
            </div>
          </div>
          <div className="pt-4 border-t border-gray-800">
            <Button
              onClick={handleTestOracleConnection}
              disabled={testingOracle}
              variant="outline"
              className="bg-green-600 hover:bg-green-700 text-white border-green-600"
            >
              {testingOracle ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  테스트 중...
                </>
              ) : (
                <>
                  <Database className="mr-2 h-4 w-4" />
                  Oracle 연결 테스트
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Polling & PLC Configuration */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader>
          <CardTitle className="text-white">폴링 & PLC 연결 설정</CardTitle>
          <CardDescription>폴링 그룹 및 PLC 연결 풀 설정</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <Label htmlFor="MAX_POLLING_GROUPS" className="text-gray-300">
                Max Polling Groups
              </Label>
              <Input
                id="MAX_POLLING_GROUPS"
                type="number"
                value={config.MAX_POLLING_GROUPS || ''}
                onChange={(e) => handleChange('MAX_POLLING_GROUPS', e.target.value)}
                className="bg-gray-800 border-gray-700 text-white mt-1"
              />
            </div>
            <div>
              <Label htmlFor="POOL_SIZE_PER_PLC" className="text-gray-300">
                Pool Size Per PLC
              </Label>
              <Input
                id="POOL_SIZE_PER_PLC"
                type="number"
                value={config.POOL_SIZE_PER_PLC || ''}
                onChange={(e) => handleChange('POOL_SIZE_PER_PLC', e.target.value)}
                className="bg-gray-800 border-gray-700 text-white mt-1"
              />
            </div>
            <div>
              <Label htmlFor="CONNECTION_TIMEOUT" className="text-gray-300">
                Connection Timeout (s)
              </Label>
              <Input
                id="CONNECTION_TIMEOUT"
                type="number"
                value={config.CONNECTION_TIMEOUT || ''}
                onChange={(e) => handleChange('CONNECTION_TIMEOUT', e.target.value)}
                className="bg-gray-800 border-gray-700 text-white mt-1"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Buffer Configuration */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader>
          <CardTitle className="text-white">버퍼 설정</CardTitle>
          <CardDescription>데이터 버퍼 및 Oracle Writer 설정</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <Label htmlFor="BUFFER_MAX_SIZE" className="text-gray-300">
                Buffer Max Size
              </Label>
              <Input
                id="BUFFER_MAX_SIZE"
                type="number"
                value={config.BUFFER_MAX_SIZE || ''}
                onChange={(e) => handleChange('BUFFER_MAX_SIZE', e.target.value)}
                className="bg-gray-800 border-gray-700 text-white mt-1"
              />
            </div>
            <div>
              <Label htmlFor="BUFFER_BATCH_SIZE" className="text-gray-300">
                Batch Size
              </Label>
              <Input
                id="BUFFER_BATCH_SIZE"
                type="number"
                value={config.BUFFER_BATCH_SIZE || ''}
                onChange={(e) => handleChange('BUFFER_BATCH_SIZE', e.target.value)}
                className="bg-gray-800 border-gray-700 text-white mt-1"
              />
            </div>
            <div>
              <Label htmlFor="BUFFER_WRITE_INTERVAL" className="text-gray-300">
                Write Interval (s)
              </Label>
              <Input
                id="BUFFER_WRITE_INTERVAL"
                type="number"
                step="0.1"
                value={config.BUFFER_WRITE_INTERVAL || ''}
                onChange={(e) => handleChange('BUFFER_WRITE_INTERVAL', e.target.value)}
                className="bg-gray-800 border-gray-700 text-white mt-1"
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
