'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { uploadCSV } from '@/lib/api/tags';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { toast } from 'sonner';
import Papa from 'papaparse';
import { Upload, Download, FileText, ArrowLeft, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import Link from 'next/link';

interface CSVRow {
  PLC_CODE: string;
  MACHINE_CODE: string;
  TAG_ADDRESS: string;
  TAG_NAME: string;
  TAG_DIVISION?: string;
  DATA_TYPE?: string;
  UNIT?: string;
  SCALE?: string;
  ENABLED?: string;
}

// CSV 템플릿 컬럼 정의
const CSV_COLUMNS = [
  { name: 'PLC_CODE', required: true, description: 'PLC 코드', example: 'PLC001' },
  { name: 'MACHINE_CODE', required: true, description: '설비 코드', example: 'MCH001' },
  { name: 'TAG_ADDRESS', required: true, description: '태그 주소', example: 'D100' },
  { name: 'TAG_NAME', required: true, description: '태그 이름', example: 'Temperature_Sensor_01' },
  { name: 'TAG_DIVISION', required: false, description: '태그 구분', example: 'PRODUCTION' },
  { name: 'DATA_TYPE', required: false, description: '데이터 타입', example: 'WORD' },
  { name: 'UNIT', required: false, description: '단위', example: '°C' },
  { name: 'SCALE', required: false, description: '스케일', example: '1.0' },
  { name: 'ENABLED', required: false, description: '활성화 (1=활성, 0=비활성)', example: '1' },
];

// 템플릿 샘플 데이터
const TEMPLATE_SAMPLE_DATA = [
  { PLC_CODE: 'PLC001', MACHINE_CODE: 'MCH001', TAG_ADDRESS: 'D100', TAG_NAME: 'Temperature_Sensor_01', TAG_DIVISION: 'PRODUCTION', DATA_TYPE: 'WORD', UNIT: '°C', SCALE: '0.1', ENABLED: '1' },
  { PLC_CODE: 'PLC001', MACHINE_CODE: 'MCH001', TAG_ADDRESS: 'D101', TAG_NAME: 'Pressure_Sensor_01', TAG_DIVISION: 'PRODUCTION', DATA_TYPE: 'DWORD', UNIT: 'bar', SCALE: '0.01', ENABLED: '1' },
  { PLC_CODE: 'PLC002', MACHINE_CODE: 'MCH002', TAG_ADDRESS: 'W200', TAG_NAME: 'Motor_Status_01', TAG_DIVISION: 'UTILITY', DATA_TYPE: 'BIT', UNIT: '', SCALE: '1', ENABLED: '1' },
];

export default function UploadTagsPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<CSVRow[]>([]);
  const [uploading, setUploading] = useState(false);
  const [parseError, setParseError] = useState<string | null>(null);

  // CSV 템플릿 다운로드
  const downloadTemplate = () => {
    const headers = CSV_COLUMNS.map(col => col.name);
    const sampleRows = TEMPLATE_SAMPLE_DATA.map(row =>
      headers.map(h => (row as any)[h] || '').join(',')
    );

    const csvContent = [
      headers.join(','),
      ...sampleRows
    ].join('\n');

    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'tags_template.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    toast.success('템플릿 파일이 다운로드되었습니다');
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setParseError(null);

    Papa.parse(selectedFile, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        // 필수 컬럼 체크
        const requiredCols = CSV_COLUMNS.filter(c => c.required).map(c => c.name);
        const headers = results.meta.fields || [];
        const missingCols = requiredCols.filter(col => !headers.includes(col));

        if (missingCols.length > 0) {
          setParseError(`필수 컬럼이 누락되었습니다: ${missingCols.join(', ')}`);
          setPreview([]);
          return;
        }

        setPreview(results.data.slice(0, 5) as CSVRow[]);
      },
      error: (error) => {
        setParseError(`파일 파싱 오류: ${error.message}`);
        setPreview([]);
      },
    });
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error('파일을 선택해주세요');
      return;
    }

    if (parseError) {
      toast.error('파일 형식 오류를 먼저 수정해주세요');
      return;
    }

    setUploading(true);
    try {
      const result = await uploadCSV(file);
      toast.success(`${result.success_count}개 태그가 업로드되었습니다`);
      if (result.fail_count > 0) {
        toast.warning(`${result.fail_count}개 태그 업로드 실패`);
      }
      router.push('/tags');
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || 'CSV 업로드 실패';
      toast.error(errorMsg);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/tags">
            <Button variant="outline" size="icon" className="bg-gray-800 border-gray-700 hover:bg-gray-700">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-2">
              <Upload className="h-8 w-8" />
              태그 CSV 업로드
            </h1>
            <p className="text-gray-400 mt-1">CSV 파일을 통해 태그를 일괄 등록합니다</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* CSV 형식 안내 */}
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <FileText className="h-5 w-5" />
              CSV 파일 형식
            </CardTitle>
            <CardDescription className="text-gray-400">
              아래 형식에 맞는 CSV 파일을 업로드해주세요
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* 템플릿 다운로드 버튼 */}
            <Button
              onClick={downloadTemplate}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
            >
              <Download className="h-4 w-4 mr-2" />
              CSV 템플릿 다운로드
            </Button>

            {/* 컬럼 설명 테이블 */}
            <div className="rounded-lg border border-gray-800 overflow-hidden">
              <Table>
                <TableHeader className="bg-gray-800">
                  <TableRow className="hover:bg-gray-800">
                    <TableHead className="text-gray-400">컬럼명</TableHead>
                    <TableHead className="text-gray-400">필수</TableHead>
                    <TableHead className="text-gray-400">설명</TableHead>
                    <TableHead className="text-gray-400">예시</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {CSV_COLUMNS.map((col) => (
                    <TableRow key={col.name} className="border-gray-800 hover:bg-gray-800/50">
                      <TableCell className="font-mono text-cyan-400 text-sm">{col.name}</TableCell>
                      <TableCell>
                        {col.required ? (
                          <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-xs">필수</span>
                        ) : (
                          <span className="px-2 py-1 bg-gray-500/20 text-gray-400 rounded text-xs">선택</span>
                        )}
                      </TableCell>
                      <TableCell className="text-gray-300 text-sm">{col.description}</TableCell>
                      <TableCell className="font-mono text-gray-400 text-sm">{col.example}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            {/* 참고 사항 */}
            <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
              <h4 className="text-yellow-400 font-semibold mb-2">참고 사항</h4>
              <ul className="text-yellow-400/80 text-sm space-y-1">
                <li>• CSV 파일은 UTF-8 또는 UTF-8 BOM 인코딩이어야 합니다</li>
                <li>• 첫 번째 행은 반드시 컬럼 헤더여야 합니다</li>
                <li>• TAG_NAME이 &quot;unknown&quot;인 경우 자동으로 비활성화됩니다</li>
                <li>• DATA_TYPE 미지정시 기본값 WORD가 적용됩니다</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* 파일 업로드 영역 */}
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Upload className="h-5 w-5" />
              파일 업로드
            </CardTitle>
            <CardDescription className="text-gray-400">
              CSV 파일을 선택하면 미리보기가 표시됩니다
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* 파일 선택 */}
            <div className="space-y-2">
              <Label htmlFor="csv-file" className="text-gray-300">CSV 파일 선택</Label>
              <Input
                id="csv-file"
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="bg-gray-800 border-gray-700 text-white file:bg-gray-700 file:text-white file:border-0 file:mr-4"
              />
            </div>

            {/* 파일 선택 상태 */}
            {file && (
              <div className={`p-3 rounded-lg flex items-center gap-2 ${parseError ? 'bg-red-500/10 border border-red-500/20' : 'bg-green-500/10 border border-green-500/20'}`}>
                {parseError ? (
                  <>
                    <AlertCircle className="h-5 w-5 text-red-400" />
                    <span className="text-red-400 text-sm">{parseError}</span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="h-5 w-5 text-green-400" />
                    <span className="text-green-400 text-sm">{file.name} 파일 준비 완료</span>
                  </>
                )}
              </div>
            )}

            {/* 미리보기 테이블 */}
            {preview.length > 0 && (
              <div className="space-y-2">
                <h3 className="text-white font-semibold">미리보기 (처음 5개 행)</h3>
                <div className="rounded-lg border border-gray-800 overflow-x-auto">
                  <Table>
                    <TableHeader className="bg-gray-800">
                      <TableRow className="hover:bg-gray-800">
                        <TableHead className="text-gray-400 text-xs">PLC_CODE</TableHead>
                        <TableHead className="text-gray-400 text-xs">MACHINE_CODE</TableHead>
                        <TableHead className="text-gray-400 text-xs">TAG_ADDRESS</TableHead>
                        <TableHead className="text-gray-400 text-xs">TAG_NAME</TableHead>
                        <TableHead className="text-gray-400 text-xs">DATA_TYPE</TableHead>
                        <TableHead className="text-gray-400 text-xs">ENABLED</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {preview.map((row, index) => (
                        <TableRow key={index} className="border-gray-800 hover:bg-gray-800/50">
                          <TableCell className="text-gray-300 text-sm">{row.PLC_CODE}</TableCell>
                          <TableCell className="text-gray-300 text-sm">{row.MACHINE_CODE}</TableCell>
                          <TableCell className="font-mono text-cyan-400 text-sm">{row.TAG_ADDRESS}</TableCell>
                          <TableCell className="text-white text-sm">{row.TAG_NAME}</TableCell>
                          <TableCell className="text-gray-300 text-sm">{row.DATA_TYPE || 'WORD'}</TableCell>
                          <TableCell className="text-sm">
                            {row.ENABLED === '0' ? (
                              <span className="px-2 py-1 bg-gray-500/20 text-gray-400 rounded text-xs">비활성</span>
                            ) : (
                              <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs">활성</span>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>
            )}

            {/* 버튼 영역 */}
            <div className="flex gap-2 justify-end pt-4">
              <Link href="/tags">
                <Button variant="outline" className="bg-gray-800 border-gray-700 hover:bg-gray-700 text-white">
                  취소
                </Button>
              </Link>
              <Button
                onClick={handleUpload}
                disabled={!file || uploading || !!parseError}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                {uploading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    업로드 중...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    업로드
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
